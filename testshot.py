#!/usr/bin/env python

import fnmatch
import os
import sys
import pycodestyle


def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def reject_file(name):
    reject_list = [
        "migrations",
        ".venv",
    ]
    return any(r in name for r in reject_list)


def test_pep8(names):
    style = pycodestyle.StyleGuide()
    result = style.check_files(names)
    return result.total_errors == 0


# Program execution starts here

if len(sys.argv) != 2:
    print("testshot <path to project>", file=sys.stderr)
    exit(1)

project_root = sys.argv[1]

all_py = find_files("*.py", project_root)
test_py = [name for name in all_py if not reject_file(name)]

success = test_pep8(test_py)

if not success:
    print("\nTESTS FAILED, ABORTING")
    exit(1)

