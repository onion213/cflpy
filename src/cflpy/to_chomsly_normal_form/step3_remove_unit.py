from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Variable


def find_unit_pairs(production_rules: ProductionRules) -> dict[Variable, set[Variable]]:
    """単位ペアを見つける
    単位ペアとは、2つの非終端記号のペア(A, B)であり、1つ以上の生成規則を介して A から Bに遷移できるようなものを指す。
    特に、全ての非終端記号 A について (A, A) は単位ペアである。

    Args:
        productions (ProductionRules): 生成規則

    Returns:
        dict[Variable, set[Variable]]: 単位ペア {非終端: [非終端...]}
    """
    unit_production_pairs: dict[Variable, set[Variable]] = {}
    for lhs, rhs in production_rules.items():
        if lhs not in unit_production_pairs.keys():
            unit_production_pairs[lhs] = set()
        for seq in rhs:
            if len(seq) == 1 and isinstance(seq[0], Variable):  # 単位規則の場合
                unit_production_pairs[lhs].add(seq[0])

    # 連鎖する単位規則について、すべての非終端記号を追加
    changed = True
    while changed:
        changed = False
        for lhs, mid_set in unit_production_pairs.items():
            to_be_extended: set[Variable] = set()
            for mid in mid_set:
                if mid in unit_production_pairs.keys():
                    to_be_extended.update(unit_production_pairs[mid])
            original_length = len(unit_production_pairs[lhs])
            unit_production_pairs[lhs].update(to_be_extended)
            if len(unit_production_pairs[lhs]) > original_length:
                changed = True
    return unit_production_pairs


def step3_remove_unit(production_rules: ProductionRules) -> ProductionRules:
    """単位規則を除去する
    単位規則とは、A -> Bの形を持つ生成規則であり、AとBは非終端記号である。
    これは以下の手順で行う。
    1. 単位規則を見つける
    2. 単位規則 A -> Bを見つけたら、Bが生成するすべての規則をAに追加する
    3. A -> Bの規則を削除する
        ただし、単位規則の連鎖を考慮する。
        例えば、A -> B, B -> Cの規則がある場合、Cが生成するすべての規則をAに追加する必要がある。


    Args:
        productions (dict): 生成規則 {非終端: {[右辺の記号...], ...}}

    Returns:
        dict: 単位規則を除去した生成規則 {非終端: {[右辺の記号...], ...}}
    """

    # 単位規則を見つける
    unit_production_rules = find_unit_pairs(production_rules)

    # 単位規則を介した変換規則を追加する
    new_production_rules = production_rules.copy()
    for lhs, mid_set in unit_production_rules.items():
        for mid in mid_set:
            if mid in production_rules.keys():
                for seq in production_rules[mid]:
                    new_production_rules[lhs].add(seq)

    # 単位規則を削除する
    for lhs, rhs in new_production_rules.items():
        new_production_rules[lhs] = ProductionRuleRHS(
            {seq for seq in rhs if len(seq) != 1 or not isinstance(seq[0], Variable)}
        )
    return new_production_rules
