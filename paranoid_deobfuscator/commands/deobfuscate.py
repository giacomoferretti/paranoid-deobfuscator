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
import shutil
import sys
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, TypedDict

import click

from .. import __version__ as deobfuscator_version
from .. import constants, paranoid, report_github_issue_message
from ..encoding import decode_unicode_chunks, encode_smali_string
from ..smali import register

logger = logging.getLogger(__name__)

REMOVED_COMMENT = (
    f"    # Removed with https://github.com/giacomoferretti/paranoid-deobfuscator - v{deobfuscator_version}"
)


class ParanoidSmaliDeobfuscator:
    class SmaliRegisterEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, register.SmaliRegister):
                return o.to_dict()
            return super().default(o)

    class ParanoidSmaliDeobfuscatorError(Exception):
        def __init__(self, message: str, extra: Dict[str, Any] = {}):
            super().__init__(message)

            self.extra = extra

        def __str__(self):
            if not self.extra:
                return super().__str__()

            return f"{super().__str__()}\n{json.dumps(self.extra, indent=4, cls=ParanoidSmaliDeobfuscator.SmaliRegisterEncoder)}"

    class State(TypedDict):
        class_name: str
        registers: Dict[str, paranoid.register.SmaliRegister]
        last_deobfuscated_string: str | None
        inside_try_block: bool

    def __init__(
        self,
        filepath: pathlib.Path | str,
        target_method: paranoid.SmaliMethod,
        obfuscated_chunks: List[str],
        # edit_in_place: bool = True,
    ):
        self.filepath = filepath
        # if edit_in_place:
        #     self.file = open(filepath, "r+")
        # else:
        #     self.file = open(filepath, "r")
        self.file = open(filepath, "r")
        self.tmp_file = NamedTemporaryFile(mode="wt", dir=pathlib.Path(filepath).parent.absolute(), delete=False)

        self.target_method = target_method
        self.obfuscated_chunks = obfuscated_chunks
        self._reset_state()

    def _reset_state(self, key_to_reset: str | None = None):
        default_state: ParanoidSmaliDeobfuscator.State = {
            "class_name": "",
            "registers": {},
            "last_deobfuscated_string": None,
            "inside_try_block": False,
        }

        if key_to_reset:
            self.state[key_to_reset] = default_state[key_to_reset]
        else:
            self.state = default_state

    @staticmethod
    def get_fully_qualified_class_name(line: str) -> str:
        if not line.startswith(".class"):
            raise Exception("Line does not start with .class")

        return line.split()[-1]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

    def process(self, line: str, line_num: int) -> str | None:
        # Reset the state if the result from the getString method is not used
        if self.state["last_deobfuscated_string"] and line.startswith("invoke"):
            self.state["last_deobfuscated_string"] = None

        if line.startswith(":try_start"):
            self.state["inside_try_block"] = True
            return

        if line.startswith(":try_end"):
            self.state["inside_try_block"] = False
            return

        # Get fully qualified class name
        if line.startswith(".class"):
            self.state["class_name"] = self.get_fully_qualified_class_name(line)
            return

        # Update registers
        if line.startswith("const"):
            try:
                instr = paranoid.instructions.SmaliInstrConst.parse(line)
            except ValueError:
                return

            self.state["registers"][instr.register] = paranoid.register.SmaliRegisterConst(instr.value)
            return

        # Search for calls to the target method
        if line.startswith("invoke-static"):
            try:
                # Try to parse invoke-static/range first
                instr = paranoid.instructions.SmaliInstrInvokeStaticRange.parse(line)
                instr = paranoid.instructions.SmaliInstrInvokeStatic(
                    instr.registers, instr.class_name, instr.method, instr._raw
                )
            except ValueError:
                try:
                    instr = paranoid.instructions.SmaliInstrInvokeStatic.parse(line)
                except ValueError:
                    return

            method_name, method_arguments, method_return_type = paranoid.SmaliMethod.parse_method_signature(
                instr.method
            )

            # Check if the target method is the one we are looking for
            if not (
                self.target_method
                and instr.class_name == self.target_method.class_name
                and method_name == self.target_method.method
                and method_arguments == self.target_method.arguments
                and method_return_type == self.target_method.return_type
                and len(instr.registers) == 2
            ):
                return

            first_register = instr.registers[0]

            # Get the value of the register
            register_value = self.state["registers"].get(first_register)

            # TODO: parameters are not supported
            # This is a limitation of the current implementation.
            # It is possible to support them, but it would require a more complex approach.
            if first_register.startswith("p") and not register_value:
                raise ParanoidSmaliDeobfuscator.ParanoidSmaliDeobfuscatorError(
                    "Parameters are not supported",
                    extra={
                        "registers": self.state["registers"],
                        "register": first_register,
                        "line": line,
                    },
                )

            if not register_value:
                raise ParanoidSmaliDeobfuscator.ParanoidSmaliDeobfuscatorError(
                    "Register not found",
                    extra={
                        "registers": self.state["registers"],
                        "register": first_register,
                        "line": line,
                    },
                )

            # Check if the register is a constant
            if not isinstance(register_value, paranoid.register.SmaliRegisterConst):
                raise ParanoidSmaliDeobfuscator.ParanoidSmaliDeobfuscatorError(
                    "Register is not a constant",
                    extra={
                        "registers": self.state["registers"],
                        "register": first_register,
                        "line": line,
                    },
                )

            # Deobfuscate the string
            deobfuscated_string = paranoid.deobfuscate_string(register_value.value, self.obfuscated_chunks, True)
            self.state["last_deobfuscated_string"] = deobfuscated_string

            # Edge case: if we are inside a try block, we need to have at least one valid instruction,
            # so we add a nop instruction, otherwise the smali file will be invalid and the APK will recompile
            if self.state["inside_try_block"]:
                return f"    nop {REMOVED_COMMENT.strip()}"

            return REMOVED_COMMENT

        # Move result object
        if line.startswith("move-result-object"):
            try:
                instr = paranoid.instructions.SmaliInstrMoveResult.parse(line)
            except ValueError:
                return

            if self.state["last_deobfuscated_string"] is not None:
                new_line = f'    const-string {instr.register}, "{encode_smali_string(self.state["last_deobfuscated_string"])}"'
                self.state["last_deobfuscated_string"] = None
                return new_line

            return

        return

    def update(self, _line: str, line_num: int = 0):
        line = _line.strip()

        # Skip empty lines
        if not line:
            self.tmp_file.write(_line)
            return

        # Process the line
        try:
            updated_line = self.process(line, line_num)
            if updated_line is not None:
                self.tmp_file.write(updated_line + "\n")
                return
        except ParanoidSmaliDeobfuscator.ParanoidSmaliDeobfuscatorError as e:
            # Ignore Parameters are not supported
            if e.args[0] == "Parameters are not supported":
                logger.warning(f"{self.filepath}:{line_num+1}: Detected unsupported method call")
                # Add the line to the temporary file
                self.tmp_file.write(_line)
                return

            # Log and raise the error
            logger.error(report_github_issue_message(str(e)))
            raise e

        # Add the line to the temporary file
        self.tmp_file.write(_line)


@click.command(name="deobfuscate", help="Deobfuscate a paranoid obfuscated APK smali files")
@click.argument("target", type=click.Path(exists=True, file_okay=False))
def cli(target: str):
    target_directory = pathlib.Path(target)

    # First pass: find the get string method and the obfuscated string array
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
        sys.exit(1)

    get_string_method, get_string_fields = potential_get_string_methods[0]
    get_string_field: paranoid.SmaliField = get_string_fields[0]

    # Check if only one field is found
    if len(get_string_fields) != 1:
        logger.error("Found more than one potential obfuscated string array")
        logger.error("This is not supported yet")
        sys.exit(1)

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

    # Decode the chunks
    chunks = decode_unicode_chunks(chunks)

    # Second pass: deobfuscate file
    for smali_file in target_directory.rglob("*.smali"):
        with ParanoidSmaliDeobfuscator(smali_file, get_string_method, chunks) as deobfuscator:
            for line_num, line in enumerate(deobfuscator.file):
                deobfuscator.update(line, line_num)

        # Replace the original file with the temporary one
        shutil.move(deobfuscator.tmp_file.name, smali_file)
