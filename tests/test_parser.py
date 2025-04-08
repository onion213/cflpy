import pytest

from cflpy.core import ProductionRuleRHS, ProductionRules, Sequence, Terminal, Variable
from cflpy.grammar import CFGrammar
from cflpy.parser import CFGParser, CFGParserConfig


class TestLoadFromString:
    def test_load_from_string(self):
        # Arrange
        content = """
<Root> := <Branch>
<Branch> :=  <Branch><Branch>|<ParentheseOpen><Branch><ParentheseClose>|<ParentheseOpen><ParentheseClose>
<ParentheseOpen> := "("|"{"|"["
<ParentheseClose> := ")"|"}"|"]"
"""
        config = CFGParserConfig()
        parser = CFGParser(cfg=config)

        expected_variables = {
            Variable("Root"),
            Variable("Branch"),
            Variable("ParentheseOpen"),
            Variable("ParentheseClose"),
        }
        expected_terminals = {
            Terminal("("),
            Terminal("{"),
            Terminal("["),
            Terminal(")"),
            Terminal("}"),
            Terminal("]"),
        }
        expected_start_symbol = Variable("Root")
        expected_production_rules = ProductionRules(
            {
                Variable("Root"): ProductionRuleRHS({Sequence([Variable("Branch")])}),
                Variable("Branch"): ProductionRuleRHS(
                    {
                        Sequence([Variable("Branch"), Variable("Branch")]),
                        Sequence(
                            [
                                Variable("ParentheseOpen"),
                                Variable("Branch"),
                                Variable("ParentheseClose"),
                            ]
                        ),
                        Sequence(
                            [
                                Variable("ParentheseOpen"),
                                Variable("ParentheseClose"),
                            ]
                        ),
                    }
                ),
                Variable("ParentheseOpen"): ProductionRuleRHS(
                    {
                        Sequence([Terminal("(")]),
                        Sequence([Terminal("{")]),
                        Sequence([Terminal("[")]),
                    }
                ),
                Variable("ParentheseClose"): ProductionRuleRHS(
                    {
                        Sequence([Terminal(")")]),
                        Sequence([Terminal("}")]),
                        Sequence([Terminal("]")]),
                    }
                ),
            }
        )

        # Act
        grammer = parser.from_string(content=content)

        # Assert
        assert isinstance(grammer, CFGrammar)
        assert grammer.start_symbol == expected_start_symbol
        assert grammer.production_rules == expected_production_rules
        assert grammer.variables == expected_variables
        assert grammer.terminals == expected_terminals

    def test_load_from_string_custom_config(self):
        # Arrange
        content = """
@Root@ -> @Branch@
@Branch@ -> @Branch@ @Branch@ ? @ParentheseOpen@ @Branch@ @ParentheseClose@ ? @ParentheseOpen@ @ParentheseClose@
@ParentheseOpen@ -> #(# ? #{# ? #[#
@ParentheseClose@ -> #)# ? #}# ? #]#
        """
        config = CFGParserConfig(
            transition_symbol="->",
            variable_enclosure=("@", "@"),
            terminal_enclosure=("#", "#"),
            comment_symbol="//",
            rhs_separator="?",
            empty_string_symbol="empty",
        )
        parser = CFGParser(cfg=config)

        expected_variables = {
            Variable("Root"),
            Variable("Branch"),
            Variable("ParentheseOpen"),
            Variable("ParentheseClose"),
        }
        expected_terminals = {
            Terminal("("),
            Terminal("{"),
            Terminal("["),
            Terminal(")"),
            Terminal("}"),
            Terminal("]"),
        }
        expected_start_symbol = Variable("Root")
        expected_production_rules = ProductionRules(
            {
                Variable("Root"): ProductionRuleRHS({Sequence([Variable("Branch")])}),
                Variable("Branch"): ProductionRuleRHS(
                    {
                        Sequence([Variable("Branch"), Variable("Branch")]),
                        Sequence(
                            [
                                Variable("ParentheseOpen"),
                                Variable("Branch"),
                                Variable("ParentheseClose"),
                            ]
                        ),
                        Sequence(
                            [
                                Variable("ParentheseOpen"),
                                Variable("ParentheseClose"),
                            ]
                        ),
                    }
                ),
                Variable("ParentheseOpen"): ProductionRuleRHS(
                    {
                        Sequence([Terminal("(")]),
                        Sequence([Terminal("{")]),
                        Sequence([Terminal("[")]),
                    }
                ),
                Variable("ParentheseClose"): ProductionRuleRHS(
                    {
                        Sequence([Terminal(")")]),
                        Sequence([Terminal("}")]),
                        Sequence([Terminal("]")]),
                    }
                ),
            }
        )

        # Act
        grammer = parser.from_string(content=content)

        # Assert
        assert isinstance(grammer, CFGrammar)
        assert grammer.start_symbol == expected_start_symbol
        assert grammer.production_rules == expected_production_rules
        assert grammer.variables == expected_variables
        assert grammer.terminals == expected_terminals
