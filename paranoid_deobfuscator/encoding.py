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


from typing import List


def decode_unicode(data: str):
    """
    Decodes a string containing Unicode escape sequences into its corresponding Unicode characters.

    Args:
        data (str): The input string containing Unicode escape sequences.

    Returns:
        str: The decoded string with Unicode characters.

    Examples:
        >>> decode_unicode("\\\\u30b9\\\\u30fc\\\\u30ab")
        "\u30b9\u30fc\u30ab"
    """
    return data.encode().decode("unicode-escape")


def encode_unicode(data: str):
    """
    Encodes a string into a Unicode escape sequence.

    Args:
        data (str): The input string to be encoded.

    Returns:
        str: The encoded string with Unicode escape sequences.

    Examples:
        >>> encode_unicode("\u30b9\u30fc\u30ab")
        "\\\\u30b9\\\\u30fc\\\\u30ab"
    """
    return data.encode("unicode-escape").decode()


def decode_unicode_chunks(chunks: List[str]):
    """
    Decodes a list of Unicode-encoded strings.

    Args:
        chunks (List[str]): A list of Unicode-encoded strings.

    Returns:
        List[str]: A list of decoded strings.

    Examples:
        >>> decode_unicode_chunks(["\\\\u30b9\\\\u30fc\\\\u30ab"])
        ["\u30b9\u30fc\u30ab"]
    """
    return [decode_unicode(chunk) for chunk in chunks]


def encode_smali_string(data: str | bytes):
    """
    Encodes a given string or bytes into a format suitable for Smali.

    This function takes a string or bytes, converts it to a Unicode string if necessary,
    and then replaces certain characters to ensure the string is properly escaped for Smali.
    Specifically, it replaces double quotes with escaped double quotes, single quotes with
    escaped single quotes, and hexadecimal byte sequences with Unicode escape sequences.

    Args:
        data (str | bytes): The input data to be encoded. It can be either a string or bytes.

    Returns:
        str: The encoded string, with special characters properly escaped for Smali.

    Examples:
        >>> encode_smali_string("\\b")
        "\\\\u0008"
        >>> encode_smali_string(b"test\\"'")
        "test\\\\\\"\\\\'"
    """
    data = data if isinstance(data, str) else bytes(data).decode()
    return encode_unicode(data).replace('"', '\\"').replace("'", "\\'").replace("\\x", "\\u00")
