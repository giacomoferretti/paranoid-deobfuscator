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
import pytest

from paranoid_deobfuscator.paranoid import DeobfuscatorHelper, RandomHelper, utils


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ((-31289, 16, False), np.uint16(34247)),
    ],
)
def test_paranoid_utils_to_int(input, expected_result):
    assert utils.to_int(*input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (2669835571, 2366240958),
    ],
)
def test_paranoid_RandomHelper_seed(input, expected_result):
    assert RandomHelper.seed(input).view(np.int64) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ((-31289, 9), -28673),
        ((-1858, 13), -8193),
        ((30135, 10), -9216),
        ((-1880, 9), 20991),
        ((7336, 13), 0),
        ((-16216, 10), -23553),
        ((-10841, 9), 20479),
        ((-10840, 13), 8191),
        ((10839, 10), 23552),
        ((-9400, 9), -28161),
        ((32584, 13), 0),
        ((9032, 10), 8192),
        ((27208, 9), -28672),
        ((19016, 13), 0),
        ((27208, 10), 8192),
        ((17224, 9), -28672),
        ((9032, 13), 0),
        ((840, 10), 8192),
    ],
)
def test_paranoid_RandomHelper_rotl(input, expected_result):
    assert RandomHelper.rotl(*input).view(np.int16) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (2366240958, -603972440),
        (-603972440, -10840),
        (-10840, 41400733302600),
        (14428438344, 18997177240136),
        (361314142792, -41471667330232),
        (-281195266956472, -84352620795320),
    ],
)
def test_paranoid_RandomHelper_next(input, expected_result):
    assert RandomHelper.next(input).view(np.int64) == expected_result


@pytest.fixture
def paranoid_obfuscated_chunks():
    return ["\u0003foo\u0003bar"]


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (0, b"foo"),
        (17179869184, b"bar"),
    ],
)
def test_paranoid_DeobfuscatorHelper_getString(paranoid_obfuscated_chunks, input, expected_result):
    assert DeobfuscatorHelper.getString(input, paranoid_obfuscated_chunks) == expected_result


# TODO: add tests for ParanoidSmaliParser
