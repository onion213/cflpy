import pathlib

import pydantic

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable

from .grammar import CFGrammar


class CFGParserConfig(pydantic.BaseModel):
    """CFGParserの設定を定義するクラス

    Attributes:
        transition_symbol (str): 生成規則の変換記号。 default: ":="
        variable_enclosure (tuple[str, str]): 非終端記号を囲む文字列。 default: ("<", ">")
        terminal_enclosure (tuple[str, str]): 終端記号を囲む文字列。 default: ('"', '"')
        comment_symbol (str): コメント行の開始記号。 default: "#"
        rhs_separator (str): 右辺の区切り文字。 default: "|"
    """

    transition_symbol: str = ":="
    variable_enclosure: tuple[str, str] = ("<", ">")
    terminal_enclosure: tuple[str, str] = ('"', '"')
    comment_symbol: str = "#"
    rhs_separator: str = "|"
    empty_string_symbol: str = "eps"

    # # validation: 全ての記号は重複してはいけない -> terminal_enclosure: tuple[str, str] = ('"', '"') は許容したいのでどうするか検討
    # @pydantic.model_validator(mode="after")
    # def validate_non_equality(self):
    #     all_set = set(
    #         self.transition_symbol,
    #         *self.variable_enclosure,
    #         *self.terminal_enclosure,
    #         self.comment_symbol,
    #         self.rhs_separator,
    #     )
    #     if len(all_set) < 7:
    #         raise ValueError(f"Config cannot contain duplicated values in different field. Given: {self}")


class CFGParser:
    def __init__(self, cfg: CFGParserConfig = CFGParserConfig()):
        """
        CFGParserのコンストラクタ

        Args:
            cfg(CFGParserConfig): CFGParserの設定
        """
        if not isinstance(cfg, CFGParserConfig):
            raise TypeError(f"Expected ParserConfig, got {type(cfg)}")
        self._cfg = cfg

    @property
    def cfg(self) -> CFGParserConfig:
        """
        CFGParserの設定を取得する

        Returns:
            CFGParserConfig: CFGParserの設定
        """
        return self._cfg

    def from_file(self, filepath: pathlib.Path) -> CFGrammar:
        """
        .cflファイルから文法を読み込む

        Args:
            filepath(pathlib.Path): 文法定義ファイルのパス

        Returns:
            CFGrammar: 構築された文法オブジェクト
        """
        if not isinstance(filepath, pathlib.Path):
            raise TypeError(f"Expected pathlib.Path, got {type(filepath)}")
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if not filepath.is_file():
            raise IsADirectoryError(f"Expected a file, but got a directory: {filepath}")
        with filepath.open("r") as f:
            content = f.read()
        return self.from_string(content)

    def from_string(self, content: str) -> CFGrammar:
        """
        文字列から文法を読み込む

        Args:
            content(str): 文法定義の文字列

        Returns:
            CFGrammar: 構築された文法オブジェクト
        """
        if not isinstance(content, str):
            raise TypeError(f"Expected str, got {type(content)}")
        if not content:
            raise ValueError("Empty content")

        variables: set[Variable] = set()
        terminals: set[Terminal] = set()
        production_rules = ProductionRules()
        start_symbol = None

        # 行ごとに処理
        for i, line in enumerate(content.split("\n")):
            line = line.strip()
            if not line or line.startswith(self.cfg.comment_symbol):
                # 空行またはコメント行はスキップ
                continue
            if self.cfg.transition_symbol not in line:
                # 生成規則の記号がない行はエラー
                raise ValueError(
                    f"Invalid production rule format. All rules must contain the transition symbol '{self.cfg.transition_symbol}'.\nLine: {i + 1}\nGiven line: {line}"
                )
            if line.count(self.cfg.transition_symbol) > 1:
                # 生成規則の記号が2つ以上ある行はエラー
                raise ValueError(
                    f"Invalid production rule format. Only one transition symbol '{self.cfg.transition_symbol}' is allowed.\nLine: {i + 1}\nGiven line: {line}"
                )

            # 生成規則のパース
            lhs_str, rhs_str = line.split(self.cfg.transition_symbol, 1)
            lhs_str = lhs_str.strip()
            rhs_str = rhs_str.strip()

            lhs = self.parse_variable(lhs_str)
            variables.add(lhs)
            if start_symbol is None:
                start_symbol = lhs

            # 右辺の解析 : 右辺は rhs_separator で区切られた文字列に分割できる
            # 各文字列は variable_enclosure もしくは terminal_enclosure に囲まれた token の列に分割できるか空文字列記号と一致する
            rhs = ProductionRuleRHS()
            for seq_str in rhs_str.split(self.cfg.rhs_separator):
                seq_str = seq_str.strip()

                # 変換先が空文字列の場合
                if seq_str == self.cfg.empty_string_symbol:
                    rhs.add(Sequence([]))
                    continue

                # 変換先が token 列の場合
                # 空文字列記号を含むことはできないないことに注意
                seq = Sequence()
                # token間に空白がないケースを考慮して、enclosure[1]enclosure[0] の列の部分の間にスペースを挿入する
                for c, o in [
                    (self.cfg.variable_enclosure[1], self.cfg.variable_enclosure[0]),
                    (self.cfg.variable_enclosure[1], self.cfg.terminal_enclosure[0]),
                    (self.cfg.terminal_enclosure[1], self.cfg.variable_enclosure[0]),
                    (self.cfg.terminal_enclosure[1], self.cfg.terminal_enclosure[0]),
                ]:
                    seq_str = seq_str.replace(c + o, c + " " + o)
                for token in seq_str.split():
                    token = token.strip()
                    if token.startswith(self.cfg.variable_enclosure[0]):
                        sym = self.parse_variable(token)
                        seq.append(sym)
                        variables.add(sym)
                    elif token.startswith(self.cfg.terminal_enclosure[0]):
                        sym = self.parse_terminal(token)
                        seq.append(sym)
                        terminals.add(sym)
                    else:
                        raise ValueError(
                            f"Invalid token in right-hand side:\n  Line: {i + 1}\n  Given line: {line}\n  Token: {token}"
                        )
                rhs.add(seq)

            # 生成規則に追加
            if lhs not in production_rules.keys():
                production_rules[lhs] = ProductionRuleRHS()
            production_rules[lhs].update(rhs)

        if start_symbol is None:
            raise ValueError("No production rules found. Please check the grammar content.")

        return CFGrammar(variables, terminals, start_symbol, production_rules)

    def parse_variable(self, variable_token: str) -> Variable:
        """
        文字列から非終端記号をパースする
        例: "<S>" -> Variable("S")

        Args:
            variable_token(str): 非終端記号の文字列

        Returns:
            Variable: パースされた非終端記号
        """
        if not isinstance(variable_token, str):
            raise TypeError(f"Expected str, got {type(variable_token)}")
        variable_token = variable_token.strip()
        if not variable_token:
            raise ValueError("Empty variable token")
        if not (
            variable_token.startswith(self.cfg.variable_enclosure[0])
            and variable_token.endswith(self.cfg.variable_enclosure[1])
        ):
            raise ValueError(
                f"Invalid variable token format. Expected form: {self.cfg.variable_enclosure[0]}SYMBOL{self.cfg.variable_enclosure[1]}"
            )
        if variable_token == self.cfg.variable_enclosure[0] + self.cfg.variable_enclosure[1]:
            raise ValueError("Empty variable name")
        variable_name = variable_token[len(self.cfg.variable_enclosure[0]) : -len(self.cfg.variable_enclosure[1])]
        variable = Variable(variable_name)
        return variable

    def parse_terminal(self, terminal_token: str) -> Terminal:
        """
        文字列から終端記号をパースする
        例: '"a"' -> Terminal("a")

        Args:
            terminal_token(str): 終端記号の文字列

        Returns:
            Terminal: パースされた終端記号
        """
        if not isinstance(terminal_token, str):
            raise TypeError(f"Expected str, got {type(terminal_token)}")
        terminal_token = terminal_token.strip()
        if not terminal_token:
            raise ValueError("Empty terminal token")
        if not (
            terminal_token.startswith(self.cfg.terminal_enclosure[0])
            and terminal_token.endswith(self.cfg.terminal_enclosure[1])
        ):
            raise ValueError(
                f"Invalid terminal token format.\nExpected form: {self.cfg.terminal_enclosure[0]}SYMBOL{self.cfg.terminal_enclosure[1]}\nGiven token: {terminal_token}"
            )
        if terminal_token == self.cfg.terminal_enclosure[0] + self.cfg.terminal_enclosure[1]:
            raise ValueError("Empty terminal name")
        terminal_name = terminal_token[len(self.cfg.terminal_enclosure[0]) : -len(self.cfg.terminal_enclosure[1])]
        terminal = Terminal(terminal_name)
        return terminal
