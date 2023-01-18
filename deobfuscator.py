#!/usr/bin/env python3

import argparse
import base64
import collections
import os
import re
import subprocess
import sys


class ParanoidDeobfuscator:
    def __init__(self):
        pass

    def _is_correct_encrypted_string(self, string):
        # Minimun count of \\u is 2
        if string.count("\\u") < 2:
            return False

        return True

    def search_encrypted_strings(self, file):
        strings = []

        regex = re.compile(r"const-string\s+[vp][0-9]+,\s+\"((?:\\u[0-9a-f]{4})+?)\"")

        with open(file) as f:
            for line in f:
                match = regex.search(line)
                if match and self._is_correct_encrypted_string(match.group(1)):
                    strings.append(match.group(1))

        return strings

    def _common_locations(self, path):
        for folder in os.listdir(path):
            # Check if is in a smali folder
            if not folder.startswith("smali"):
                continue

            verboseprint("Searching in {}...".format(os.path.join(path, folder)))

            target_folder = os.path.join(path, folder, "io", "michaelrocks", "paranoid")
            if os.path.isdir(target_folder):
                verboseprint("Found {}".format(target_folder))
                for file in os.listdir(target_folder):
                    if not file.startswith("Deobfuscator") or not file.endswith(".smali"):
                        continue

                    verboseprint(" - {}".format(file))

                    encrypted_strings = self.search_encrypted_strings(
                        os.path.join(target_folder, file)
                    )

                    verboseprint("   - {}".format(encrypted_strings))

                    if encrypted_strings:
                        verboseprint("Found {}".format(encrypted_strings))
                        return (os.path.join(target_folder, file), encrypted_strings)

        return (None, None)

    def search_deobfuscator_class(self, path):
        # Search for common locations
        # common = self._common_locations(path)
        # if common[0] != None and common[1] != None:
        #     return common

        for root, _, filenames in os.walk(path):
            # Check if is in a smali folder
            if not root.startswith(os.path.join(path, "smali")):
                continue

            for filename in filenames:
                verboseprint(" - {}".format(filename))
                encrypted_strings = self.search_encrypted_strings(os.path.join(root, filename))
                if encrypted_strings:
                    # verboseprint('Found {}'.format(encrypted_strings))
                    if self.get_deobfuscator_signature(os.path.join(root, filename)):
                        return (os.path.join(root, filename), encrypted_strings)

        return (None, None)

    def get_deobfuscator_signature(self, file):
        regex = re.compile(r"\.method\s+public\s+static\s+(\w+)\(J\)Ljava/lang/String;")

        with open(file) as f:
            for line in f:
                match = regex.search(line)
                if match:
                    method = "{}(J)Ljava/lang/String;".format(match.group(1))
                    method_class = file.split("smali")[1].split(os.sep, 1)[1][:-1]
                    method_class = method_class.replace("\\", "/")
                    signature = "L{};->{}".format(method_class, method)

                    verboseprint("Found {}".format(signature))

                    return signature

        return None


def main(args):
    path = args.folder
    if not os.path.isdir(path):
        print("Target folder not found. Exiting...", file=sys.stderr)
        sys.exit(1)

    deobfuscator = ParanoidDeobfuscator()

    # Search class
    verboseprint("Searching DeobfuscatorHelper class...")
    deobfuscator_class, encrypted_strings = deobfuscator.search_deobfuscator_class(path)

    if not deobfuscator_class:
        sys.exit(1)

    # Search signature
    verboseprint("Extracting getString signature...")
    signature = deobfuscator.get_deobfuscator_signature(deobfuscator_class)

    if not deobfuscator_class or len(encrypted_strings) < 1 or not signature:
        print("Paranoid was not found. Exiting...", file=sys.stderr)
        sys.exit(1)

    # Extract numbers
    verboseprint("Searching for decryption numbers...")

    for root, _, filenames in os.walk(path):
        # Check if is in a smali folder
        if not root.startswith(os.path.join(path, "smali")):
            continue

        for filename in filenames:

            # TODO: SEPARATE FUNCTION - Process file
            with open(os.path.join(root, filename)) as f:
                data = f.readlines()
            # Increase buffer size
            buffer = collections.deque(3 * [""], 3)

            identifier = None
            temp_output = None

            for line_num, line in enumerate(data):

                # Found deobfuscation method
                if signature in line:
                    verboseprint(os.path.join(root, filename))
                    verboseprint("Found {}".format(line.strip()))
                    # verboseprint(encrypted_strings)

                    # Get identifier
                    match = re.search(r"invoke-static\s+{([vp][0-9]+),", line)
                    if match:
                        verboseprint(os.path.join(root, filename))
                        identifier = match.group(1)
                        verboseprint("Identifier: {}".format(identifier))

                        # Search for deobfuscation number
                        regex = re.compile(
                            r"const-wide[/hig1632]*\s+" + identifier + r",\s+([-]*0x[a-f0-9]+)L*"
                        )
                        for previous in reversed(buffer):
                            match = regex.search(previous)
                            if match:
                                number = int(match.group(1), 16)
                                verboseprint("Number: {}".format(number))

                                # print(['java', '-jar', 'deobfuscator.jar', '{}'.format(number), *encrypted_strings])

                                p = subprocess.Popen(
                                    [
                                        "java",
                                        "-jar",
                                        "deobfuscator.jar",
                                        "{}".format(number),
                                        *encrypted_strings,
                                    ],
                                    stdout=subprocess.PIPE,
                                )
                                response = p.communicate()[0]

                                print(response)

                                if args.output:
                                    with open(args.output, "a") as out:
                                        verboseprint(response)
                                        out.write(response.decode())
                                        out.write("\n")

                                temp_output = response.decode()
                                # Otherwise it might complain
                                break

                # We previously deobfuscated a string, replace it
                if temp_output:
                    match = re.search(r"move-result-object\s+([vp][0-9]+)", line)
                    if match:
                        data[line_num] = '{}const-string {}, "{}"{}'.format(
                            data[line_num][: match.span()[0]],
                            match.group(1),
                            temp_output,
                            data[line_num][match.span()[1] :],
                        )
                        temp_output = None
                # Ignore empty lines --> not gonna get anything
                if line.strip() != "":
                    buffer.append(line)

            with open(os.path.join(root, filename), "w") as f:
                f.writelines(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deobfuscate paranoid string encryption.")
    parser.add_argument(
        "folder", help="input folder generated with apktool", type=str, metavar="<folder>"
    )
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-o", "--output", nargs="?", help="output file containing strings")
    args = parser.parse_args()

    if args.verbose:

        def verboseprint(*args, **kwargs):
            print(*args, **kwargs)

    else:
        verboseprint = lambda *a, **k: None

    main(args)
