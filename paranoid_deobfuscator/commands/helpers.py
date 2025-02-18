# Copyright 2024 Giacomo Ferretti
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

import json
import logging
import pathlib

import click

from .. import constants, paranoid, report_github_issue_message
from ..encoding import decode_unicode_chunks
from ..smali import SmaliField, register

logger = logging.getLogger(__name__)


@click.group(name="helpers", help="Helper commands")
def cli():
    pass


@cli.command(help="Extracts the strings from a paranoid obfuscated APK")
@click.argument("target", type=click.Path(exists=True, file_okay=False))
def extract_strings(target: str):
    target_directory = pathlib.Path(target)

    potential_get_string_methods = []
    potential_obfuscated_string_arrays = []
    for smali_file in target_directory.rglob("*.smali"):
        with open(smali_file, "r") as f:
            smali_parser = paranoid.ParanoidSmaliParser(filename=str(smali_file))

            for line_num, line in enumerate(f):
                smali_parser.update(line, line_num)

            # Add potential get string methods
            for method, data in smali_parser.methods.items():
                if (
                    data["consts"] == constants.PARANOID_GET_STRING_CONST_SIGNATURE
                    and method.arguments == constants.PARANOID_GET_STRING_ARGUMENTS
                    and method.return_type == constants.PARANOID_GET_STRING_RETURN_TYPE
                ):
                    potential_get_string_methods.append((method, data["sget_objects"]))

            # Add potential obfuscated string arrays
            for field, data in smali_parser.fields.items():
                if field.type == "[Ljava/lang/String;":
                    potential_obfuscated_string_arrays.append((field, data["value"]))

    # Check if only one method is found
    if len(potential_get_string_methods) != 1:
        logger.error("Found more than one potential get string method")
        logger.error("This is not supported yet")
        return

    get_string_method, get_string_fields = potential_get_string_methods[0]
    get_string_field: SmaliField = get_string_fields[0]

    # Check if only one field is found
    if len(get_string_fields) != 1:
        logger.error("Found more than one potential obfuscated string array")
        logger.error("This is not supported yet")
        return

    # Extract the string chunks
    chunks = []
    for field, value in potential_obfuscated_string_arrays:
        if field.class_name == get_string_field.class_name and field.name == get_string_field.name:
            chunks = value

    # Check if the chunks are found
    if not chunks:
        logger.error("No chunks found")
        return

    logger.debug(f"Method: {get_string_method}")
    logger.debug(f"Field: {get_string_field}")
    logger.debug("Chunks:")
    logger.debug(chunks)

    # Find all the deobfuscation values
    deobfuscation_values = []
    for smali_file in target_directory.rglob("*.smali"):
        with open(smali_file, "r") as f:
            smali_parser = paranoid.ParanoidSmaliParser(filename=str(smali_file), target_method=get_string_method)

            for line_num, line in enumerate(f):
                try:
                    smali_parser.update(line, line_num)
                except paranoid.ParanoidSmaliParserError as e:
                    # Ignore Parameters are not supported
                    if e.args[0] == "Parameters are not supported":
                        logger.warning(f"{smali_file}:{line_num+1}: Detected unsupported method call")
                        continue

                    # Log and raise the error
                    logger.error(report_github_issue_message(str(e)))
                    raise e

            deobfuscation_values.extend(smali_parser.state["calls_to_target_method"])

    logger.debug("Deobfuscation values:")
    logger.debug(deobfuscation_values)

    # Decode the chunks
    chunks = decode_unicode_chunks(chunks)

    # Get the raw value
    values = []
    for x in deobfuscation_values:
        if isinstance(x, register.SmaliRegisterConst):
            values.append(x.value)

    # Deobfuscate the strings
    for x in values:
        print(f"[{x:x}]:{paranoid.deobfuscate_string(x, chunks, True)}")


@cli.command(help="Save the chunks from a paranoid obfuscated APK")
@click.argument("target", type=click.Path(exists=True, file_okay=False))
@click.argument("output", type=click.Path(exists=False, dir_okay=False))
def extract_chunks(target: str, output: str):
    target_directory = pathlib.Path(target)

    potential_get_string_methods = []
    potential_obfuscated_string_arrays = []
    for smali_file in target_directory.rglob("*.smali"):
        with open(smali_file, "r") as f:
            smali_parser = paranoid.ParanoidSmaliParser(filename=str(smali_file))

            for line_num, line in enumerate(f):
                smali_parser.update(line, line_num)

            # Add potential get string methods
            for method, data in smali_parser.methods.items():
                if (
                    data["consts"] == constants.PARANOID_GET_STRING_CONST_SIGNATURE
                    and method.arguments == constants.PARANOID_GET_STRING_ARGUMENTS
                    and method.return_type == constants.PARANOID_GET_STRING_RETURN_TYPE
                ):
                    potential_get_string_methods.append((method, data["sget_objects"]))

            # Add potential obfuscated string arrays
            for field, data in smali_parser.fields.items():
                if field.type == "[Ljava/lang/String;":
                    potential_obfuscated_string_arrays.append((field, data["value"]))

    # Check if only one method is found
    if len(potential_get_string_methods) != 1:
        logger.error("Found more than one potential get string method")
        logger.error("This is not supported yet")
        return

    get_string_method, get_string_fields = potential_get_string_methods[0]
    get_string_field: SmaliField = get_string_fields[0]

    # Check if only one field is found
    if len(get_string_fields) != 1:
        logger.error("Found more than one potential obfuscated string array")
        logger.error("This is not supported yet")
        return

    # Extract the string chunks
    chunks = []
    for field, value in potential_obfuscated_string_arrays:
        if field.class_name == get_string_field.class_name and field.name == get_string_field.name:
            chunks = value

    # Check if the chunks are found
    if not chunks:
        logger.error("No chunks found")
        return

    # Save chunks
    with open(output, "w") as f:
        json.dump(chunks, f, indent=4)


@cli.command(help="Deobfuscate a string using extracted chunks")
@click.argument("chunk_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("deobfuscation_long", type=int)
def deobfuscate_string(chunk_file: str, deobfuscation_long: int):
    chunks = []
    with open(chunk_file, "r") as f:
        chunks = json.load(f)

    # Decode the chunks
    chunks = decode_unicode_chunks(chunks)

    print(f"[{deobfuscation_long:x}]:{paranoid.deobfuscate_string(deobfuscation_long, chunks, True)}")
