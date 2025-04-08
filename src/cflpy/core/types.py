import random


class Symbol:
    def __init__(self, name: str):
        self._name = name
        self.is_terminal = False

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"Symbol({self.name})"

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def startswith(self, prefix: str) -> bool:
        return self.name.startswith(prefix)


class Variable(Symbol):
    def __init__(self, name: str):
        super().__init__(name)

    def __repr__(self):
        return f"Variable({self.name})"


class Terminal(Symbol):
    def __init__(self, name: str):
        super().__init__(name)
        self.is_terminal = True

    def __repr__(self):
        return f"Terminal({self.name})"


class Sequence:
    def __init__(self, symbols: list[Symbol] | None = None):
        if symbols is None:
            symbols = []
        elif not isinstance(symbols, list):
            raise TypeError("symbols must be a list of Symbol objects")
        if not all(isinstance(symbol, Symbol) for symbol in symbols):
            raise TypeError("all elements in symbols must be Symbol objects")
        self._symbols = symbols

    def append(self, symbol: Symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self._symbols.append(symbol)

    @property
    def symbols(self):
        return self._symbols

    def copy(self):
        return Sequence(self._symbols.copy())

    def __len__(self):
        return len(self.symbols)

    def __getitem__(self, index) -> Symbol:
        return self.symbols[index]

    def __setitem__(self, index, value: Symbol):
        if not isinstance(value, Symbol):
            raise TypeError("value must be a Symbol object")
        self.symbols[index] = value

    def __repr__(self):
        return f"Sequence({self.symbols})"

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False
        return self.symbols == other.symbols

    def __hash__(self):
        return hash(tuple(self.symbols))


class ProductionRuleRHS:
    def __init__(self, rhs: set[Sequence] | None = None):
        if rhs is None:
            rhs = set()
        self._rhs = rhs

    def add(self, sequence: Sequence):
        if not isinstance(sequence, Sequence):
            raise TypeError("sequence must be a Sequence object")
        self._rhs.add(sequence)

    def remove(self, sequence: Sequence):
        if not isinstance(sequence, Sequence):
            raise TypeError("sequence must be a Sequence object")
        if sequence not in self._rhs:
            raise ValueError("sequence not found in rhs")
        self._rhs.remove(sequence)

    def update(self, other: "ProductionRuleRHS"):
        if not isinstance(other, ProductionRuleRHS):
            raise TypeError("other must be a ProductionRuleRHS object")
        self._rhs.update(other.rhs)

    def get_random(self):
        return random.choice(list(self._rhs))

    def copy(self):
        return ProductionRuleRHS(self._rhs.copy())

    @property
    def rhs(self):
        return self._rhs

    def __iter__(self):
        yield from self.rhs

    def __len__(self):
        return len(self.rhs)

    def __repr__(self):
        return f"ProductionRuleRHS({'|'.join([' '.join(map(str, seq.symbols)) for seq in self.rhs])})"

    def __eq__(self, other):
        if not isinstance(other, ProductionRuleRHS):
            return False
        return self.rhs == other.rhs

    def __hash__(self):
        return hash(self.rhs)


class ProductionRules:
    def __init__(self, production_rules: dict[Variable, ProductionRuleRHS] | None = None):
        if production_rules is None:
            production_rules = {}
        self._production_rules = production_rules

    def keys(self):
        return self._production_rules.keys()

    def values(self):
        return self._production_rules.values()

    def items(self):
        return self._production_rules.items()

    def copy(self):
        return ProductionRules(self._production_rules.copy())

    def __getitem__(self, key: Variable) -> ProductionRuleRHS:
        if not isinstance(key, Variable):
            raise TypeError("key must be a Variable object")
        return self._production_rules[key]

    def __setitem__(self, key: Variable, value: ProductionRuleRHS):
        if not isinstance(key, Variable):
            raise TypeError("key must be a Variable object")
        if not isinstance(value, ProductionRuleRHS):
            raise TypeError("value must be a ProductionRuleRHS object")
        self._production_rules[key] = value

    def __delitem__(self, key: Variable):
        if not isinstance(key, Variable):
            raise TypeError("key must be a Variable object")
        if key not in self._production_rules:
            raise KeyError("key not found in production rules")
        del self._production_rules[key]

    @property
    def production_rules(self):
        return self._production_rules

    def __repr__(self):
        return f"ProductionRules({self.production_rules})"

    def __eq__(self, other):
        if not isinstance(other, ProductionRules):
            return False
        return self.production_rules == other.production_rules

    def __hash__(self):
        return hash(tuple(self.production_rules.items()))
