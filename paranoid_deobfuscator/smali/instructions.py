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

import re
from typing import Any

# Regex components
# CONST_WIDE_REGEX_PATTERN = r"const-wide(?:/16|/32|/high16)?"
# CONST_REGEX_PATTERN = r"const(?:/4|/16|/high16)?"
# CONST_VALUE_REGEX_PATTERN = r"-?0x[0-9a-f]+"
# REGISTER_REGEX_PATTERN = r"([vp][0-9]+)"
# FULLY_CLASSIFIED_NAME = r"L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;"
# SIMPLE_NAME = r"[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF]+"
# TYPE_DESCRIPTOR = r"\[*(?:" + FULLY_CLASSIFIED_NAME + r"|[VZBSCIJFD])"
# STATIC_GET_PUT_FIELD_REGEX = r"(" + FULLY_CLASSIFIED_NAME + r")->(" + SIMPLE_NAME + r"):(" + TYPE_DESCRIPTOR + r")"

CONST = re.compile(r"const(?:/4|/16|/high16|-wide(?:/16|/32|/high16)?)?\s+([vp][0-9]+),\s+(-?0x[0-9a-fA-F]+)")  # noqa: E501
CONST_STRING = re.compile(r'const-string\s+([vp][0-9]+),\s+"(.+)"')  # noqa: E501
NEW_ARRAY = re.compile(
    r"new-array\s+([vp][0-9]+),\s+([vp][0-9]+),\s+(\[*(?:L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;|[VZBSCIJFD]))"  # noqa: E501
)
AGET_APUT = re.compile(
    r"a(?:put|get)(?:-(?:wide|object|boolean|byte|char|short))?\s+([vp][0-9]+),\s+([vp][0-9]+),\s+([vp][0-9]+)"  # noqa: E501
)
SGET_SPUT = re.compile(
    r"s(?:put|get)(?:-(?:wide|object|boolean|byte|char|short))?\s+([vp][0-9]+),\s+((L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;)->([a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF]+):(\[*(?:L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;|[VZBSCIJFD])))"  # noqa: E501
)
INVOKE_STATIC = re.compile(
    r"invoke-static\s+{([vp][0-9]+(?:,\s*[vp][0-9]+)*)},\s+(L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;)->([a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/\[\(\);]+)"  # noqa: E501
)
INVOKE_STATIC_RANGE = re.compile(
    r"invoke-static/range\s*{([vp][0-9]+\s*\.\.\s*[vp][0-9]+)},\s*(L[a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/]+;)->([a-zA-Z0-9$_\- \u00A0-\u1FFF\u2000-\u200A\u2010-\u2027\u202F\u2030-\uD7FF\uE000-\uFFEF\U00010000-\U0010FFFF/\[\(\);]+)"  # noqa: E501
)
MOVE_RESULT = re.compile(r"move-result(?:-(?:wide|object))?\s+([vp][0-9]+)")  # noqa: E501


class SmaliInstrConst:
    def __init__(self, register: str, value: int, _raw: str | None = None):
        self.register = register
        self.value = value
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = CONST.match(data)
        if not m:
            raise ValueError("Invalid const instruction")

        register = m.group(1)
        value = int(m.group(2), 0)

        return SmaliInstrConst(register, value, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.register == other.register and self.value == other.value


class SmaliInstrConstString:
    def __init__(self, register: str, value: str, _raw: str | None = None):
        self.register = register
        self.value = value
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = CONST_STRING.match(data)
        if not m:
            raise ValueError("Invalid const-string instruction")

        register = m.group(1)
        value = m.group(2)

        return SmaliInstrConstString(register, value, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.register == other.register and self.value == other.value


class SmaliInstrInvokeStatic:
    def __init__(self, registers: list[str], class_name: str, method: str, _raw: str | None = None):
        self.registers = registers
        self.class_name = class_name
        self.method = method
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = INVOKE_STATIC.match(data)
        if not m:
            raise ValueError("Invalid invoke-static instruction")

        registers = [x.strip() for x in m.group(1).split(",")]
        class_name = m.group(2)
        method = m.group(3)

        return SmaliInstrInvokeStatic(registers, class_name, method, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.registers == other.registers and self.class_name == other.class_name and self.method == other.method


class SmaliInstrInvokeStaticRange:
    def __init__(self, registers: list[str], class_name: str, method: str, _raw: str | None = None):
        self.registers = registers
        self.class_name = class_name
        self.method = method
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = INVOKE_STATIC_RANGE.match(data)
        if not m:
            raise ValueError("Invalid invoke-static/range instruction")

        # TODO: do we need to include all the possible registers inside the range?
        # For example: {v0 .. v5} -> v0, v1, v2, v3, v4, v5
        registers = [x.strip() for x in m.group(1).split("..")]
        class_name = m.group(2)
        method = m.group(3)

        return SmaliInstrInvokeStaticRange(registers, class_name, method, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.registers == other.registers and self.class_name == other.class_name and self.method == other.method


class SmaliInstrNewArray:
    def __init__(self, register: str, size_register: str, type_descriptor: str, _raw: str | None = None):
        self.register = register
        self.size_register = size_register
        self.type_descriptor = type_descriptor
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = NEW_ARRAY.match(data)
        if not m:
            raise ValueError("Invalid new-array instruction")

        register = m.group(1)
        size_register = m.group(2)
        type_descriptor = m.group(3)

        return SmaliInstrNewArray(register, size_register, type_descriptor, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.register == other.register
            and self.size_register == other.size_register
            and self.type_descriptor == other.type_descriptor
        )


class SmaliInstrAGetAPut:
    def __init__(self, register_dest: str, register_array: str, register_index: str, _raw: str | None = None):
        self.register_dest = register_dest
        self.register_array = register_array
        self.register_index = register_index
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = AGET_APUT.match(data)
        if not m:
            raise ValueError("Invalid aget/aput instruction")

        register_dest = m.group(1)
        register_array = m.group(2)
        register_index = m.group(3)

        return SmaliInstrAGetAPut(register_dest, register_array, register_index, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.register_dest == other.register_dest
            and self.register_array == other.register_array
            and self.register_index == other.register_index
        )


class SmaliInstrSGetSPut:
    def __init__(self, register_dest: str, class_name: str, field_name: str, field_type: str, _raw: str | None = None):
        self.register_dest = register_dest
        self.class_name = class_name
        self.field_name = field_name
        self.field_type = field_type
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = SGET_SPUT.match(data)
        if not m:
            raise ValueError("Invalid sget/sput instruction")

        register_dest = m.group(1)
        # full_field = m.group(2)
        class_name = m.group(3)
        field_name = m.group(4)
        field_type = m.group(5)

        return SmaliInstrSGetSPut(register_dest, class_name, field_name, field_type, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self.register_dest == other.register_dest
            and self.class_name == other.class_name
            and self.field_name == other.field_name
            and self.field_type == other.field_type
        )


class SmaliInstrMoveResult:
    def __init__(self, register: str, _raw: str | None = None):
        self.register = register
        self._raw = _raw

    @staticmethod
    def parse(data: str):
        data = data.strip()

        m = MOVE_RESULT.match(data)
        if not m:
            raise ValueError("Invalid move-result instruction")

        register = m.group(1)

        return SmaliInstrMoveResult(register, _raw=data)

    def __eq__(self, other: Any):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.register == other.register
