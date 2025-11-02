import argparse
import fnmatch
import os
from pathlib import Path
from typing import List, Optional

from gitignore_parser import parse_gitignore_str


def create_transformed_file(
    root_dir: Path,
    output_file: Path,
    rules_file_path: Optional[Path] = None,
    custom_ignore_patterns: List[str] = [],
    verbose: bool = False,
) -> None:
    """
    Combines files from the specified directory into one text file,
    ignoring files according to rules and additional patterns.

    Args:
        root_dir (Path): Absolute path to the root directory to traverse.
        output_file (Path): Absolute path to the output file.
        rules_file_path (Path, optional): Path to the rules file for ignoring.
        custom_ignore_patterns (list): List of additional patterns to ignore.
        verbose (bool): Flag for detailed process output.
    """
    matches = lambda x: False
    if rules_file_path and rules_file_path.exists():
        try:
            rules_str = rules_file_path.read_text(encoding="utf-8")
            matches = parse_gitignore_str(rules_str, base_dir=str(root_dir))
            # Note: base_dir ensures relative path matching from root
            if verbose:
                print(f"[*] Using rules file: {rules_file_path}")
        except Exception as e:
            if verbose:
                print(f"[!] Error parsing .gitignore: {e}. Ignoring disabled.")
            matches = lambda x: False
    else:
        if verbose:
            print("[*] .gitignore rules file not used. Ignoring only by arguments.")

    def should_ignore_dir_or_file(path: Path) -> bool:
        rel_path = path.relative_to(root_dir).as_posix()
        # Check custom patterns (filename or full relative path)
        is_custom_ignored = any(
            fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel_path, pattern)
            for pattern in custom_ignore_patterns
        )
        # Check gitignore rules
        is_rule_ignored = matches(str(path))
        return is_custom_ignored or is_rule_ignored

    with output_file.open("w", encoding="utf-8") as outfile:
        for dirpath_str, dirnames, filenames in os.walk(str(root_dir), topdown=True):
            dirpath = Path(dirpath_str)
            
            # Prune ignored directories first (respects both custom and rules)
            dirnames_to_keep = []
            for d in dirnames:
                potential_dir = dirpath / d
                if should_ignore_dir_or_file(potential_dir):
                    if verbose:
                        rel_dir = potential_dir.relative_to(root_dir).as_posix()
                        print(f"[skipped dir - ignore rule] {rel_dir}")
                else:
                    dirnames_to_keep.append(d)
            dirnames[:] = dirnames_to_keep
            
            # Then skip hidden dirs (if not already pruned)
            dirnames_to_keep = []
            for d in dirnames:
                if d.startswith("."):
                    if verbose:
                        rel_dir = (dirpath / d).relative_to(root_dir).as_posix()
                        print(f"[skipped dir - hidden] {rel_dir}")
                else:
                    dirnames_to_keep.append(d)
            dirnames[:] = dirnames_to_keep

            for filename in filenames:
                file_path = dirpath / filename
                relative_path = file_path.relative_to(root_dir).as_posix()

                if file_path == output_file:
                    if verbose:
                        print(f"[skipped - output file] {relative_path}")
                    continue

                if should_ignore_dir_or_file(file_path):
                    if verbose:
                        print(f"[skipped - ignore rule] {relative_path}")
                    continue

                if verbose:
                    print(f"[included] {relative_path}")

                try:
                    with file_path.open("r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(f"----file start {relative_path}----\n")
                        outfile.write(infile.read())
                        outfile.write(f"\n----file end {relative_path}----\n\n")
                except Exception as e:
                    if verbose:
                        print(f"  [reading error] {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Script to combine files into .txt with smart .gitignore search and "
            "user exclusions."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the folder to parse (default: current).",
    )

    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",
        default=[],
        help="Additional patterns to ignore (e.g., -i *.log .env).",
    )

    parser.add_argument(
        "--rules-file",
        help="Explicitly specify path to rules file (e.g., .gitignore). Highest priority.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed process output.",
    )

    args = parser.parse_args()

    root_to_parse = Path(args.directory).resolve()
    output_filename = Path("out.txt").resolve()

    args.ignore.append(Path(__file__).name)

    if not root_to_parse.is_dir():
        print(f"Error: directory '{root_to_parse}' not found.")
    else:
        rules_path_to_use = None
        script_dir = Path(__file__).parent

        if args.rules_file:
            rules_path_to_use = Path(args.rules_file).resolve()
        else:
            target_gitignore = root_to_parse / ".gitignore"
            if target_gitignore.exists():
                rules_path_to_use = target_gitignore
            else:
                script_gitignore = script_dir / ".gitignore"
                if script_gitignore.exists():
                    rules_path_to_use = script_gitignore

        create_transformed_file(
            root_dir=root_to_parse,
            output_file=output_filename,
            rules_file_path=rules_path_to_use,
            custom_ignore_patterns=args.ignore,
            verbose=args.verbose,
        )
        print(f"\nDone! File {output_filename} successfully created.")
