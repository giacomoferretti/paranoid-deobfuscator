# [Paranoid] deobfuscator

A simple script to deobfuscate apps obfuscated with [Paranoid].

## Prerequisites
* [Apktool]
* Java 1.8+
* Python 3

## Usage
1. Decode app with [Apktool]: `apktool d app.apk`
2. Run deobfuscator: `python deobfuscator.py app` or `./deobfuscator.py app`
3. Build app with [Apktool]: `apktool b app`
4. Enjoy your deobfuscated apk!

[paranoid]: https://github.com/MichaelRocks/paranoid
[apktool]: https://github.com/iBotPeaches/Apktool