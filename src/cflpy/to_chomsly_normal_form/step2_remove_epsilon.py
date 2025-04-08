from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable


def find_null_definite(production_rules: ProductionRules) -> set[Variable]:
    """変換の結果 必ず epsilon を生成する変数を見つける

    Args:
        production_rules: 変換対象の生成規則

    Returns:
        set[Variable]: epsilon を生成する変数の集合
    """
    # null_definiteな変数を取り除く
    null_definite = set()
    changed = False
    eps = Sequence([])

    for var, rhs in production_rules.items():
        if rhs == ProductionRuleRHS({eps}):
            null_definite.add(var)
            changed = True

    while changed:
        changed = False
        for var, rhs in production_rules.items():
            if var in null_definite:
                continue
            if all(all(sym in null_definite for sym in seq) for seq in rhs):
                null_definite.add(var)
                changed = True
                break

    return null_definite


def remove_null_definite(
    production_rules: ProductionRules, variables: set[Variable], start_symbol: Variable
) -> tuple[ProductionRules, set[Variable]]:
    """null-definiteな変数を削除した新しい規則を追加

    Args:
        production_rules: 変換対象の生成規則
        variables: 変数の集合
        start_symbol: 開始記号

    Returns:
        ProductionRules: 変換後の生成規則
        set[Variable]: 変換後の変数の集合

    """
    null_definite = find_null_definite(production_rules)

    if not null_definite:
        return production_rules, variables

    if start_symbol in null_definite:
        new_production_rules = ProductionRules({start_symbol: ProductionRuleRHS({Sequence([])})})
        new_variables = {start_symbol}
        return new_production_rules, new_variables

    new_production_rules = production_rules.copy()
    new_variables = variables - null_definite
    for var in null_definite:
        del new_production_rules[var]

    for var in new_variables:
        new_rhs = ProductionRuleRHS()
        for seq in new_production_rules[var]:
            indices = [i for i, sym in enumerate(seq) if sym in null_definite]
            if not indices:
                new_rhs.add(seq)
                continue
            new_seq_list = seq.copy().symbols
            for i in reversed(indices):
                new_seq_list = new_seq_list[:i] + new_seq_list[i + 1 :]
            new_seq = Sequence(new_seq_list)
            new_rhs.add(new_seq)
        new_production_rules[var] = new_rhs

    return new_production_rules, new_variables


def find_nullable(production_rules: ProductionRules) -> set[Variable]:
    """変換の結果 epsilon を生成しうる変数を見つける

    Args:
        production_rules: 変換対象の生成規則

    Returns:
        set[Variable]: epsilon を生成しうる変数の集合
    """
    nullable = set()
    changed = False
    eps = Sequence([])

    # First pass: find variables with direct epsilon productions
    for var, rhs in production_rules.items():
        if any(seq == eps for seq in rhs):
            nullable.add(var)
            changed = True

    # Subsequent passes: find variables that derive all nullable symbols
    while changed:
        changed = False
        for var, rhs in production_rules.items():
            if var in nullable:
                continue
            for seq in rhs:
                if all(sym in nullable for sym in seq):
                    nullable.add(var)
                    changed = True
                    break

    return nullable


def generate_nullable_replaced_sequences(sequence: Sequence, nullable_variable: Variable) -> set[Sequence]:
    """元の生成規則の右辺に出現するnullableな変数について、それをepsilonで置き換えた新しい規則を生成する
    nullable_variableがn個出現する場合、最大で2^n個の新しいSequenceからなる集合を生成する
    ただし、重複とEpsilonは削除される

    Args:
        sequence (Sequence): Symbolの列
        nullable_variable (Variable): nullableな変数

    Returns:
        set[Sequence]: 新しい列の集合
    """
    generated_sequences: set[Sequence] = set()
    # Generate all combinations of nullable variables
    for i in range(1 << len(sequence)):
        new_sequence_symbols = []
        for j, sym in enumerate(sequence):
            if isinstance(sym, Variable) and sym == nullable_variable:
                # Replace with epsilon (empty string)
                if i & (1 << j):
                    continue
            new_sequence_symbols.append(sym)
        new_sequence = Sequence(new_sequence_symbols)
        if new_sequence == Sequence([]):
            continue
        generated_sequences.add(new_sequence)
    return generated_sequences


def replace_nullable(production_rules: ProductionRules, target_nullable: Variable) -> ProductionRules:
    """生成規則の右辺に出現するnullableな変数について、それをepsilonで置き換えた新しい規則を追加

    Args:
        production_rules: 変換対象の生成規則
        target_nullable: nullableな変数

    Returns:
        ProductionRules: 変換後の生成規則
    """
    new_production_rules = production_rules.copy()
    for var, rhs in production_rules.items():
        new_rhs = rhs.copy()
        for seq in rhs:
            if target_nullable not in seq:
                continue
            new_seq_set = generate_nullable_replaced_sequences(seq, target_nullable)
            new_rhs.update(ProductionRuleRHS(new_seq_set))
        new_production_rules[var] = new_rhs
    return new_production_rules


def step2_remove_epsilon(
    variables: set[Variable], start_symbol: Variable, production_rules: ProductionRules
) -> tuple[set[Variable], Variable, ProductionRules]:
    """以下の手順でepsilon ruleを削除する
    1. null-denifiteな変数を見つける
    2. null-denifiteな変数を削除した新しい規則を追加する
    3. nullableな変数を見つける
    4. nullableな変数を削除した新しい規則を追加する
    5. epsilon ruleを削除する

    Args:
        variables: Set of variables in the grammar
        start_symbol: The start symbol
        production_rules: The production rules

    Returns:
        Tuple containing:
        - Updated set of variables
        - Updated start symbol (same as input)
        - Updated production rules without epsilon productions
    """
    production_rules, variables = remove_null_definite(production_rules, variables, start_symbol)

    nullable = find_nullable(production_rules)
    production_rules = production_rules.copy()

    for nullable_variable in nullable:
        production_rules = replace_nullable(production_rules, nullable_variable)

    eps = Sequence([])
    for nullable_variable in nullable:
        if eps in production_rules[nullable_variable]:
            production_rules[nullable_variable].remove(eps)

    if start_symbol in nullable:
        production_rules[start_symbol].add(eps)

    return variables, start_symbol, production_rules
