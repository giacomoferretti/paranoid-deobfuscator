> [!WARNING]  
> Currently not working on Windows. Please use WSL or a Linux VM. See [#14](https://github.com/giacomoferretti/paranoid-deobfuscator/issues/14).


# Paranoid/LSParanoid deobfuscator

![PyPI - Version](https://img.shields.io/pypi/v/paranoid-deobfuscator)

> [!NOTE]  
> Only compatible with Paranoid v0.3.0+ (released in 25 Jan 2020)
> 
A script to deobfuscate apps obfuscated with [Paranoid]/[LSParanoid] to help you with static analysis.

|            Before             |            After            |
| :---------------------------: | :-------------------------: |
| ![Before](.assets/before.png) | ![After](.assets/after.png) |

## Installation

### Using pip

`pip install paranoid-deobfuscator`

### Manual

1. `git clone https://github.com/giacomoferretti/paranoid-deobfuscator`
2. `cd paranoid-deobfuscator`
3. `pip install .`

## Usage

### APK file (using [Apktool])

1. Decode `.apk` file: `apktool d app.apk`
2. Run deobfuscator: `python -m paranoid_deobfuscator app` <!-- `paranoid-deobfuscator app` (or `python -m paranoid_deobfuscator app`) -->
3. Build: `apktool b app`
4. Enjoy your deobfuscated apk!

### DEX file (using [smali])

1. Disassemble `.dex` file: `baksmali d classes.dex`
2. Run deobfuscator: `python -m paranoid_deobfuscator out` <!-- `paranoid-deobfuscator out` (or `python -m paranoid_deobfuscator out`) -->
3. Assemble: `smali a out`
4. Enjoy your deobfuscated dex!

[paranoid]: https://github.com/MichaelRocks/paranoid
[lsparanoid]: https://github.com/LSPosed/LSParanoid
[apktool]: https://github.com/iBotPeaches/Apktool
[smali]: https://github.com/google/smali
