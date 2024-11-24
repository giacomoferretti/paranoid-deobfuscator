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

# This class was converted from the following Java code:
#  - https://github.com/MichaelRocks/paranoid/blob/7030aea9aeb8d245c3bea2ef6df20d104d198fce/core/src/main/java/io/michaelrocks/paranoid/RandomHelper.java
#  - https://github.com/LSPosed/LSParanoid/blob/91e1231bc0062d1f90685d739bff9bc50a2b57b0/core/src/main/java/org/lsposed/lsparanoid/RandomHelper.java

import numpy as np

from . import utils


# MurmurHash3 "Mix4" variant
def seed(x: np.int64 | np.integer | int) -> np.int64:
    _x = utils.to_int(x, 64, signed=False)

    with np.errstate(over="ignore"):
        z = (_x ^ (_x >> 33)) * utils.to_int(0x62A9D9ED799705F5, 64)
        y = (z ^ (z >> 28)) * utils.to_int(0xCB24D0A5C88C35B3, 64)

        return y >> 32


def rotl(x: np.int16 | np.integer | int, k: int) -> np.int16:
    _x = utils.to_int(x, 32, signed=False)  # Need to be not signed to get zeros while shifting right

    with np.errstate(over="ignore"):
        return np.int16(_x << k | _x >> (32 - k))


def next(state: np.int64 | np.integer | int) -> np.int64:
    _state = utils.to_int(state, 64, signed=False)

    with np.errstate(over="ignore"):
        s0 = np.int16(_state & 0xFFFF)
        s1 = np.int16((_state >> 16) & 0xFFFF)
        next = s0
        next += s1
        next = rotl(next, 9)
        next += s0

        s1 ^= s0
        s0 = rotl(s0, 13)
        s0 ^= s1
        s0 ^= s1 << 5
        s1 = rotl(s1, 10)

        result = np.int64(next)
        result <<= np.int64(16)
        result |= np.int64(s1)
        result <<= np.int64(16)
        result |= np.int64(s0)
        return result
