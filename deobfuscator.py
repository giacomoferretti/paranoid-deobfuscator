#!/usr/bin/env python3

import os
import re
import sys
import argparse
import subprocess


def search_encrypted_string(file):
    regex = re.compile(r'const-string\s+[vp][0-9]+,\s+\"(.+?)\"')

    with open(file) as f:
        for line in f:
            match = regex.search(line)
            if match:
                encrypted_string = match.group(1)

                # TODO: Improve check
                if encrypted_string.startswith('\\u'):
                    if len(encrypted_string) % encrypted_string.count('\\u') == 0:
                        return encrypted_string

    return None


def search_deobfuscator_class(path):
    # Common locations
    for folder in os.listdir(path):
        # Check if is in a smali folder
        if not folder.startswith('smali'):
            continue

        target_folder = os.path.join(path, folder, 'io', 'michaelrocks', 'paranoid')
        if os.path.isdir(target_folder):
            for file in os.listdir(target_folder):
                if not file.startswith('Deobfuscator') or not file.endswith('.smali'):
                    continue

                encrypted_string = search_encrypted_string(os.path.join(target_folder, file))
                if encrypted_string:
                    return (os.path.join(target_folder, file), encrypted_string)


    for root, _, filenames in os.walk(path):
        # Check if is in a smali folder
        if not root.startswith(os.path.join(path, 'smali')):
            continue

        for filename in filenames:
            encrypted_string = search_encrypted_string(os.path.join(root, filename))
            if encrypted_string:
                return (os.path.join(root, filename), encrypted_string)

    return (None, None)


def get_deobfuscator_signature(base_folder, file):
    # Strip base folder
    target = file[len(base_folder):]

    with open(file) as f:
        data = f.read()
        m = re.search(r'\.method\s+public\s+static\s+(\w+)\(J\)Ljava/lang/String;', data)
        if m:
            method = '{}(J)Ljava/lang/String;'.format(m.group(1))

            # Remove smali folder
            method_class = os.path.splitext('/'.join(target.split(os.sep)[1:]))[0]

            return 'L{};->{}'.format(method_class, method)

    return None


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield (i, i+len(p), s[i:i+len(p)])
        i = s.find(p, i+1)


def insert_at(original, string, index):
    return original[:index] + string + original[index:]


def main(args):
    path = args.folder
    if not os.path.isdir(path):
        print('target folder not found. Exiting...', file=sys.stderr)
        exit(1)

    # Search class
    print('Searching DeobfuscatorHelper class...')
    deobfuscator_class, encrypted_string = search_deobfuscator_class(path)

    # Search deobfuscator signature
    print('Extract getString signature...')
    signature = get_deobfuscator_signature(path, deobfuscator_class)

    if not deobfuscator_class or not encrypted_string or not signature:
        print('Paranoid was not found. Exiting...', file=sys.stderr)
        exit(1)

    # Extract numbers
    print('Searching for decryption numbers...')
    regex = re.compile(r'const-wide[/hig1632]*\s+([vp][0-9]+),\s+([-]*0x[a-f0-9]+)L*')
    for root, _, filenames in os.walk(path):
        if root.startswith(os.path.join(path, 'smali')):
            for filename in filenames:
                #print(os.path.join(root, filename))
                with open(os.path.join(root, filename), 'r+') as f:
                    data = f.read()

                    """print(os.path.join(root, filename))
                    try:
                        print(data.index(signature))
                    except:
                        continue"""

                    offset = 0
                    for i in findall(signature, data):
                        start, end, string = i

                        start += offset
                        end += offset

                        xxx = None
                        for xxx in regex.finditer(data[:start]):
                            pass

                        # Skip if not found
                        if not xxx:
                            continue

                        m = re.search(r'\A\s*move-result-object\s+([vp][0-9]+)', data[end:])
                        if not m:
                            continue

                        # Deobfuscate
                        num = int(xxx.group(2), 16)
                        print('Decrypting for {}...'.format(num))
                        p = subprocess.Popen(['java', '-jar', 'deobfuscator.jar', bytes(encrypted_string, 'ascii').decode('unicode-escape'), '{}'.format(num)], stdout=subprocess.PIPE)
                        response = p.communicate()[0].decode()

                        mmmmmmm = 'const-string {}, "{}"'.format(m.group(1), response)
                        offset += len(mmmmmmm)
                        data = insert_at(data, mmmmmmm, m.span()[1]+end)

                        offset -= (m.span()[1] + end) - xxx.span()[0]
                        data = data[:xxx.span()[0]] + data[m.span()[1] + end:]

                    f.seek(0)
                    f.write(data)
                    f.truncate()


if __name__ == '__main__':
    # Setup arguments
    parser = argparse.ArgumentParser(description='Deobfuscate paranoid string encryption.')
    parser.add_argument('folder', type=str, metavar='<folder>')
    main(parser.parse_args())
