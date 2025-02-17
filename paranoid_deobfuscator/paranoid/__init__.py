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
from typing import Any, Dict, List, Literal, TypedDict, overload

from ..smali import SmaliField, SmaliMethod, instructions, register
from . import DeobfuscatorHelper, RandomHelper

# Expose the following classes and functions to the outside world
__all__ = ["DeobfuscatorHelper", "RandomHelper"]

logger = logging.getLogger(__name__)


class SmaliRegisterEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, register.SmaliRegister):
            return o.to_dict()
        return super().default(o)


class ParanoidSmaliParserError(Exception):
    """
    Exception raised for errors encountered by the Paranoid Smali Parser.

    Attributes:
        message (str): The error message.
        extra (Dict[str, Any]): Additional information about the error.

    Methods:
        __str__(): Returns the string representation of the error, including any extra information if available.
    """

    def __init__(self, message: str, extra: Dict[str, Any] = {}):
        super().__init__(message)

        self.extra = extra

    def __str__(self):
        if not self.extra:
            return super().__str__()

        return f"{super().__str__()}\n{json.dumps(self.extra, indent=4, cls=SmaliRegisterEncoder)}"


class ParanoidSmaliParser:
    """
    ParanoidSmaliParser is a class designed to parse and deobfuscate Smali code.

        class_name (str | None): The fully qualified name of the class being parsed.
        fields (Dict[SmaliField, ParanoidSmaliParser.Field]): A dictionary mapping SmaliField instances to their corresponding field data.
        methods (Dict[SmaliMethod, ParanoidSmaliParser.Method]): A dictionary mapping SmaliMethod instances to their corresponding method data.
        target_method (SmaliMethod | None): The target method to look for during parsing.
        _metadata (str): The filename of the Smali file being parsed.
        state (ParanoidSmaliParser.State): The current state of the deobfuscation process.

    Methods:
        __init__(filename: str, target_method: SmaliMethod | None = None):
            Initializes the parser with the given filename and optional target method.

        _reset_state(key_to_reset: str | None = None):
            Resets the parser state to its default values or resets a specific key in the state.

        get_fully_qualified_class_name(line: str) -> str:
            Extracts and returns the fully qualified class name from a Smali class definition line.

        update(line: str):
            Updates the parser state based on the given line of Smali code.
    """

    class Field(TypedDict):
        """
        A TypedDict representing a field with a value and an optional register.

        Attributes:
            value (Any): The value of the field.
            _register (str | None): An optional register associated with the field.
        """

        value: Any
        _register: str | None

    class Method(TypedDict):
        """
        A TypedDict representing a method with constants and static get objects.

        Attributes:
            consts (List[int]): A list of integer constants used in the method.
            sget_objects (List[SmaliField]): A list of static get objects represented by SmaliField instances.
        """

        consts: List[int]
        sget_objects: List[SmaliField]

    class State(TypedDict):
        """
        State is a TypedDict that represents the state of the deobfuscation process.

        Attributes:
            in_method (bool): Indicates if the current context is within a method.
            in_static_constructor (bool): Indicates if the current context is within a static constructor.
            current_method (SmaliMethod | None): The current method being processed, or None if not applicable.
            registers (Dict[str, register.SmaliRegister]): A dictionary mapping register names to their corresponding SmaliRegister objects.
            calls_to_target_method (List[Any]): A list of calls to the target method.
        """

        in_method: bool
        in_static_constructor: bool
        current_method: SmaliMethod | None
        registers: Dict[str, register.SmaliRegister]
        calls_to_target_method: List[Any]

    def __init__(self, *, filename: str, target_method: SmaliMethod | None = None):
        self.class_name: str | None = None
        self.fields: Dict[SmaliField, ParanoidSmaliParser.Field] = {}
        self.methods: Dict[SmaliMethod, ParanoidSmaliParser.Method] = {}

        self.target_method = target_method
        self._metadata = filename

        self._reset_state()

    def _reset_state(self, key_to_reset: str | None = None):
        """
        Resets the state of the parser.

        If a specific key is provided, only that part of the state will be reset.
        Otherwise, the entire state will be reset to its default values.

        Args:
            key_to_reset (str | None): The specific key in the state to reset. If None, the entire state is reset.
        """
        default_state: ParanoidSmaliParser.State = {
            "in_method": False,
            "current_method": None,
            "in_static_constructor": False,
            "registers": {},
            "calls_to_target_method": [],
        }

        if key_to_reset:
            self.state[key_to_reset] = default_state[key_to_reset]
        else:
            self.state = default_state

    @staticmethod
    def get_fully_qualified_class_name(line: str) -> str:
        """
        Extracts the fully qualified class name from a given Smali class definition line.

        Args:
            line (str): A line from a Smali file that is expected to be a class definition.

        Returns:
            str: The fully qualified class name extracted from the line.

        Raises:
            ParanoidSmaliParserError: If the line does not start with ".class".
        """
        if not line.startswith(".class"):
            raise ParanoidSmaliParserError("Line is not a class definition", {"line": line})

        return line.split()[-1]

    def update(self, line: str, line_number: int = 0):
        """
        Updates the internal state based on the provided Smali code line.

        Args:
            line (str): A single line of Smali code to be processed.

        The method performs the following actions based on the content of the line:
            - Strips leading and trailing whitespace from the line.
            - Skips empty lines.
            - Parses and updates the class name if the line defines a class.
            - Parses and updates fields if the line defines a field.
            - Parses and updates methods if the line defines a method.
            - Updates the state when entering or exiting a method.
            - Updates registers for constant strings and constants.
            - Handles static field gets and puts.
            - Creates arrays and updates their values.
            - Handles static method invocations.

        Raises:
            ParanoidSmaliParserError: If parameters are encountered in an invoke-static instruction.
        """
        line = line.strip()

        # Skip empty lines
        if not line:
            return

        # Get fully qualified class name
        if line.startswith(".class"):
            self.class_name = self.get_fully_qualified_class_name(line)
            return

        # Parse fields
        if line.startswith(".field"):
            field = SmaliField.from_string(line, self.class_name)
            self.fields[field] = {
                "value": None,
                "_register": None,
            }
            return

        # Parse methods
        if line.startswith(".method"):
            method = SmaliMethod.from_string(line, self.class_name)
            self.methods[method] = {
                "consts": [],
                "sget_objects": [],
            }
            self.state["in_method"] = True
            self.state["current_method"] = method
            # logger.debug(f"{line} # -> Entering method")

            # Check if we are in a static constructor
            if "static" in method.modifiers and "constructor" in method.modifiers and method.method == "<clinit>":
                self.state["in_static_constructor"] = True
                # logger.debug(f"{line} # -> Entering static constructor")

            return

        if line.startswith(".end method"):
            self.state["in_method"] = False
            self.state["in_static_constructor"] = False
            # logger.debug(f"{line} # -> Exiting method")
            return

        # Update registers
        if line.startswith("const-string"):
            try:
                instr = instructions.SmaliInstrConstString.parse(line)
            except ValueError:
                return

            # If the register is an array, update the associated field value
            current_value = self.state["registers"].get(instr.register, None)
            if current_value is not None and isinstance(current_value, register.SmaliRegisterArray):
                for field, data in self.fields.items():
                    if data["_register"] == instr.register:
                        self.fields[field]["value"] = self.state["registers"][instr.register].value

            self.state["registers"][instr.register] = register.SmaliRegisterString(instr.value)
            return

        if line.startswith("const"):
            try:
                instr = instructions.SmaliInstrConst.parse(line)
            except ValueError:
                return

            # If the register is an array, update the associated field value
            current_value = self.state["registers"].get(instr.register, None)
            if current_value is not None and isinstance(current_value, register.SmaliRegisterArray):
                for field, data in self.fields.items():
                    if data["_register"] == instr.register:
                        self.fields[field]["value"] = self.state["registers"][instr.register].value

            # Add const to method consts
            if self.state["current_method"]:
                self.methods[self.state["current_method"]]["consts"].append(instr.value)

            self.state["registers"][instr.register] = register.SmaliRegisterConst(instr.value)
            return

        if line.startswith("sget-object"):
            if not self.state["in_method"]:
                return

            try:
                instr = instructions.SmaliInstrSGetSPut.parse(line)
            except ValueError:
                return

            field = SmaliField(instr.field_name, instr.field_type, [], instr.class_name)

            if self.state["current_method"]:
                self.methods[self.state["current_method"]]["sget_objects"].append(field)

        # Create array
        if line.startswith("new-array"):
            try:
                instr = instructions.SmaliInstrNewArray.parse(line)
            except ValueError:
                return

            # Skip array other than [Ljava/lang/String;
            # Necessary for speed
            if instr.type_descriptor != "[Ljava/lang/String;":
                return

            # Get size from register
            if instr.size_register not in self.state["registers"]:
                return

            size_register = self.state["registers"][instr.size_register]
            # Check if size_register is instance of SmaliRegisterConst
            if not isinstance(size_register, register.SmaliRegisterConst):
                logger.debug(self._metadata)
                logger.debug(line)
                logger.debug(f"Size register {instr.size_register} is not a const")
                logger.debug(f" - Class: {size_register.__class__}")
                return

            self.state["registers"][instr.register] = register.SmaliRegisterArray([None] * size_register.get_value())
            return

        # Put value in field
        if line.startswith("sput-object"):
            try:
                instr = instructions.SmaliInstrSGetSPut.parse(line)
            except ValueError:
                return

            # Check if the field is in the current class
            if instr.class_name != self.class_name:
                return

            # Get the field with the matching name
            field = next((f for f in self.fields if f.name == instr.field_name), None)
            if field is None:
                return

            # Save the register and the last value
            self.fields[field]["_register"] = instr.register_dest
            return

        # Insert value in array
        if line.startswith("aput-object"):
            try:
                instr = instructions.SmaliInstrAGetAPut.parse(line)
            except ValueError:
                return

            # Check if arguments are in the registers
            if (
                instr.register_array not in self.state["registers"]
                or instr.register_index not in self.state["registers"]
                or instr.register_dest not in self.state["registers"]
            ):
                return

            array = self.state["registers"][instr.register_array]
            index = self.state["registers"][instr.register_index]
            value = self.state["registers"][instr.register_dest]

            # Check if the array_register is an array
            if not isinstance(array, register.SmaliRegisterArray):
                return

            # Check if the value is a const-string
            if not isinstance(value, register.SmaliRegisterString):
                # logger.warning(f"Value register {instr.register_dest} is not a string")
                # logger.warning(f"{self._metadata}:{line_number+1} -> {line}")
                return

            # Check if the index is a const
            if not isinstance(index, register.SmaliRegisterConst):
                logger.warning(f"Index register {instr.register_index} is not a const")
                return

            # Append the value to the array
            array.value[index.value] = value.value
            return

        if line.startswith("invoke-static"):
            try:
                instr = instructions.SmaliInstrInvokeStatic.parse(line)
            except ValueError:
                return

            method_name, method_arguments, method_return_type = SmaliMethod.parse_method_signature(instr.method)

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

            # TODO: parameters are not supported
            # This is a limitation of the current implementation.
            # It is possible to support them, but it would require a more complex approach.
            if first_register.startswith("p"):
                try:
                    self.state["calls_to_target_method"].append(self.state["registers"][first_register])
                except KeyError:
                    raise ParanoidSmaliParserError(
                        "Parameters are not supported",
                        extra={
                            "registers": self.state["registers"],
                            "register": first_register,
                            "line": line,
                        },
                    )

            try:
                self.state["calls_to_target_method"].append(self.state["registers"][first_register])
            except KeyError:
                raise ParanoidSmaliParserError(
                    "Register not found",
                    extra={
                        "registers": self.state["registers"],
                        "register": first_register,
                        "line": line,
                    },
                )

            return


@overload
def deobfuscate_string(id: int, chunks: List[str]) -> bytes: ...
@overload
def deobfuscate_string(id: int, chunks: List[str], decode: Literal[False]) -> bytes: ...
@overload
def deobfuscate_string(id: int, chunks: List[str], decode: Literal[True]) -> str: ...
def deobfuscate_string(id: int, chunks: List[str], decode: bool = False):
    """
    Deobfuscates a string based on the provided identifier and chunks.

    Args:
        id (int): The identifier for the string to be deobfuscated.
        chunks (List[str]): A list of string chunks used for deobfuscation.
        decode (bool, optional): If True, the result will be decoded to a string. Defaults to False.

    Returns:
        Union[bytes, str]: The deobfuscated string as bytes, or as a decoded string if decode is True.
    """
    result = DeobfuscatorHelper.getString(id, chunks)
    if decode:
        return result.decode()

    return result
