import argparse
import pathlib

import tqdm

from cflpy.parser import CFGParser


def main(grammar_file: pathlib.Path, num: int, max_depth: int):
    # parse the grammar file
    parser = CFGParser()  # TODO: make configurable
    grammer = parser.from_file(grammar_file)

    # In some cases, onverting to Chomsky Normal Form makes the expected length of
    # the generated string smaller
    # grammer = grammer.to_chomsky_normal_form()

    print(f"Parsed grammar from {grammar_file}.")

    for i in tqdm.tqdm(range(num), desc="Generating strings", unit="string"):
        content = grammer.generate_string(max_depth=max_depth)
        tqdm.tqdm.write(content)

    print(f"Generated {num} strings and printed them to the console.")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a dataset of strings from a context-free grammar.")
    parser.add_argument(
        "--grammar_file",
        "-g",
        type=pathlib.Path,
        required=True,
        help="Path to the file containing the context-free grammar.",
    )
    parser.add_argument(
        "--num",
        "-n",
        type=int,
        default=1000,
        help="Number of strings to generate.",
    )
    parser.add_argument(
        "--max_depth",
        "-d",
        type=int,
        default=-1,
        help="Maximum depth of recursion for string generation.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.grammar_file, args.num, args.max_depth)
