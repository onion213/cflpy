from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step1_start_symbol import step1_start_symbol


class TestStep1StartSymbol:
    def test_step1_start_symbol_add(self):
        # Arrange
        variables = {Variable("S"), Variable("S'")}
        start_symbol = Variable("S")
        production_rules = ProductionRules(
            {
                Variable("S"): ProductionRuleRHS(
                    {Sequence([Variable("S")]), Sequence([Terminal("S'")]), Sequence([Terminal("s")])}
                ),
            }
        )

        # Act
        new_variables, new_start_symbol, new_production_rules = step1_start_symbol(
            variables, start_symbol, production_rules
        )

        # Assert
        assert new_variables == {Variable("S"), Variable("S'"), Variable("S''")}
        assert new_start_symbol == Variable("S''")
        assert new_production_rules == ProductionRules(
            {
                Variable("S"): ProductionRuleRHS(
                    {Sequence([Variable("S")]), Sequence([Terminal("S'")]), Sequence([Terminal("s")])}
                ),
                Variable("S''"): ProductionRuleRHS({Sequence([Variable("S")])}),
            }
        )

    def test_step1_start_symbol_no_change(self):
        # Arrange
        variables = {Variable("S")}
        start_symbol = Variable("S")
        production_rules = ProductionRules(
            {
                Variable("S"): ProductionRuleRHS(
                    {Sequence([Terminal("a")]), Sequence([Terminal("b")]), Sequence([Terminal("c")])}
                ),
            }
        )

        # Act
        new_variables, new_start_symbol, new_production_rules = step1_start_symbol(
            variables, start_symbol, production_rules
        )

        # Assert
        assert new_variables == {Variable("S")}
        assert new_start_symbol == Variable("S")
        assert new_production_rules == ProductionRules(
            {
                Variable("S"): ProductionRuleRHS(
                    {Sequence([Terminal("a")]), Sequence([Terminal("b")]), Sequence([Terminal("c")])}
                ),
            }
        )
