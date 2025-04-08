from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable


def step5_remove_terminal_in_2_term_rule(
    production_rules: ProductionRules, variables: set[Variable], terminals: set[Terminal]
) -> tuple[ProductionRules, set[Variable]]:
    """終端記号を含む2項規則を除去する
    2項規則とは、右辺が2つの記号からなる規則のことを指す。
    A := aBの形を持つ規則を A := Y1B, Y1 := aの形に変換する。

    Args:
        production_rules(ProductionRules): 変換対象の生成規則
        variables(set[Variable]): 変数の集合
        terminals(set[Terminal]): 終端記号の集合

    Returns:
        ProductionRules: 新しい生成規則
        set[Variable]: 新しい非終端記号の集合
    """
    # 変数の接頭辞: 既存の終端・非終端記号と衝突しないようにする
    # 既存の変数名で new_variable_prefix で始まるものがなくなるまで "Y" を追加していく
    new_variable_prefix = "Y"
    while any(var.startswith(new_variable_prefix) for var in variables):
        new_variable_prefix += "Y"
    while any(term.startswith(new_variable_prefix) for term in terminals):
        new_variable_prefix += "Y"

    new_production_rules = ProductionRules()
    new_variables = variables.copy()
    counter = 1

    for lhs, rhs in production_rules.items():
        for seq in rhs:
            if lhs not in new_production_rules.keys():
                new_production_rules[lhs] = ProductionRuleRHS()
            if len(seq) < 2:
                new_production_rules[lhs].add(seq)
                continue

            # 終端記号を含む2項規則を除去
            new_seq = seq.copy()
            for i, sym in enumerate(seq):
                if isinstance(sym, Terminal):
                    new_var = Variable(f"{new_variable_prefix}{counter}")
                    counter += 1
                    new_variables.add(new_var)
                    new_seq[i] = new_var
                    new_production_rules[new_var] = ProductionRuleRHS({Sequence([sym])})
            new_production_rules[lhs].add(new_seq)
    return new_production_rules, new_variables
