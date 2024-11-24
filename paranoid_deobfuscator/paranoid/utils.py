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

import numpy as np


def to_int(num: np.integer | int, bit_size: int = 32, signed: bool = True) -> np.integer:
    """
    Convert a number to a numpy integer of a specified bit size and sign.

    Parameters:
        num (int): The number to convert.
        bit_size (int, optional): The bit size of the integer. Must be one of 8, 16, 32, or 64. Default is 32.
        signed (bool, optional): Whether the integer should be signed or unsigned. Default is True.

    Returns:
        np.integer: The converted numpy integer.

    Raises:
        ValueError: If the bit size is not one of 8, 16, 32, or 64.
        ValueError: If the number is out of range for the specified bit size.
    """
    if bit_size not in (8, 16, 32, 64):
        raise ValueError("Invalid bit size. Must be 8, 16, 32, or 64.")

    if not (0 <= num <= 2**bit_size - 1 or -(2 ** (bit_size - 1)) <= num < 2 ** (bit_size - 1)):
        raise ValueError(f"Number out of range for {bit_size}-bit integer.")

    if signed:
        if num < 0:
            if bit_size == 8:
                return np.int8(num)
            elif bit_size == 16:
                return np.int16(num)
            elif bit_size == 32:
                return np.int32(num)
            elif bit_size == 64:
                return np.int64(num)
        else:
            if bit_size == 8:
                return np.uint8(num).view(np.uint8)
            elif bit_size == 16:
                return np.uint16(num).view(np.uint16)
            elif bit_size == 32:
                return np.uint32(num).view(np.uint32)
            elif bit_size == 64:
                return np.uint64(num).view(np.uint64)
    else:
        if num < 0:
            if bit_size == 8:
                return np.int8(num).view(np.uint8)
            elif bit_size == 16:
                return np.int16(num).view(np.uint16)
            elif bit_size == 32:
                return np.int32(num).view(np.uint32)
            elif bit_size == 64:
                return np.int64(num).view(np.uint64)
        else:
            if bit_size == 8:
                return np.uint8(num)
            elif bit_size == 16:
                return np.uint16(num)
            elif bit_size == 32:
                return np.uint32(num)
            elif bit_size == 64:
                return np.uint64(num)
