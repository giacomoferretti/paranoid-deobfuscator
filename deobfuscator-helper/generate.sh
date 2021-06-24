#!/usr/bin/env bash

rm deobfuscator.jar
rm $(find . -iname "*.class")
javac $(find . -iname "*.java") && jar cmf manifest.mf deobfuscator.jar $(find . -iname "*.class") && mv deobfuscator.jar ..
