import random

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form import to_chomsky_normal_form


class CFGrammar:
    def __init__(
        self,
        variables: set[Variable],
        terminals: set[Terminal],
        start_symbol: Variable,
        production_rules: ProductionRules,
    ):
        """
        文脈自由文法を表現するクラス

        Args:
            variables: 非終端記号の集合
            terminals: 終端記号の集合
            start_symbol: 開始記号
            production_rules: 生成規則の辞書 {非終端: [右辺の記号...]}
        """
        self.variables = variables
        self.terminals = terminals
        self.start_symbol = start_symbol
        self.production_rules = production_rules

    def __repr__(self):
        return f"{self.__class__.__name__}(\n  variables={self.variables},\n  terminals={self.terminals},\n  start_symbol={self.start_symbol},\n  production_rules={self.production_rules}\n)"

    def to_chomsky_normal_form(self) -> "ChomskyNormalFormGrammar":
        """
        文法をチョムスキー標準形に変換
        """
        print("Converting grammar to Chomsky Normal Form...")
        grammer = ChomskyNormalFormGrammar(
            *to_chomsky_normal_form(self.variables, self.terminals, self.start_symbol, self.production_rules)
        )
        print("Conversion complete.")
        return grammer

    def is_member(self, sequence: Sequence) -> bool:
        """
        文字列が文法に含まれるか判定

        Args:
            sequence: 判定対象の文字列

        Returns:
            bool: 文法に含まれるかどうか
        """
        raise NotImplementedError(
            "is_member method is not implemented for this grammar. Use ChomskyNormalFormGrammar instead."
        )

    def generate(self) -> Sequence:
        """
        文法から文字列を生成

        Args:
            max_depth: 再帰の最大深さ

        Returns:
            Sequence: 生成された文字列
        """
        sequence = Sequence([self.start_symbol])
        while any(isinstance(symbol, Variable) for symbol in sequence):
            for i, symbol in enumerate(sequence):
                if isinstance(symbol, Variable):
                    # 生成規則をランダムに選択
                    production_rule_rhs = self.production_rules[symbol]
                    new_symbols = production_rule_rhs.get_random()
                    # sequence = sequence[:i] + new_symbols + sequence[i + 1:]
                    sequence = Sequence(sequence.symbols[:i] + new_symbols.symbols + sequence.symbols[i + 1 :])
                    break

        return sequence

    def generate_string(self) -> str:
        """
        文法から文字列を生成

        Returns:
            str: 生成された文字列
        """
        sequence = self.generate()
        return " ".join(str(symbol) for symbol in sequence)

    def generate_strings(self, num: int) -> list[str]:
        """
        文法から文字列を生成

        Args:
            num: 生成する文字列の数

        Returns:
            list[str]: 生成された文字列のリスト
        """
        if num <= 0:
            raise ValueError("num must be greater than 0")
        return [self.generate_string() for _ in range(num)]


class ChomskyNormalFormGrammar(CFGrammar):
    def __init__(
        self,
        variables: set[Variable],
        terminals: set[Terminal],
        start_symbol: Variable,
        production_rules: ProductionRules,
    ):
        """
        チョムスキー標準形の文法を表現するクラス

        Args:
            variables: 非終端記号の集合
            terminals: 終端記号の集合
            start_symbol: 開始記号
            production_rules: 生成規則の辞書 {非終端: [右辺の記号...]}
        """
        self.validate_chomsky_normal_form(variables, production_rules)
        super().__init__(variables, terminals, start_symbol, production_rules)

    def validate_chomsky_normal_form(self, variables: set[Variable], production_rules: ProductionRules) -> None:
        """
        チョムスキー標準形の文法かどうかを検証

        Args:
            variables: 非終端記号の集合
            production_rules: 生成規則の辞書 {非終端: [右辺の記号...]}

        Raises:
            ValueError: チョムスキー標準形でない場合
        """
        for lhs, rhs_set in production_rules.items():
            for rhs in rhs_set:
                if len(rhs) > 2:
                    raise ValueError(f"Production rule {lhs} -> {rhs} is not in Chomsky Normal Form: Too long.")
                if len(rhs) == 2 and any(isinstance(symbol, Terminal) for symbol in rhs):
                    raise ValueError(
                        f"Production rule {lhs} -> {rhs} is not in Chomsky Normal Form: 2 terms rule with terminals."
                    )
                if len(rhs) == 1 and isinstance(rhs[0], Variable):
                    raise ValueError(f"Production rule {lhs} -> {rhs} is not in Chomsky Normal Form: Unit production.")
        return

    def get_cyk_table(self, sequence: Sequence) -> list[list[dict[Variable, bool]]]:
        """
        CYKアルゴリズムのテーブルを生成

        Args:
            sequence: 判定対象の文字列

        Returns:
            list[list[dict[Variable, bool]]]: CYKテーブル
        """
        if not all(isinstance(symbol, Terminal) for symbol in sequence):
            raise ValueError("All symbols in the sequence must be terminals.")

        n = len(sequence)
        r = len(self.variables)

        cyk_table = [[{v: False for v in self.variables} for _ in range(n)] for _ in range(n)]

        # Initialize the table with terminal symbols production rules
        for i in range(n):
            for lhs, rhs in self.production_rules.items():
                cyk_table[i][i][lhs] = Sequence([sequence[i]]) in rhs

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    for lhs, rhs in self.production_rules.items():
                        for seq in rhs:
                            if len(seq) == 1:
                                continue
                            if cyk_table[i][k][seq[0]] and cyk_table[k + 1][j][seq[1]]:
                                cyk_table[i][j][lhs] = True
                                break
                        if cyk_table[i][j][lhs] is True:
                            break
                    if cyk_table[i][j][lhs] is True:
                        break
        return cyk_table

    def is_member_seq(self, sequence: Sequence) -> bool:
        """
        CYKアルゴリズムで文字列が言語に含まれるか判定

        Args:
            sequence: 判定対象の文字列

        Returns:
            bool: 言語に含まれるかどうか
        """
        # cyk_tableを生成
        cyk_table = self.get_cyk_table(sequence)

        # 開始記号が生成するかどうかを確認
        return cyk_table[0][-1][self.start_symbol]

    def is_member(self, string: str) -> bool:
        """
        文字列が文法に含まれるか判定

        Args:
            string: 判定対象の文字列

        Returns:
            bool: 文法に含まれるかどうか
        """
        if not isinstance(string, str):
            raise ValueError("Input must be a string.")
        sequence = Sequence([Terminal(symbol) for symbol in string.split()])
        for t in sequence:
            if t not in self.terminals:
                raise ValueError(f"Terminal {t} is not in the grammar's terminals.\n Given: {string}")
        return self.is_member_seq(sequence)

    def get_generation_history(self, seq: Sequence) -> dict:
        """
        CYKアルゴリズムを用いてある文字列の生成履歴を取得

        例えば，
        S -> A B
        A -> a
        B -> C D
        C -> c
        D -> d
        と生成される文字列 a c d の生成履歴は以下のようになる．
        {
            Variable("S"): {
                Variable("A"): Terminal("a"),
                Variable("B"): {
                    Variable("C"): Terminal("c"),
                    Variable("D"): Terminal("d")
                }
            }
        }

        Args:
            seq (Sequence): 生成履歴を取得する文字列を表すSequenceオブジェクト

        Returns:
            dict: 生成履歴を表す辞書
        """
        cyk_table = self.get_cyk_table(seq)
        n = len(seq)

        if n == 0:
            raise ValueError("Empty sequence")

        # 開始記号が生成できない場合はNoneを返す
        if not cyk_table[0][n - 1][self.start_symbol]:
            return None

        # バックトラッキングにより解析木を再構築する
        return self._build_parse_tree(cyk_table, 0, n - 1, self.start_symbol, seq)

    def _build_parse_tree(
        self, cyk_table: list[list[dict[Variable, bool]]], start: int, end: int, variable: Variable, seq: Sequence
    ) -> dict:
        """
        CYKテーブルから解析木を再構築する

        Args:
            cyk_table: CYKテーブル
            start: 部分文字列の開始位置
            end: 部分文字列の終了位置
            variable: 非終端記号
            seq: 元の文字列

        Returns:
            dict: 解析木を表す辞書
        """
        # 長さ1の場合は終端記号に対応
        if start == end:
            for rhs in self.production_rules[variable]:
                if len(rhs) == 1 and rhs[0] == seq[start]:
                    return seq[start]

        # 長さ2以上の場合は分割点を探す
        for k in range(start, end):
            for rhs in self.production_rules[variable]:
                if len(rhs) != 2:
                    continue

                left_var, right_var = rhs[0], rhs[1]

                if (
                    isinstance(left_var, Variable)
                    and isinstance(right_var, Variable)
                    and cyk_table[start][k][left_var]
                    and cyk_table[k + 1][end][right_var]
                ):
                    left_tree = self._build_parse_tree(cyk_table, start, k, left_var, seq)
                    right_tree = self._build_parse_tree(cyk_table, k + 1, end, right_var, seq)

                    return {variable: {left_var: left_tree, right_var: right_tree}}

        # ここに到達するのは理論上はあり得ない（CYKテーブルが正しければ）
        raise ValueError(f"Could not reconstruct parse tree for {variable} from {start} to {end}")
