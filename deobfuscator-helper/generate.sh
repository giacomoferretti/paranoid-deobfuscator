#!/usr/bin/env bash

rm deobfuscator.jar
rm -fr out
javac -cp src/ $(find src -iname "*.java") -d out -classpath libs/commons-lang3-3.12.0.jar -classpath libs/commons-text-1.9.jar -Xlint:deprecation
unzip -o libs/commons-text-1.9.jar -d out
unzip -o libs/commons-lang3-3.12.0.jar -d out
jar -cvmf manifest.mf deobfuscator.jar -C out .
mv deobfuscator.jar ..
