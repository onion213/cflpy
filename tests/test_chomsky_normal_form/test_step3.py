import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step3_remove_unit import find_unit_productions, step3_remove_unit


class TestFindUnitProductions:
    @pytest.mark.parametrize(
        "production_rules, expected_unit_production_pairs, expected_new_production_rules",
        [
            (
                ProductionRules(
                    {
                        Variable("S"): ProductionRuleRHS(
                            {
                                Sequence([Variable("A"), Variable("B")]),
                                Sequence([Terminal("a")]),
                                Sequence([Variable("A")]),
                            }
                        ),
                        Variable("A"): ProductionRuleRHS({Sequence([Variable("B")]), Sequence([Terminal("a")])}),
                        Variable("B"): ProductionRuleRHS(
                            {Sequence([Terminal("b"), Variable("B")]), Sequence([Terminal("b")])}
                        ),
                    }
                ),
                {
                    Variable("S"): {Variable("B"), Variable("A")},
                    Variable("A"): {Variable("B")},
                },
                ProductionRules(
                    {
                        Variable("S"): ProductionRuleRHS(
                            {Sequence([Variable("A"), Variable("B")]), Sequence([Variable("a")])}
                        ),
                        Variable("A"): ProductionRuleRHS({Sequence([Variable("a")])}),
                        Variable("B"): ProductionRuleRHS(
                            {Sequence([Variable("b"), Variable("B")]), Sequence([Variable("b")])}
                        ),
                    }
                ),
            ),
        ],
    )
    def test_find_unit_productions(
        self, production_rules, expected_unit_production_pairs, expected_new_production_rules
    ):
        # Arrange

        # Act
        unit_production_pairs, new_production_rules = find_unit_productions(production_rules)

        # Assert
        assert unit_production_pairs == expected_unit_production_pairs
        assert new_production_rules == expected_new_production_rules

    @pytest.mark.parametrize(
        "production_rules, expected_new_production_rules",
        [
            (
                ProductionRules(
                    {
                        Variable("S"): ProductionRuleRHS(
                            {
                                Sequence([Variable("A"), Variable("B")]),
                                Sequence([Terminal("a")]),
                                Sequence([Variable("A")]),
                            }
                        ),
                        Variable("A"): ProductionRuleRHS(
                            {
                                Sequence([Variable("B")]),
                                Sequence([Terminal("a")]),
                            }
                        ),
                        Variable("B"): ProductionRuleRHS(
                            {
                                Sequence([Terminal("b"), Variable("B")]),
                                Sequence([Terminal("b")]),
                            }
                        ),
                    }
                ),
                ProductionRules(
                    {
                        Variable("S"): ProductionRuleRHS(
                            {
                                Sequence([Variable("A"), Variable("B")]),
                                Sequence([Variable("a")]),
                                Sequence([Variable("b"), Variable("B")]),
                                Sequence([Variable("b")]),
                            }
                        ),
                        Variable("A"): ProductionRuleRHS(
                            {
                                Sequence([Variable("a")]),
                                Sequence([Variable("b"), Variable("B")]),
                                Sequence([Variable("b")]),
                            }
                        ),
                        Variable("B"): ProductionRuleRHS(
                            {
                                Sequence([Variable("b"), Variable("B")]),
                                Sequence([Variable("b")]),
                            }
                        ),
                    }
                ),
            ),
        ],
    )
    def test_step3_remove_unit(self, production_rules, expected_new_production_rules):
        # Arrange

        # Act
        new_production_rules = step3_remove_unit(production_rules)

        # Assert
        assert new_production_rules == expected_new_production_rules
