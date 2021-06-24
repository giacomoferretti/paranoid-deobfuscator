/*
 * Copyright 2020-2021 Giacomo Ferretti
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package me.hexile.paranoid.deobfuscator;

import java.util.Arrays;
import org.apache.commons.text.StringEscapeUtils;
import io.michaelrocks.paranoid.DeobfuscatorHelper;

public class Main {
    static final char[] HEX_DIGITS = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};

    public static String escapeSmali(CharSequence input) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);
            if (c == '\t') {
                out.append("\\t");
            } else if (c == '\n') {
                out.append("\\n");
            } else if (c == '\r') {
                out.append("\\r");
            } else if (c == '\"') {
                out.append("\\\"");
            } else if (c == '\'') {
                out.append("\\'");
            } else if (c == '\\') {
                out.append("\\\\");
            } else if (c < ' ' || c >= 127) {
                out.append("\\u");
                out.append(HEX_DIGITS[(c >> '\f') & 15]);
                out.append(HEX_DIGITS[(c >> '\b') & 15]);
                out.append(HEX_DIGITS[(c >> 4) & 15]);
                out.append(HEX_DIGITS[c & 15]);
            } else {
                out.append(c);
            }
        }
        return out.toString();
    }

    public static void main(String... args) {
        // Usage: java -jar main.jar NUMBER ARG1 ARG2 ARG3
        if (args.length < 2) {
            System.err.println("Wrong usage.");
            System.exit(1);
        }

        long number = Long.parseLong(args[0]);

        String[] chunks = Arrays.copyOfRange(args, 1, args.length);

        for (int i = 0; i < chunks.length; i++) {
            chunks[i] = StringEscapeUtils.unescapeJava(chunks[i]);
        }

        System.out.print(escapeSmali(DeobfuscatorHelper.getString(number, chunks)));
    }
}