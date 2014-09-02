#!/usr/bin/env python3

import os
import re
import sys


CITE_KEY_RE = re.compile(r"\s*:CITE-KEY:(?:\s*(\w+)(-\d+)?)?", re.IGNORECASE)
PROPERTIES_RE = re.compile(r"(\s*):PROPERTIES:\s*", re.IGNORECASE)
END_RE = re.compile(r"\s*:END:\s*", re.IGNORECASE)
META_GENRE_RE = re.compile(r"\s*:genre:\s*(note|preface|section)\b", re.IGNORECASE)

cite_keys = {}


def skip_until_re(regex, lines, i, output):
    num_lines = len(lines)

    while i < num_lines and not regex.match(lines[i]):
        output.append(lines[i])
        i += 1

    return i


def parse(lines, start):
    output = []
    num_lines = len(lines)
    i = 0
    meta_count = 0

    # Scan until we find the first CITE-KEY
    i = skip_until_re(CITE_KEY_RE, lines, i, output)

    if i >= num_lines:
        print("ERROR: missing initial CITE-KEY")
        return output

    cite_key = CITE_KEY_RE.match(lines[i]).group(1)

    if cite_key not in cite_keys:
        cite_keys[cite_key] = start

    output.append(lines[i])
    i += 1

    # Now scan until we find :END:
    while i < num_lines:
        i = skip_until_re(PROPERTIES_RE, lines, i, output)

        if i >= num_lines:
            return output

        indent = PROPERTIES_RE.match(lines[i]).group(1)
        output.append(lines[i])
        i += 1
        have_meta = False
        have_end = False

        while i <= num_lines:
            line = lines[i]
            m = CITE_KEY_RE.match(line)

            if m:
                i += 1
                continue
            else:
                m = META_GENRE_RE.match(line)

                if m:
                    have_meta = True
                else:
                    m = END_RE.match(line)

                    if m:
                        # Insert next CITE-KEY
                        if have_meta:
                            meta_count += 1
                            cite_key_count = cite_keys[cite_key] + 1
                            fmt = "{}:cite-key: {}:{}e{}\n"
                        else:
                            cite_keys[cite_key] += 1
                            cite_key_count = cite_keys[cite_key]
                            meta_count = 0
                            fmt = "{}:cite-key: {}:{}\n"

                        output.append(fmt.format(indent, cite_key, cite_key_count, meta_count))
                        have_end = True

            output.append(line)
            i += 1

            if have_end:
                break

    return output


def main():
    start = 0
    path = None

    for i, arg in enumerate(sys.argv):
        if arg == "--start":
            start = max(int(sys.argv[i + 1]) - 1, 0)
        else:
            path = arg

    if not path:
        print("No path given!")
        sys.exit(1)

    root_path = os.path.realpath(os.path.expanduser(path))

    for root, dirs, files in os.walk(root_path):
        for filename in [filename for filename in files if filename.endswith(".txt")]:
            print(filename)
            file_path = os.path.join(root, filename)

            with open(file_path, encoding="utf8") as f:
                lines = f.readlines()

            output = parse(lines, start)

            with open(file_path, mode="w", encoding="utf8") as f:
                f.write("".join(output))

    if cite_keys:
        print("\ncite keys:\n")

        for key in sorted(cite_keys.keys(), key=str.lower):
            print("{}:{}".format(key, cite_keys[key]))


if __name__ == "__main__":
    main()
