import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step2_remove_epsilon import find_null_definite, remove_null_definite


class TestFindNullable:
    def test_find_nullable(self):
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        D = Variable("D")
        a = Terminal("a")
        b = Terminal("b")
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B]), Sequence([a])}),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([])}),
                B: ProductionRuleRHS({Sequence([C, D])}),
                C: ProductionRuleRHS({Sequence([])}),
                D: ProductionRuleRHS({Sequence([])}),
            }
        )
        expected_null_definite = {B, C, D}

        # Act
        nullable = find_null_definite(production_rules)

        # Assert
        assert nullable == expected_null_definite

    def test_remove_null_definite(self):
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        D = Variable("D")
        a = Terminal("a")
        b = Terminal("b")
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B]), Sequence([a])}),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([])}),
                B: ProductionRuleRHS({Sequence([C, D])}),
                C: ProductionRuleRHS({Sequence([])}),
                D: ProductionRuleRHS({Sequence([])}),
            }
        )
        expected_production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A]), Sequence([a])}),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([])}),
            }
        )
        expected_variables = {S, A}

        # Act
        new_production_rules, new_variables = remove_null_definite(production_rules, {S, A, B, C, D}, S)

        # Assert
        assert new_production_rules == expected_production_rules
        assert new_variables == expected_variables
