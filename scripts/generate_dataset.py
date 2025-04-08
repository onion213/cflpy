import argparse
import pathlib
import random
import string

import tqdm

from cflpy.parser import CFGParser


def random_string(length: int) -> str:
    """
    Generate a random string of fixed length
    :param length: Length of the string to generate
    :return: Random string
    """
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for i in range(length))


def main(grammar_file: pathlib.Path, output_dir: pathlib.Path, num: int, name: str | None):
    # parse the grammar file
    parser = CFGParser()  # TODO: make configurable
    grammer = parser.from_file(grammar_file)
    print(f"Parsed grammar from {grammar_file}.")

    # generate output directory
    # output_dir must exist, then create a subdirectory with random name
    if not output_dir.exists():
        raise ValueError(f"Output directory {output_dir} does not exist.")
    if not output_dir.is_dir():
        raise ValueError(f"Output path {output_dir} is not a directory.")

    # randomly generate a subdirectory name
    if name is None:
        name = random_string(8)
    subdir = output_dir / name

    # subdir must not exist
    if subdir.exists():
        raise ValueError(f"Subdirectory {subdir} already exists.")
    subdir.mkdir(parents=False, exist_ok=False)
    print(f"Created output directory {subdir}.")

    # generate and save strings
    digit_count = len(str(num))
    for i in tqdm.tqdm(range(num), desc="Generating strings", unit="string"):
        # generate a numbered file name, zero-padded to digit_count

        content = grammer.generate_string()

        filename = f"{i + 1:0{digit_count}}.txt"
        file_path = subdir / filename

        # write the content to the file
        with open(file_path, "w") as f:
            f.write(content)

    print(f"Generated {num} strings and saved them to {subdir}.")


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
        "--output_dir",
        "-o",
        type=pathlib.Path,
        required=True,
        help="Path to the output directory where the generated strings will be saved.",
    )
    parser.add_argument(
        "--num",
        "-n",
        type=int,
        default=1000,
        help="Number of strings to generate.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Name of the subdirectory to save the generated strings.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.grammar_file, args.output_dir, args.num, args.name)
