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

import warnings

import numpy as np

# Overflow warnings are expected, ignore them
warnings.simplefilter("ignore", RuntimeWarning)

MAX_CHUNK_LENGTH = 0x1FFF


# MurmurHash3 "Mix4" variant
def RandomHelper_seed(x):
    z = (np.uint64(x) ^ (np.uint64(x) >> np.uint64(33))) * np.uint64(0x62A9D9ED799705F5)
    y = (np.uint64(z) ^ (np.uint64(z) >> np.uint64(28))) * np.uint64(0xCB24D0A5C88C35B3)
    return np.int64(np.uint64(y) >> np.uint64(32))


def RandomHelper_next(state):
    s0 = np.int16(np.uint64(state) & np.uint64(0xFFFF))
    s1 = np.int16(np.uint64(state) >> np.uint64(16) & np.uint64(0xFFFF))
    next = s0
    next += s1
    next = RandomHelper_rotl(next, 9)
    next += s0

    s1 = np.int16(np.uint16(s1) ^ np.uint16(s0))
    s0 = RandomHelper_rotl(s0, 13)
    s0 = np.int16(np.uint16(s0) ^ np.uint16(s1))
    s0 = np.int16(np.uint16(s0) ^ np.uint16(np.uint16(s1) << np.uint16(5)))
    s1 = RandomHelper_rotl(s1, 10)

    result = next
    result <<= 16
    result |= s1
    result <<= 16
    result |= s0
    return result


def RandomHelper_rotl(x, k):
    return np.int16((np.uint32(x) << np.uint32(k)) | (np.uint32(x) >> (32 - np.uint32(k))))


def DeobfuscatorHelper_getString(id, chunks):
    state = RandomHelper_seed(np.array(id).astype(np.uint64) & np.uint64(0xFFFFFFFF))
    state = RandomHelper_next(state)
    low = np.int64((np.array(state).astype(np.uint64) >> np.uint64(32)) & np.uint64(0xFFFF))
    state = RandomHelper_next(state)
    high = np.int64((np.array(state).astype(np.uint64) >> np.uint64(16)) & np.uint64(0xFFFF0000))
    index = np.int32(
        (np.array(id).astype(np.uint64) >> np.uint64(32)) ^ np.uint64(low) ^ np.uint64(high)
    )
    state = DeobfuscatorHelper_getCharAt(index, chunks, state)
    length = np.int32((np.array(state).astype(np.uint64) >> np.uint64(32)) & np.uint64(0xFFFF))

    output = []

    for x in range(length):
        state = DeobfuscatorHelper_getCharAt(index + x + 1, chunks, state)
        output.append(state >> 32 & 0xFFFF)

    return "".join(map(chr, output)).encode("unicode-escape")


def DeobfuscatorHelper_getCharAt(char_index, chunks, state):
    next_state = RandomHelper_next(state)
    chunk = chunks[int(char_index / MAX_CHUNK_LENGTH)]

    return np.int64(
        np.uint64(next_state)
        ^ (
            np.uint64(
                np.frombuffer(
                    chunk[int(char_index % MAX_CHUNK_LENGTH)].encode("utf-16", "surrogatepass")[
                        2:
                    ],
                    dtype=np.uint16,
                )[0]
            )
            << np.uint16(32)
        )
    )
