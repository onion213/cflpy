from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable


def step4_decompose_long_productions(
    production_rules: ProductionRules,
    variables: set[Variable],
    terminals: set[Terminal],
) -> tuple[ProductionRules, set[Variable]]:
    """長い規則を分解する
    長い規則とは、右辺が3つ以上の記号からなる規則のことを指す。

    Args:
        productions (dict[str, set[list[str]]]): 生成規則 {非終端: [[右辺の記号...], ...]}
        variables (set[str]): 非終端記号の集合
        terminals (set[str]): 終端記号の集合

    Returns:
        dict[str, list[list[str]]]: 新しい生成規則
        set[str]: 新しい非終端記号の集合
    """
    # 変数の接頭辞: 既存の終端・非終端記号と衝突しないようにする
    # 既存の変数名で new_variable_prefix で始まるものがなくなるまで "X" を追加していく
    new_variable_prefix = "X"
    while any(var.startswith(new_variable_prefix) for var in variables):
        new_variable_prefix += "X"
    while any(term.startswith(new_variable_prefix) for term in terminals):
        new_variable_prefix += "X"

    new_production_rules = ProductionRules()
    new_variables = variables.copy()
    counter = 1

    for lhs, rhs_set in production_rules.items():
        for rhs in rhs_set:
            if len(rhs) <= 2:
                if lhs not in new_production_rules.keys():
                    new_production_rules[lhs] = ProductionRuleRHS()
                new_production_rules[lhs].add(rhs)
                continue

            # 長い規則を分解
            current_lhs = lhs
            remaining_rhs = rhs.copy()

            while len(remaining_rhs) > 2:
                new_var = Variable(f"{new_variable_prefix}{counter}")
                counter += 1
                new_variables.add(new_var)
                new_rhs_item = Sequence([remaining_rhs[0], new_var])
                # new_productions.setdefault(current_lhs, []).append(new_rhs)
                if current_lhs not in new_production_rules.keys():
                    new_production_rules[current_lhs] = ProductionRuleRHS()
                new_production_rules[current_lhs].add(new_rhs_item)
                current_lhs = new_var
                remaining_rhs = Sequence(remaining_rhs[1:])

            if current_lhs not in new_production_rules.keys():
                new_production_rules[current_lhs] = ProductionRuleRHS()
            new_production_rules[current_lhs].add(remaining_rhs)

    return new_production_rules, new_variables
