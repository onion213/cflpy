import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step2_remove_epsilon import find_nullable, step2_remove_epsilon


class TestFindNullable:
    def test_find_nullable(self):
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        a = Terminal("a")
        b = Terminal("b")
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B]), Sequence([a])}),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([])}),
                B: ProductionRuleRHS({Sequence([b, B]), Sequence([b])}),
            }
        )
        expected_nullable = {A}

        # Act
        nullable = find_nullable(production_rules)

        # Assert
        assert nullable == expected_nullable

    def test_find_nullable_with_2_term_rule(self):
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        a = Terminal("a")
        b = Terminal("b")
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B]), Sequence([A, C]), Sequence([a])}),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([])}),
                B: ProductionRuleRHS({Sequence([b, B]), Sequence([b])}),
                C: ProductionRuleRHS({Sequence([b, C]), Sequence([])}),
            }
        )
        expected_nullable = {S, A, C}

        # Act
        nullable = find_nullable(production_rules)

        # Assert
        assert nullable == expected_nullable
