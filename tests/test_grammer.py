import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.grammar import CFGrammar, ChomskyNormalFormGrammar


class TestCFGrammar:
    def test_initialization(self):
        """基本的な初期化テスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        variables = {S, A}
        a = Terminal("a")
        terminals = {a}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A])}),
                A: ProductionRuleRHS({Sequence([a])}),
            }
        )

        # Act
        grammar = CFGrammar(variables, terminals, S, production_rules)

        # Assert
        assert grammar.variables == variables
        assert grammar.terminals == terminals
        assert grammar.start_symbol == S
        assert grammar.production_rules == production_rules

    def test_generate_string(self):
        """文字列生成機能のテスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        variables = {S, A}
        a = Terminal("a")
        terminals = {a}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A])}),
                A: ProductionRuleRHS({Sequence([a])}),
            }
        )
        grammar = CFGrammar(variables, terminals, S, production_rules)

        # Act
        result = grammar.generate_string()

        # Assert
        assert result == "a"

    def test_to_chomsky_normal_form(self):
        """チョムスキー標準形への変換テスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        variables = {S, A, B}
        a = Terminal("a")
        b = Terminal("b")
        terminals = {a, b}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B])}),
                A: ProductionRuleRHS({Sequence([a])}),
                B: ProductionRuleRHS({Sequence([b])}),
            }
        )
        grammar = CFGrammar(variables, terminals, S, production_rules)

        # Act
        cnf_grammar = grammar.to_chomsky_normal_form()

        # Assert
        assert isinstance(cnf_grammar, ChomskyNormalFormGrammar)
        assert cnf_grammar.start_symbol == S
        assert all(len(rhs) <= 2 for rhs_set in cnf_grammar.production_rules.values() for rhs in rhs_set)

    def test_repr(self):
        """文字列表現のテスト"""
        # Arrange
        S = Variable("S")
        variables = {S}
        a = Terminal("a")
        terminals = {a}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([a])}),
            }
        )
        grammar = CFGrammar(variables, terminals, S, production_rules)

        # Act
        result = repr(grammar)

        # Assert
        assert "CFGrammar" in result
        assert "S" in result
        assert "a" in result


class TestChomskyNormalFormGrammar:
    def test_validation(self):
        """チョムスキー標準形のバリデーションテスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        variables = {S, A}
        a = Terminal("a")
        terminals = {a}
        valid_production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, A])}),
                A: ProductionRuleRHS({Sequence([a])}),
            }
        )
        invalid_production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, A, A])}),  # 3つの記号はNG
            }
        )

        # Act & Assert (valid case)
        ChomskyNormalFormGrammar(variables, terminals, S, valid_production_rules)

        # Act & Assert (invalid case)
        with pytest.raises(ValueError):
            ChomskyNormalFormGrammar(variables, terminals, S, invalid_production_rules)

    def test_is_member_seq(self):
        """CYKアルゴリズムによるメンバーシップ判定テスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        variables = {S, A, B}
        a = Terminal("a")
        b = Terminal("b")
        terminals = {a, b}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B])}),
                A: ProductionRuleRHS({Sequence([a])}),
                B: ProductionRuleRHS({Sequence([b])}),
            }
        )
        grammar = ChomskyNormalFormGrammar(variables, terminals, S, production_rules)

        # Act & Assert
        assert grammar.is_member_seq(Sequence([a, b])) is True
        assert grammar.is_member_seq(Sequence([a])) is False
        assert grammar.is_member_seq(Sequence([b, a])) is False

    def test_is_member(self):
        """CYKアルゴリズムによるメンバーシップ判定テスト"""
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        variables = {S, A, B}
        a = Terminal("a")
        b = Terminal("b")
        terminals = {a, b}
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B])}),
                A: ProductionRuleRHS({Sequence([a])}),
                B: ProductionRuleRHS({Sequence([b])}),
            }
        )
        grammar = ChomskyNormalFormGrammar(variables, terminals, S, production_rules)

        # Act & Assert
        assert grammar.is_member("a b") is True
        assert grammar.is_member("a") is False
        assert grammar.is_member("b a") is False
