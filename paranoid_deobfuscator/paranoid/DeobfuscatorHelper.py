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
#  - https://github.com/MichaelRocks/paranoid/blob/7030aea9aeb8d245c3bea2ef6df20d104d198fce/core/src/main/java/io/michaelrocks/paranoid/DeobfuscatorHelper.java
#  - https://github.com/LSPosed/LSParanoid/blob/91e1231bc0062d1f90685d739bff9bc50a2b57b0/core/src/main/java/org/lsposed/lsparanoid/DeobfuscatorHelper.java

from typing import List

import numpy as np

from . import RandomHelper, utils

MAX_CHUNK_LENGTH = 0x1FFF


def getString(id: int, chunks: List[str]) -> bytes:
    _id = utils.to_int(id, 64, signed=False)

    with np.errstate(over="ignore"):
        state = RandomHelper.seed(_id & 0xFFFFFFFF)
        state = RandomHelper.next(state)
        low = np.uint64(state) >> 32 & 0xFFFF
        state = RandomHelper.next(state)
        high = np.uint64(state) >> 16 & 0xFFFF0000
        index = (_id >> 32) ^ low ^ high
        state = getCharAt(index, chunks, state)
        length = np.uint64(state) >> 32 & 0xFFFF

        output = []
        for x in range(length):
            state = getCharAt(index + x + 1, chunks, state)
            output.append(np.uint64(state) >> 32 & 0xFFFF)

        return "".join(map(chr, output)).encode("unicode-escape")


def getCharAt(char_index, chunks, state):
    next_state = RandomHelper.next(state)
    chunk = chunks[int(char_index / MAX_CHUNK_LENGTH)]
    char = chunk[int(char_index % MAX_CHUNK_LENGTH)]

    return np.int64(np.uint64(next_state) ^ (np.uint64(ord(char)) << np.uint16(32)))
