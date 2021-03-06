# [Paranoid] deobfuscator

A script to deobfuscate apps obfuscated with [Paranoid]
to help you with static analysis.

Before | After
:-:|:-:
![Before](.assets/before.png) | ![After](.assets/after.png)

## Prerequisites
* [Apktool]
* Java 1.8+
* Python 3

## Usage
1. Decode app with [Apktool]: `apktool d app.apk`
2. Run deobfuscator: `python deobfuscator.py app` or `./deobfuscator.py app`
3. Build app with [Apktool]: `apktool b app`
4. Enjoy your deobfuscated apk!

## Build `deobfuscator.jar`
Run `generate.sh` inside the `deobfuscator-helper` folder.

[paranoid]: https://github.com/MichaelRocks/paranoid
[apktool]: https://github.com/iBotPeaches/Apktool