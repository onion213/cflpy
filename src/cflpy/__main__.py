import argparse
import pathlib

from cflpy.parser import CFGParser, CFGParserConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Context-Free Language Processor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Check membership command
    check_parser = subparsers.add_parser("check", help="Check if string is in language")
    check_parser.add_argument("file", help="Path to .cfl file", type=pathlib.Path)
    check_parser.add_argument("string", help="String to check")

    # Generate strings command
    gen_parser = subparsers.add_parser("generate", help="Generate strings from grammar")
    gen_parser.add_argument("file", help="Path to .cfl file", type=pathlib.Path)
    gen_parser.add_argument("--max-depth", type=int, default=5, help="Maximum recursion depth for generation")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    # TODO: implement config options
    grammar = CFGParser(cfg=CFGParserConfig()).from_file(args.file)

    if args.command == "check":
        result = grammar.is_member(args.string)
        print(f"String '{args.string}' is {'in' if result else 'not in'} the language")
    elif args.command == "generate":
        strings = grammar.generate_strings(args.max_depth)
        print("Generated strings:")
        for s in strings:
            print(f"- {s}")


if __name__ == "__main__":
    main()
