# Copyright 2025 Giacomo Ferretti
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

import pytest

from paranoid_deobfuscator.smali import SmaliField
from paranoid_deobfuscator.smali.instructions import (
    SmaliInstrInvokeStatic,
    SmaliInstrInvokeStaticRange,
    SmaliInstrSGetSPut,
)


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            ".field public static final ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ:[Ljava/lang/String;",
            SmaliField("ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ", "[Ljava/lang/String;", ["public", "static", "final"]),
        ),
    ],
)
def test_valid_SmaliField_from_string(input, expected_result):
    assert SmaliField.from_string(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "sput-object v2, LGs;->ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ:[Ljava/lang/String;",
            SmaliInstrSGetSPut("v2", "LGs;", "ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ", "[Ljava/lang/String;"),
        ),
        (
            "sget-object v0, LGs;->ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ:[Ljava/lang/String;",
            SmaliInstrSGetSPut("v0", "LGs;", "ہ٢ٶڽڦؤۗٹلٛٴۨؕڢيٿڷۻچٴڄ٣٘ێڰٓۈئٱ٦ڀآپۆٗۜشٍٝڐۡدړ٦ٌۭٙلڌؿ", "[Ljava/lang/String;"),
        ),
    ],
)
def test_valid_SmaliInstrSGetSPut_parse(input, expected_result):
    assert SmaliInstrSGetSPut.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "invoke-static/range {v0 .. v1}, LGs;->l(J)Ljava/lang/String;",
            SmaliInstrInvokeStaticRange(
                ["v0", "v1"],
                "LGs;",
                "l(J)Ljava/lang/String;",
            ),
        ),
    ],
)
def test_valid_SmaliInstrInvokeStaticRange_parse(input, expected_result):
    assert SmaliInstrInvokeStaticRange.parse(input) == expected_result
