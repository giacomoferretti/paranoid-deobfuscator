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


from abc import ABC, abstractmethod


class SmaliRegister(ABC):
    def __init__(self, value):
        self.value = value
        self.validate_value(value)

    @abstractmethod
    def validate_value(self, value):
        """Validate the value for the specific type."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def get_value(self):
        return self.value

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        """Return the type of the register."""
        pass


class SmaliRegisterConst(SmaliRegister):
    def validate_value(self, value):
        if not isinstance(value, int):
            raise ValueError("For 'const', value must be an int")

    @classmethod
    def get_type(cls):
        return "const"


class SmaliRegisterArray(SmaliRegister):
    def validate_value(self, value):
        if not isinstance(value, list):
            raise ValueError("For 'array', value must be a list")
        # if not all(isinstance(item, str) for item in value):
        #     raise ValueError("All elements in the 'array' value must be strings")

    @classmethod
    def get_type(cls):
        return "array"


class SmaliRegisterString(SmaliRegister):
    def validate_value(self, value):
        if not isinstance(value, str):
            raise ValueError("For 'string', value must be a string")

    @classmethod
    def get_type(cls):
        return "string"
