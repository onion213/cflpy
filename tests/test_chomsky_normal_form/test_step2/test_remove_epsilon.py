from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step2_remove_epsilon import step2_remove_epsilon


class TestStep2RemoveEpsilon:
    def test_step2_remove_epsilon(self):
        # Arrange
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
        expected_production_rules = ProductionRules(
            {
                S: ProductionRuleRHS(
                    {
                        Sequence([A, B]),
                        Sequence([A, C]),
                        Sequence([A]),
                        Sequence([a]),
                        Sequence([B]),
                        Sequence([C]),
                        Sequence([]),
                    }
                ),
                A: ProductionRuleRHS({Sequence([a, A, b]), Sequence([a, b])}),
                B: ProductionRuleRHS({Sequence([b, B]), Sequence([b])}),
                C: ProductionRuleRHS({Sequence([b, C]), Sequence([b])}),
            }
        )
        expected_start_symbol = S
        expected_variables = {S, A, B, C}

        # Act
        variables, start_symbol, new_production_rules = step2_remove_epsilon({S, A, B, C}, S, production_rules)

        # Assert
        assert variables == expected_variables
        assert start_symbol == expected_start_symbol
        assert new_production_rules == expected_production_rules
