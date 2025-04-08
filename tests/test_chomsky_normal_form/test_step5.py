from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step5_remove_terminal_in_2_term_rule import step5_remove_terminal_in_2_term_rule


def test_step5_remove_terminal_in_2_term_rule():
    # Arrange
    S = Variable("S")
    A = Variable("A")
    B = Variable("B")
    a = Terminal("a")
    b = Terminal("b")

    Y1 = Variable("Y1")
    Y2 = Variable("Y2")
    Y3 = Variable("Y3")

    production_rules = ProductionRules(
        {
            S: ProductionRuleRHS({Sequence([A, B]), Sequence([a, B]), Sequence([A, b])}),
            A: ProductionRuleRHS({Sequence([a, B])}),
            B: ProductionRuleRHS({Sequence([b])}),
        }
    )
    variables = {S, A, B}
    terminals = {a, b}

    expected_variables = {S, A, B, Y1, Y2, Y3}

    # Act
    new_production_rules, new_variables = step5_remove_terminal_in_2_term_rule(production_rules, variables, terminals)

    # Assert
    for _, rhs in new_production_rules.items():
        for seq in rhs:
            assert len(seq) == 1 or len(seq) == 2
            if len(seq) == 1:
                assert isinstance(seq[0], Terminal)
            elif len(seq) == 2:
                assert isinstance(seq[0], Variable)
                assert isinstance(seq[1], Variable) or isinstance(seq[1], Terminal)
    assert new_variables == expected_variables
