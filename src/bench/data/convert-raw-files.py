#!/usr/bin/env python3
# Copyright (c) 2019 The Bitcoin Core developers
# Copyright (c) 2019-2020 The Bitcoin developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from glob import glob
from os.path import basename

names_raw = glob("*.raw")
print("Found " + str(len(names_raw)) + " .raw file(s) in working directory")
names_raw.sort()

names = []

for name_raw in names_raw:

    name = name_raw[:-4]
    name_cpp = name + ".cpp"
    name = basename(name)

    with open(name_raw, "rb") as file_raw, open(name_cpp, "w") as file_cpp:

        print("Converting " + name_raw + " to " + name_cpp + " ...")
        contents = file_raw.read()

        file_cpp.write("// DO NOT EDIT THIS FILE - it is machine-generated, use convert-raw-files.py to regenerate\n")
        file_cpp.write("\n")
        file_cpp.write("#include <cstdint>\n")
        file_cpp.write("#include <vector>\n")
        file_cpp.write("\n")
        code = "static const unsigned char raw[] = \""
        prevX = -1
        for i in range(len(contents)):
            x = contents[i]
            # We use short escape sequences for control characters that have one.
            if x == 0x07:
                code += "\\a"
            elif x == 0x08:
                code += "\\b"
            elif x == 0x09:
                code += "\\t"
            elif x == 0x0a:
                code += "\\n"
            elif x == 0x0b:
                code += "\\v"
            elif x == 0x0c:
                code += "\\f"
            elif x == 0x0d:
                code += "\\r"
            # To avoid ending the C++ string, we escape quotation marks.
            elif x == 0x22:
                code += "\\\""
            # To avoid formation of unintended escape sequences, we escape backslashes.
            elif x == 0x5c:
                code += "\\\\"
            # To avoid C++ trigraph formation, we escape a question mark if the previous character was also a question mark.
            elif prevX == 0x3f and x == 0x3f:
                code += "\\?"
            # We display a character unescaped if it is ASCII, and not a control character.
            elif x >= 0x20 and x < 0x7f:
                code += chr(x)
            else:
                # This character can be omitted if it is the last character and it is null,
                # since we are allowed to read the terminating null added by the C++ compiler.
                last = i+1 == len(contents)
                if not last or x > 0x00:
                    # We use octal escape sequences for the rest, which have a length limit of three octal digits.
                    # One or two leading zeros in octal sequences can be omitted if the next character is not a digit.
                    # If the next character is a digit, it is cheaper to use all three octal digits here,
                    # than to escape the next character as well.
                    octalAbbr = last or contents[i+1] < 0x30 or contents[i+1] >= 0x3a
                    if octalAbbr and x < 0x08:
                        code += "\\" + str(x)
                    elif octalAbbr and x < 0x20:
                        code += "\\" + str(x // 8) + str(x % 8)
                    else:
                        code += "\\" + str(x // 64) + str(x // 8 % 8) + str(x % 8)
            prevX = x
        code += "\";\n"
        file_cpp.write(code)
        file_cpp.write("\n")
        file_cpp.write("namespace benchmark {\n")
        file_cpp.write("namespace data {\n")
        file_cpp.write("\n")
        file_cpp.write("extern const std::vector<uint8_t> " + name + "(raw, raw + " + str(len(contents)) + ");\n")
        file_cpp.write("\n")
        file_cpp.write("} // namespace data\n")
        file_cpp.write("} // namespace benchmark\n")

    names.append(name)

if len(names):

    name_h = "../data.h"

    with open(name_h, "w") as file_h:

        print("Writing " + str(len(names)) + " declaration(s) to " + name_h + " ...")

        file_h.write("// DO NOT EDIT THIS FILE - it is machine-generated, use data/convert-raw-files.py to regenerate\n")
        file_h.write("\n")
        file_h.write("#ifndef BITCOIN_BENCH_DATA_H\n")
        file_h.write("#define BITCOIN_BENCH_DATA_H\n")
        file_h.write("\n")
        file_h.write("#include <cstdint>\n")
        file_h.write("#include <vector>\n")
        file_h.write("\n")
        file_h.write("namespace benchmark {\n")
        file_h.write("namespace data {\n")
        file_h.write("\n")
        for name in names:
            file_h.write("extern const std::vector<uint8_t> " + name + ";\n")
        file_h.write("\n")
        file_h.write("} // namespace data\n")
        file_h.write("} // namespace benchmark\n")
        file_h.write("\n")
        file_h.write("#endif // BITCOIN_BENCH_DATA_H\n")

    print("Done")

