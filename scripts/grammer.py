from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.grammar import CFGrammar

# Example usage
S = Variable("S")
A = Variable("A")
B = Variable("B")
C = Variable("C")
variables = {S, A, B, C}

a = Terminal("a")
b = Terminal("b")
c = Terminal("c")
terminals = {a, b, c}

start_symbol = S
production_rules = ProductionRules(
    {
        S: ProductionRuleRHS({Sequence([A, B, C])}),
        A: ProductionRuleRHS({Sequence([a, B])}),
        B: ProductionRuleRHS({Sequence([b, C])}),
        C: ProductionRuleRHS({Sequence([c])}),
    }
)

grammar = CFGrammar(variables, terminals, start_symbol, production_rules)
cnf_grammar = grammar.to_chomsky_normal_form()

print("Chomsky Normal Form Grammar:")
print(cnf_grammar)

# try is_member
sequence = Sequence([a, b, c, b, c, c])  # valid
print(f"Is the sequence {sequence} a member of the language? {cnf_grammar.is_member(sequence)}")
sequence = Sequence([a, b, c])  # invalid
print(f"Is the sequence {sequence} a member of the language? {cnf_grammar.is_member(sequence)}")
sequence = Sequence([a, b])  # invalid
print(f"Is the sequence {sequence} a member of the language? {cnf_grammar.is_member(sequence)}")
sequence = Sequence([a, b, c, a])  # invalid
print(f"Is the sequence {sequence} a member of the language? {cnf_grammar.is_member(sequence)}")

# Generate a string from the grammar
generated_string = grammar.generate_string()
print(f"Generated string: {generated_string}")
