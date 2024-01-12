#!/usr/bin/env python3
# Copyright 2020-2024 Giacomo Ferretti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import logging
import pathlib
import sys
from typing import List

import paranoid_deobfuscator as deobfuscator

REMOVED_COMMENT = (
    "    # Removed with https://github.com/giacomoferretti/paranoid-deobfuscator\n"
)
INSTRUCTION_BUFFER = 20


def search_candidates(target: pathlib.Path):
    candidates = []

    for x in target.rglob("*"):
        if x.is_file() and x.suffix == ".smali":
            with open(x) as f:
                chunks = deobfuscator.extract_obfuscated_strings(f.read())
                if len(chunks) > 0:
                    candidates.append((x, chunks))

    return candidates


def search_deobfuscator(
    target: pathlib.Path, candidate: pathlib.Path, is_apktool: bool
):
    with open(candidate) as f:
        method = deobfuscator.extract_deobfuscator_method(f.read())

        if method:
            clazz = candidate.relative_to(target)
            if is_apktool:
                clazz = clazz.relative_to(*clazz.parts[:1])

            return f"L{'/'.join(clazz.with_suffix('').parts)};->{method}"

    return None


def decode_unicode(chunks: List[str]):
    return [x.encode().decode("unicode-escape") for x in chunks]


def main(args):
    logger = logging.getLogger(__name__)

    # TODO: Alternative for intellisense?
    target: pathlib.Path = args.target
    keep_calls: bool = args.keep_calls

    # Check if target is directory
    if not target.is_dir():
        logger.error("Target must be a directory containing .smali files.")
        sys.exit(1)

    # Check if target is Apktool's output
    is_apktool = (target / "apktool.yml").is_file()
    if is_apktool:
        logger.debug("Target is Apktool output.")

    # Check if specified deobfuscator is correct
    # if not args.deobfuscator.is_file() or not args.deobfuscator.suffix == ".smali":
    #     logger.warning("Specified deobfuscator file is not a .smali file. Fallback to search.")

    # Step 1 - Search for UTF-16 strings (obfuscated chunks)
    logger.debug("Searching for obfuscated strings...")
    candidates = search_candidates(target)

    # Exit if no candidates found
    if len(candidates) == 0:
        logger.error("No candidate found. Is this app really using Paranoid?")
        sys.exit(1)

    logger.debug(f"Found {len(candidates)} candidates.")
    for x in candidates:
        logger.debug(f" - {x[0]} [chunks={len(x[1])}]")

    # Step 2 - Search for deobfuscator class
    logger.debug("Searching for deobfuscator class...")
    getstring_method_signature, chunks = None, None
    for x in candidates:
        getstring_method_signature = search_deobfuscator(target, x[0], is_apktool)
        if getstring_method_signature:
            chunks = x[1]
            break

    # Check
    if not getstring_method_signature or not chunks:
        logger.error(
            "Cannot find Deobfuscator.getString() method. Is this app really using Paranoid?"
        )
        sys.exit(1)

    logger.debug(f"getString method signature: {getstring_method_signature}")

    # 3. Search getString() calls
    logger.info("Searching for getString() calls...")

    # Decode chunks
    chunks = decode_unicode(chunks)

    obfuscated_files = {}
    for x in target.rglob("*"):
        if x.is_file() and x.suffix == ".smali":
            with open(x) as f:
                deobfuscated = deobfuscator.deobfuscate_strings(
                    f.read(), getstring_method_signature, chunks
                )

                if len(deobfuscated) > 0:
                    obfuscated_files[str(x)] = deobfuscated

    # Debug print
    logger.debug(f"Obfuscated files: {len(obfuscated_files)}")
    for k, v in obfuscated_files.items():
        logger.debug(f" - {k}")
        for x in v:
            logger.debug(f"   - {x[0]}: {x[1]}")

    # 4. Deobfuscate
    for file, decoded_strings in obfuscated_files.items():
        logger.info(f"Processing {file}")
        with open(file) as f:
            lines = f.readlines()

        for decoded in decoded_strings:
            line_num, deobfuscated = decoded

            identifier = deobfuscator.extract_identifier_from_invoke(lines[line_num])
            logger.debug(f" - identifier {identifier}")

            # Clear matching const-wide
            for i, x in enumerate(
                reversed(lines[line_num - INSTRUCTION_BUFFER : line_num])
            ):
                x = x.strip()

                # Skip empty lines, comments, labels and directives
                if not x or x.startswith("#") or x.startswith(".") or x.startswith(":"):
                    continue

                if x.startswith("const-wide"):
                    m = deobfuscator.CONST_WIDE_REGEX.match(x)
                    if m and identifier == m.group(1):
                        lines[line_num - i - 1] = REMOVED_COMMENT
                        break

            # Search for move-result-object
            # The next instruction should be move-result-object, because getString() returns a String object
            # If not, it's probably a useless call that was optimized
            for i, x in enumerate(
                lines[line_num + 1 : line_num + 1 + INSTRUCTION_BUFFER]
            ):
                x = x.strip()

                # Skip empty lines, comments, labels and directives
                if not x or x.startswith("#") or x.startswith(".") or x.startswith(":"):
                    continue

                # If next instruction is not move-result-object, break
                if not x.startswith("move-result-object"):
                    logger.debug(
                        f'Could not find move-result-object, probably useless call (string was: "{deobfuscated}")'
                    )
                    break

                # Extract identifier
                m = deobfuscator.MOVE_RESULT_OBJECT_REGEX.match(x)
                if m:
                    lines[
                        line_num + 1 + i
                    ] = f'    const-string {m.group(1)}, "{deobfuscated}"\n'
                break

            # Clear invoke-static call
            if not keep_calls:
                lines[line_num] = REMOVED_COMMENT

        with open(file, "w") as f:
            f.writelines(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deobfuscate paranoid string encryption."
    )
    parser.add_argument(
        "target",
        help="apktool folder or dex file",
        type=pathlib.Path,
    )

    parser.add_argument(
        "-k",
        "--keep-calls",
        help="keep getString() calls",
        action="store_true",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )

    args = parser.parse_args()
    logging.basicConfig(format="%(levelname).1s: %(message)s", level=args.loglevel)

    main(args)
