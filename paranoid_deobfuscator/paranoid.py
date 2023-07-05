import re
from typing import List

from .deobfuscator import DeobfuscatorHelper_getString

"""
const-wide v0, -0x123L

invoke-static {v0, v1}, Lorg/lsposed/lsparanoid/Deobfuscator;->getString(J)Ljava/lang/String;

move-result-object v0
"""

"""
const-string v0, "DEOBFUSCATED"
"""

MOVE_RESULT_OBJECT_REGEX = re.compile(r"move-result-object\s+([vp][0-9]+)")
CONST_STRING_REGEX = re.compile(r'const-string\s+[vp][0-9]+,\s+"((?:\\u[0-9a-f]{4})+)"')
CONST_WIDE_REGEX = re.compile(
    r"const-wide(?:/(?:high)?(?:16|32))?\s+([vp][0-9]+),\s+(-?0x[a-f0-9]+)L?"
)
INVOKE_STATIC_REGEX = re.compile(r"invoke-static\s+{([vp][0-9]+),\s+[vp][0-9]+},")
UTF16_REGEX = re.compile(r"^(?:\\u[0-9a-f]{4})+$")
# TODO: Match DEX SimpleName instead of \w
DEOBFUSCATOR_SIGNATURE_REGEX = re.compile(
    r"\.method\s+public\s+static\s+(\w+)\(J\)Ljava/lang/String;"
)


def is_encrypted_string(data: str):
    # Check if it's a UTF-16 string
    if not UTF16_REGEX.match(data):
        return False

    # Minimun count of \\u is 2
    if data.count("\\u") < 2:
        return False

    return True


def extract_obfuscated_strings(data: str):
    result = []

    for line in data.splitlines():
        line = line.strip()

        # Filter out lines
        if not line or not line.startswith("const-string"):
            continue

        m = CONST_STRING_REGEX.search(line)
        if m and is_encrypted_string(m.group(1)):
            result.append(m.group(1))

    return result


def extract_deobfuscator_method(data: str):
    """
    Search for this signature:

    Lorg/lsposed/lsparanoid/Deobfuscator;->getString(J)Ljava/lang/String;
    """

    for line in data.splitlines():
        # Filter out lines
        line = line.strip()
        if not line or not line.startswith(".method"):
            continue

        m = DEOBFUSCATOR_SIGNATURE_REGEX.search(line)
        if m:
            return "{}(J)Ljava/lang/String;".format(m.group(1))

    return None


def extract_identifier_from_invoke(line: str):
    m = INVOKE_STATIC_REGEX.search(line)
    if m:
        return m.group(1)


def deobfuscate_strings(data: str, signature: str, chunks: List[str]):
    result = []

    const_buffer = []

    for line_num, line in enumerate(data.splitlines()):
        # Filter out lines
        line = line.strip()
        if not line:
            continue

        # Clear buffer if end method
        if line == ".end method":
            const_buffer.clear()

        # Add long to buffer
        if line.startswith("const-wide"):
            m = CONST_WIDE_REGEX.search(line)
            if m:
                const_buffer.append((m.group(1), m.group(2)))

        # Check if calling deobfuscator method
        if signature in line:
            m = INVOKE_STATIC_REGEX.search(line)
            if m:
                identifier = m.group(1)
                for x in reversed(const_buffer):
                    if x[0] == identifier:
                        string_id = int(x[1], 16)
                        decoded = (
                            DeobfuscatorHelper_getString(string_id, chunks)
                            .decode()
                            .replace('"', '\\"')
                            .replace("'", "\\'")
                            .replace("\\x", "\\u00")
                        )
                        result.append((line_num, decoded))
                        break

    return result
