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

from typing import Any


class SmaliField:
    def __init__(
        self,
        name: str,
        type: str,
        modifiers: list[str] = [],
        class_name: str | None = None,
        init_value: str | None = None,
    ):
        self.name = name
        self.type = type
        self.modifiers = modifiers
        self.class_name = class_name
        self.init_value = init_value

    @classmethod
    def from_string(cls, data: str, class_name: str | None = None):
        if not data.startswith(".field"):
            raise ValueError("Invalid field string")

        parts = data.split()

        # Check if the field has value
        init_value = None
        if "=" in parts:
            init_value = parts[-1]
            parts = parts[: parts.index("=")]

        field_modifiers = parts[1:-1]
        field_name, field_type = parts[-1].split(":")

        return cls(field_name, field_type, field_modifiers, class_name, init_value)

    def to_smali(self):
        if self.init_value:
            return f".field {' '.join(self.modifiers)} {self.name}:{self.type} = {self.init_value}"

        return f".field {' '.join(self.modifiers)} {self.name}:{self.type}"

    def __repr__(self):
        return f"SmaliField(name={self.name}, type={self.type}, modifiers={self.modifiers}, class_name={self.class_name}, init_value={self.init_value})"

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.name == other.name
            and self.type == other.type
            and self.modifiers == other.modifiers
            and self.class_name == other.class_name
            and self.init_value == other.init_value
        )

    def __hash__(self):
        return hash((self.name, self.type, tuple(self.modifiers), self.class_name, self.init_value))


class SmaliMethod:
    def __init__(
        self,
        method: str,
        arguments: list[str] = [],
        return_type: str = "V",
        modifiers: list[str] = [],
        class_name: str | None = None,
    ):
        self.method = method
        self.arguments = arguments
        self.return_type = return_type
        self.modifiers = modifiers
        self.class_name = class_name

    @staticmethod
    def parse_arguments_string(data: str):
        arguments: list[str] = []

        is_in_class = False

        tmp = ""
        for c in data:
            tmp += c

            # Start of a fully qualified class name
            if c == "L":
                is_in_class = True
                continue

            # End of a fully qualified class name
            if is_in_class and c == ";":
                is_in_class = False
                arguments.append(tmp)
                tmp = ""
                continue

            # Primitive type
            if not is_in_class and c in "VZBSCIJFD":
                arguments.append(tmp)
                tmp = ""
                continue

        return arguments

    @staticmethod
    def parse_method_signature(data: str):
        method_name = data.split("(")[0]
        method_return_type = data.split(")")[1]

        # Parse arguments
        method_arguments_raw = data.split("(")[1].split(")")[0]
        method_arguments = SmaliMethod.parse_arguments_string(method_arguments_raw)

        return method_name, method_arguments, method_return_type

    @classmethod
    def from_string(cls, data: str, class_name: str | None = None):
        if not data.startswith(".method"):
            raise ValueError("Invalid method string")

        parts = data.split()
        method_signature = parts[-1]
        method_modifiers = parts[1:-1]

        method_name, method_arguments, method_return_type = SmaliMethod.parse_method_signature(method_signature)

        return cls(method_name, method_arguments, method_return_type, method_modifiers, class_name)

    def to_smali(self):
        return f".method {' '.join(self.modifiers)} {self.method}({''.join(self.arguments)}){self.return_type}"

    def __repr__(self):
        return f"SmaliMethod(method={self.method}, arguments={self.arguments}, return_type={self.return_type}, modifiers={self.modifiers}, class_name={self.class_name})"

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.method == other.method
            and self.arguments == other.arguments
            and self.return_type == other.return_type
            and self.modifiers == other.modifiers
            and self.class_name == other.class_name
        )

    def __hash__(self):
        return hash((self.method, tuple(self.arguments), self.return_type, tuple(self.modifiers), self.class_name))
