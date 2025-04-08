from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Variable


def find_unit_productions(production_rules: ProductionRules) -> tuple[dict[Variable, set[Variable]], ProductionRules]:
    """単位規則を見つける
    単位規則とは、A -> Bの形を持つ生成規則であり、AとBは非終端記号である。

    Args:
        productions (dict): 生成規則 {非終端: {[右辺の記号...], ...}}

    Returns:
        dict: 単位規則 {非終端: [非終端...]}
        dict: 生成規則 {非終端: {[右辺の記号...], ...}} 単位規則を除去したもの
    """
    # 単位規則を見つける
    # 単位規則を除去した生成規則を作成
    new_production_rules = ProductionRules()
    unit_production_pairs: dict[Variable, set[Variable]] = {}
    for lhs, rhs_set in production_rules.items():
        for rhs in rhs_set:
            if len(rhs) == 1 and isinstance(rhs[0], Variable):  # 単位規則の場合
                if lhs not in unit_production_pairs.keys():
                    unit_production_pairs[lhs] = set()
                unit_production_pairs[lhs].add(rhs[0])
            else:  # 単位規則でない場合: new_production_rulesに追加
                if lhs not in new_production_rules.keys():
                    new_production_rules[lhs] = ProductionRuleRHS()
                new_production_rules[lhs].add(rhs)

    # 連鎖する単位規則について、すべての非終端記号を追加
    changed = True
    while changed:
        changed = False
        for lhs, rhs_set in unit_production_pairs.items():
            to_be_extended: set[Variable] = set()
            for rhs in rhs_set:
                if rhs in unit_production_pairs.keys():
                    to_be_extended.update(unit_production_pairs[rhs])
            original_length = len(unit_production_pairs[lhs])
            unit_production_pairs[lhs].update(to_be_extended)
            if len(unit_production_pairs[lhs]) > original_length:
                changed = True

    return unit_production_pairs, new_production_rules


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
    unit_production_rules, new_production_rules = find_unit_productions(production_rules)

    # 単位規則を除去する
    for lhs, rhs_set in unit_production_rules.items():
        for rhs in rhs_set:
            if rhs in new_production_rules.keys():
                new_production_rules[lhs].update(new_production_rules[rhs])

    return new_production_rules
