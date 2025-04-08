import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step4_decompose_long_productions import step4_decompose_long_productions


class TestStep4DecomposeLongProductions:
    def test_step4_decompose_long_productions(self):
        # Arrange
        S = Variable("S")
        A = Variable("A")
        B = Variable("B")
        C = Variable("C")
        a = Terminal("a")
        b = Terminal("b")
        c = Terminal("c")
        production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, B, C])}),
                A: ProductionRuleRHS({Sequence([a])}),
                B: ProductionRuleRHS({Sequence([b])}),
                C: ProductionRuleRHS({Sequence([c])}),
            }
        )
        production_rules = {
            S: [Sequence([A, B, C])],
            A: [Sequence([a])],
            B: [Sequence([b])],
            C: [Sequence([c])],
        }
        variables = {S, A, B, C}
        terminals = {a, b, c}
        expected_production_rules = ProductionRules(
            {
                S: ProductionRuleRHS({Sequence([A, Variable("X1")])}),
                A: ProductionRuleRHS({Sequence([a])}),
                Variable("X1"): ProductionRuleRHS({Sequence([B, C])}),
                B: ProductionRuleRHS({Sequence([b])}),
                C: ProductionRuleRHS({Sequence([c])}),
            }
        )
        expected_variables = {S, A, B, C, Variable("X1")}

        # Act
        new_production_rules, new_variables = step4_decompose_long_productions(production_rules, variables, terminals)

        # Assert
        assert new_production_rules == expected_production_rules
        assert new_variables == expected_variables
