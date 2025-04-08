from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Variable


def step1_start_symbol(
    variables: set[Variable], start_symbol: Variable, production_rules: ProductionRules
) -> tuple[set[Variable], Variable, ProductionRules]:
    """チョムスキー標準形の変換ステップ1: 開始記号の処理
    開始記号が右辺に現れる場合、新しい非終端記号を追加し、開始記号を変更する。

    Args:
        variables: 非終端記号の集合
        start_symbol: 開始記号
        production_rules: 生成規則の辞書

    Returns:
        new_variables: 新しい非終端記号の集合
        new_start_symbol: 新しい開始記号
        new_production_rules: 新しい生成規則の辞書
    """
    new_production_rules = production_rules.copy()
    new_variables = variables.copy()

    if any(start_symbol in seq for rhs in production_rules.values() for seq in rhs):
        new_start_symbol = Variable(f"{start_symbol}'")
        while new_start_symbol in variables:
            new_start_symbol = Variable(f"{new_start_symbol.name}'")
        new_variables.add(new_start_symbol)
        new_production_rules[new_start_symbol] = ProductionRuleRHS({Sequence([start_symbol])})
    else:
        new_start_symbol = start_symbol

    return new_variables, new_start_symbol, new_production_rules
