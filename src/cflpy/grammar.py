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

    def is_member_seq(self, sequence: Sequence) -> bool:
        """
        CYKアルゴリズムで文字列が言語に含まれるか判定

        Args:
            sequence: 判定対象の文字列

        Returns:
            bool: 言語に含まれるかどうか
        """
        # sequence の要素がすべて終端記号であることを確認
        if not all(isinstance(symbol, Terminal) for symbol in sequence):
            raise ValueError("All symbols in the sequence must be terminals.")

        n = len(sequence)
        if n == 0:
            return False

        r = len(self.variables)

        cyk_slice = {v: False for v in self.variables}
        cyk_col = [cyk_slice.copy() for _ in range(n)]
        cyk_table = [cyk_col.copy() for _ in range(n)]

        # Initialize the table with terminal symbols production rules
        for i in range(n):
            for lhs, rhs_set in self.production_rules.items():
                cyk_table[i][i][lhs] = Sequence([sequence[i]]) in rhs_set

        for length in range(2, n + 1):  # 部分列の長さ
            for i in range(n - length + 1):
                j = i + length - 1  # 部分列 tokens[i]～tokens[j]
                # 部分列を2つに分割するすべての位置 k (i ≤ k < j) について検討
                for k in range(i, j):
                    for lhs, rhs_set in self.production_rules.items():
                        for rhs in rhs_set:
                            if len(rhs) == 1:
                                continue
                            if cyk_table[i][k][rhs[0]] and cyk_table[k + 1][j][rhs[1]]:
                                cyk_table[i][j][lhs] = True

        # 開始記号が生成するかどうかを確認
        return cyk_table[0][n - 1][self.start_symbol]

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
