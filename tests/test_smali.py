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

import pytest

from paranoid_deobfuscator.smali import SmaliField, SmaliMethod
from paranoid_deobfuscator.smali.instructions import (
    SmaliInstrAGetAPut,
    SmaliInstrConst,
    SmaliInstrConstString,
    SmaliInstrInvokeStatic,
    SmaliInstrInvokeStaticRange,
    SmaliInstrMoveResult,
    SmaliInstrNewArray,
    SmaliInstrSGetSPut,
)


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            ".method public static d(Lp/e;Ln/d;Ljava/util/ArrayList;I)V",
            SmaliMethod(
                "d",
                arguments=["Lp/e;", "Ln/d;", "Ljava/util/ArrayList;", "I"],
                return_type="V",
                modifiers=["public", "static"],
                class_name=None,
            ),
        ),
        (
            ".method test([Ljava/lang/String;[[[[I)V",
            SmaliMethod(
                "test",
                arguments=["[Ljava/lang/String;", "[[[[I"],
                return_type="V",
                modifiers=[],
                class_name=None,
            ),
        ),
    ],
)
def test_valid_SmaliMethod_from_string(input, expected_result):
    assert SmaliMethod.from_string(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            SmaliMethod(
                "d",
                arguments=["Lp/e;", "Ln/d;", "Ljava/util/ArrayList;", "I"],
                return_type="V",
                modifiers=["public", "static"],
                class_name=None,
            ),
            ".method public static d(Lp/e;Ln/d;Ljava/util/ArrayList;I)V",
        ),
    ],
)
def test_valid_SmaliMethod_to_smali(input, expected_result):
    assert input.to_smali() == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            ".field public static final A:[I",
            SmaliField("A", "[I", ["public", "static", "final"]),
        ),
        (
            ".field public static final F:[Ljava/lang/String;",
            SmaliField("F", "[Ljava/lang/String;", ["public", "static", "final"]),
        ),
        (
            ".field public static final H:[Ljava/lang/Object;",
            SmaliField("H", "[Ljava/lang/Object;", ["public", "static", "final"]),
        ),
        (
            ".field public static Q:Ljava/lang/reflect/Method;",
            SmaliField("Q", "Ljava/lang/reflect/Method;", ["public", "static"]),
        ),
        (
            ".field public static R:Z",
            SmaliField("R", "Z", ["public", "static"]),
        ),
        (
            ".field public static S:Ljava/lang/reflect/Field;",
            SmaliField("S", "Ljava/lang/reflect/Field;", ["public", "static"]),
        ),
        (
            ".field public static final b:[I",
            SmaliField("b", "[I", ["public", "static", "final"]),
        ),
        (
            ".field public static d:Ljava/lang/reflect/Field; = null",
            SmaliField("d", "Ljava/lang/reflect/Field;", ["public", "static"], init_value="null"),
        ),
        (
            ".field public static e:Z = false",
            SmaliField("e", "Z", ["public", "static"], init_value="false"),
        ),
    ],
)
def test_valid_SmaliField_from_string(input, expected_result):
    assert SmaliField.from_string(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            SmaliField("A", "[I", ["public", "static", "final"]),
            ".field public static final A:[I",
        ),
        (
            SmaliField("F", "[Ljava/lang/String;", ["public", "static", "final"]),
            ".field public static final F:[Ljava/lang/String;",
        ),
        (
            SmaliField("H", "[Ljava/lang/Object;", ["public", "static", "final"]),
            ".field public static final H:[Ljava/lang/Object;",
        ),
        (
            SmaliField("Q", "Ljava/lang/reflect/Method;", ["public", "static"]),
            ".field public static Q:Ljava/lang/reflect/Method;",
        ),
        (
            SmaliField("R", "Z", ["public", "static"]),
            ".field public static R:Z",
        ),
        (
            SmaliField("S", "Ljava/lang/reflect/Field;", ["public", "static"]),
            ".field public static S:Ljava/lang/reflect/Field;",
        ),
        (
            SmaliField("b", "[I", ["public", "static", "final"]),
            ".field public static final b:[I",
        ),
        (
            SmaliField("d", "Ljava/lang/reflect/Field;", ["public", "static"], init_value="null"),
            ".field public static d:Ljava/lang/reflect/Field; = null",
        ),
        (
            SmaliField("e", "Z", ["public", "static"], init_value="false"),
            ".field public static e:Z = false",
        ),
    ],
)
def test_valid_SmaliField_to_smali(input, expected_result):
    assert input.to_smali() == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ("const/4 v0, 0x0", SmaliInstrConst("v0", 0)),
        ("const/16 v3, 0x1", SmaliInstrConst("v3", 1)),
        ("const v0, 0x2", SmaliInstrConst("v0", 2)),
        ("const/high16 v0, -0x100", SmaliInstrConst("v0", -0x100)),
        ("const-wide/16 v0, -0x4cL", SmaliInstrConst("v0", -0x4C)),
        ("const-wide/32 p0, 0x0L", SmaliInstrConst("p0", 0)),
        ("const-wide v2, 0x4fc200000000L", SmaliInstrConst("v2", 0x4FC200000000)),
        ("const-wide/high16 v0, 0x0L", SmaliInstrConst("v0", 0)),
    ],
)
def test_valid_SmaliInstrConst_parse(input, expected_result):
    assert SmaliInstrConst.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            'const-string v0, "\\u001dThis should not be obfuscated\\u0003TAG\\u0014\\u30b9\\u30fc\\u30ab\\ud83c\\udf49\\u30b9\\u30fc\\u30ab\\t\\u0008\\n\\r\\u000c\\\'\\"\\\\\\u0000\\u0001\\u0002\\u0003\\u0003TAG\\u0080\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\u0008\\t\\n\\u000b\\u000c\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\"#$%&\\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f\\u0003TAG\\u0080\\u0080\\u0081\\u0082\\u0083\\u0084\\u0085\\u0086\\u0087\\u0088\\u0089\\u008a\\u008b\\u008c\\u008d\\u008e\\u008f\\u0090\\u0091\\u0092\\u0093\\u0094\\u0095\\u0096\\u0097\\u0098\\u0099\\u009a\\u009b\\u009c\\u009d\\u009e\\u009f\\u00a0\\u00a1\\u00a2\\u00a3\\u00a4\\u00a5\\u00a6\\u00a7\\u00a8\\u00a9\\u00aa\\u00ab\\u00ac\\u00ad\\u00ae\\u00af\\u00b0\\u00b1\\u00b2\\u00b3\\u00b4\\u00b5\\u00b6\\u00b7\\u00b8\\u00b9\\u00ba\\u00bb\\u00bc\\u00bd\\u00be\\u00bf\\u00c0\\u00c1\\u00c2\\u00c3\\u00c4\\u00c5\\u00c6\\u00c7\\u00c8\\u00c9\\u00ca\\u00cb\\u00cc\\u00cd\\u00ce\\u00cf\\u00d0\\u00d1\\u00d2\\u00d3\\u00d4\\u00d5\\u00d6\\u00d7\\u00d8\\u00d9\\u00da\\u00db\\u00dc\\u00dd\\u00de\\u00df\\u00e0\\u00e1\\u00e2\\u00e3\\u00e4\\u00e5\\u00e6\\u00e7\\u00e8\\u00e9\\u00ea\\u00eb\\u00ec\\u00ed\\u00ee\\u00ef\\u00f0\\u00f1\\u00f2\\u00f3\\u00f4\\u00f5\\u00f6\\u00f7\\u00f8\\u00f9\\u00fa\\u00fb\\u00fc\\u00fd\\u00fe\\u00ff"',
            SmaliInstrConstString(
                "v0",
                "\\u001dThis should not be obfuscated\\u0003TAG\\u0014\\u30b9\\u30fc\\u30ab\\ud83c\\udf49\\u30b9\\u30fc\\u30ab\\t\\u0008\\n\\r\\u000c\\'\\\"\\\\\\u0000\\u0001\\u0002\\u0003\\u0003TAG\\u0080\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\u0008\\t\\n\\u000b\\u000c\\r\\u000e\\u000f\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f !\\\"#$%&\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\u007f\\u0003TAG\\u0080\\u0080\\u0081\\u0082\\u0083\\u0084\\u0085\\u0086\\u0087\\u0088\\u0089\\u008a\\u008b\\u008c\\u008d\\u008e\\u008f\\u0090\\u0091\\u0092\\u0093\\u0094\\u0095\\u0096\\u0097\\u0098\\u0099\\u009a\\u009b\\u009c\\u009d\\u009e\\u009f\\u00a0\\u00a1\\u00a2\\u00a3\\u00a4\\u00a5\\u00a6\\u00a7\\u00a8\\u00a9\\u00aa\\u00ab\\u00ac\\u00ad\\u00ae\\u00af\\u00b0\\u00b1\\u00b2\\u00b3\\u00b4\\u00b5\\u00b6\\u00b7\\u00b8\\u00b9\\u00ba\\u00bb\\u00bc\\u00bd\\u00be\\u00bf\\u00c0\\u00c1\\u00c2\\u00c3\\u00c4\\u00c5\\u00c6\\u00c7\\u00c8\\u00c9\\u00ca\\u00cb\\u00cc\\u00cd\\u00ce\\u00cf\\u00d0\\u00d1\\u00d2\\u00d3\\u00d4\\u00d5\\u00d6\\u00d7\\u00d8\\u00d9\\u00da\\u00db\\u00dc\\u00dd\\u00de\\u00df\\u00e0\\u00e1\\u00e2\\u00e3\\u00e4\\u00e5\\u00e6\\u00e7\\u00e8\\u00e9\\u00ea\\u00eb\\u00ec\\u00ed\\u00ee\\u00ef\\u00f0\\u00f1\\u00f2\\u00f3\\u00f4\\u00f5\\u00f6\\u00f7\\u00f8\\u00f9\\u00fa\\u00fb\\u00fc\\u00fd\\u00fe\\u00ff",
            ),
        ),
        (
            'const-string v2, "WrappedDrawableApi21"',
            SmaliInstrConstString("v2", "WrappedDrawableApi21"),
        ),
        (
            'const-string v3, "Error calling Drawable#isProjected() method"',
            SmaliInstrConstString("v3", "Error calling Drawable#isProjected() method"),
        ),
    ],
)
def test_valid_SmaliInstrConstString_parse(input, expected_result):
    assert SmaliInstrConstString.parse(input) == expected_result


# SmaliInstrInvokeStatic, SmaliInstrSGetSPut, SmaliInstrMoveResult
@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "new-array v2, v0, [Landroidx/appcompat/view/menu/b$d;",
            SmaliInstrNewArray("v2", "v0", "[Landroidx/appcompat/view/menu/b$d;"),
        ),
        (
            "new-array v5, v2, [Ljava/lang/Class;",
            SmaliInstrNewArray("v5", "v2", "[Ljava/lang/Class;"),
        ),
        (
            "new-array p2, p2, [Ljava/lang/CharSequence;",
            SmaliInstrNewArray("p2", "p2", "[Ljava/lang/CharSequence;"),
        ),
    ],
)
def test_valid_SmaliInstrNewArray_parse(input, expected_result):
    assert SmaliInstrNewArray.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ("aget v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-object v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-wide v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-boolean v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-byte v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-char v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aget-short v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-object v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-wide v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-boolean v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-byte v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-char v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
        ("aput-short v0, v1, v2", SmaliInstrAGetAPut("v0", "v1", "v2")),
    ],
)
def test_valid_SmaliInstrAGetAPut_parse(input, expected_result):
    assert SmaliInstrAGetAPut.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        ("move-result v0", SmaliInstrMoveResult("v0")),
        ("move-result-wide v0", SmaliInstrMoveResult("v0")),
        ("move-result-object v0", SmaliInstrMoveResult("v0")),
    ],
)
def test_valid_SmaliInstrMoveResult_parse(input, expected_result):
    assert SmaliInstrMoveResult.parse(input) == expected_result


# sget-boolean v0, La0/a;->d:Z
# sget-object v0, La0/a;->c:Ljava/lang/reflect/Method;
# sput-object v3, La0/a;->c:Ljava/lang/reflect/Method;
# sput-boolean v0, La0/a;->d:Z
# sput p1, Landroidx/activity/ImmLeaksCleaner;->b:I
# sput-wide v4, Lv0/a;->a:J


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "sget v0, Landroid/os/Build$VERSION;->SDK_INT:I",
            SmaliInstrSGetSPut("v0", "Landroid/os/Build$VERSION;", "SDK_INT", "I"),
        ),
        (
            "sget-boolean v0, La0/a;->d:Z",
            SmaliInstrSGetSPut("v0", "La0/a;", "d", "Z"),
        ),
        (
            "sget-object v0, La0/a;->c:Ljava/lang/reflect/Method;",
            SmaliInstrSGetSPut("v0", "La0/a;", "c", "Ljava/lang/reflect/Method;"),
        ),
        (
            "sput-object v3, La0/a;->c:Ljava/lang/reflect/Method;",
            SmaliInstrSGetSPut("v3", "La0/a;", "c", "Ljava/lang/reflect/Method;"),
        ),
        (
            "sput-boolean v0, La0/a;->d:Z",
            SmaliInstrSGetSPut("v0", "La0/a;", "d", "Z"),
        ),
        (
            "sput p1, Landroidx/activity/ImmLeaksCleaner;->b:I",
            SmaliInstrSGetSPut("p1", "Landroidx/activity/ImmLeaksCleaner;", "b", "I"),
        ),
        (
            "sput-wide v4, Lv0/a;->a:J",
            SmaliInstrSGetSPut("v4", "Lv0/a;", "a", "J"),
        ),
    ],
)
def test_valid_SmaliInstrSGetSPut_parse(input, expected_result):
    assert SmaliInstrSGetSPut.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "invoke-static {v1, v4, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I",
            SmaliInstrInvokeStatic(
                ["v1", "v4", "v3"],
                "Landroid/util/Log;",
                "i(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I",
            ),
        ),
        (
            "invoke-static{p0,p1},La;->a(J)Ljava/lang/String;",
            SmaliInstrInvokeStatic(["p0", "p1"], "La;", "a(J)Ljava/lang/String;"),
        ),
    ],
)
def test_valid_SmaliInstrInvokeStatic_parse(input, expected_result):
    assert SmaliInstrInvokeStatic.parse(input) == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "invoke-static/range {v0 .. v1}, Ltest;->test(J)V",
            SmaliInstrInvokeStaticRange(
                ["v0", "v1"],
                "Ltest;",
                "test(J)V",
            ),
        ),
        (
            "invoke-static/range{v0..v1},Ltest;->test(J)V",
            SmaliInstrInvokeStaticRange(
                ["v0", "v1"],
                "Ltest;",
                "test(J)V",
            ),
        ),
    ],
)
def test_valid_SmaliInstrInvokeStaticRange_parse(input, expected_result):
    assert SmaliInstrInvokeStaticRange.parse(input) == expected_result
