from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.to_chomsly_normal_form.step1_start_symbol import step1_start_symbol
from cflpy.to_chomsly_normal_form.step2_remove_epsilon import step2_remove_epsilon
from cflpy.to_chomsly_normal_form.step3_remove_unit import step3_remove_unit
from cflpy.to_chomsly_normal_form.step4_decompose_long_productions import step4_decompose_long_productions
from cflpy.to_chomsly_normal_form.step5_remove_terminal_in_2_term_rule import step5_remove_terminal_in_2_term_rule


def to_chomsky_normal_form(
    variables: set[Variable],
    terminals: set[Terminal],
    start_symbol: Variable,
    production_rules: ProductionRules,
) -> tuple[set[Variable], set[Terminal], Variable, ProductionRules]:
    """
    文脈自由文法をチョムスキー標準形に変換

    Args:
        variables: 非終端記号の集合
        terminals: 終端記号の集合
        start_symbol: 開始記号
        productions: 生成規則 {非終端: {[右辺の記号...], ...}}

    Returns:
        tuple: (新しい非終端記号の集合, 新しい終端記号の集合, 新しい開始記号, 新しい生成規則)
    """

    # 仮実装

    # Step 1: 開始記号の処理
    variables, start_symbol, production_rules = step1_start_symbol(variables, start_symbol, production_rules)

    # Step 2: ε-規則の除去
    variables, start_symbol, production_rules = step2_remove_epsilon(variables, start_symbol, production_rules)

    # Step 3: 単位規則の除去
    production_rules = step3_remove_unit(production_rules)

    # Step 4: 長い規則の分解
    production_rules, variables = step4_decompose_long_productions(production_rules, variables, terminals)

    # Step 5: 終端記号の処理
    production_rules, variables = step5_remove_terminal_in_2_term_rule(production_rules, variables, terminals)

    return variables, terminals, start_symbol, production_rules
