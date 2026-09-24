#!/usr/bin/env python

import fnmatch
import os
import sys
from pathlib import Path
import time
import pycodestyle
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def reject_file(name):
    reject_list = [
        "manage.py",
        "migrations",
        ".venv",
    ]
    return any(r in name for r in reject_list) or os.path.getsize(name) == 0


def test_pep8(names):
    style = pycodestyle.StyleGuide()
    result = style.check_files(names)
    return result.total_errors == 0


def screenshot_name(root, folder, name):
    relpath = os.path.relpath(name, root)
    no_extension = os.path.splitext(relpath)[0]
    png_name = no_extension.replace('/', '-') + ".png"
    return os.path.join(folder, png_name)


# Program execution starts here

if len(sys.argv) != 2:
    print("testshot <path to project>", file=sys.stderr)
    exit(1)

project_root = sys.argv[1]
output_folder = os.path.join(project_root, "docs/py-valid")

all_py = find_files("*.py", project_root)
test_py = [name for name in all_py if not reject_file(name)]

success = test_pep8(test_py)

if not success:
    print("\nTESTS FAILED, ABORTING")
    exit(1)

try:
    os.makedirs(output_folder)
except FileExistsError:
    pass

driver = webdriver.Firefox()
driver.get("https://pep8ci.herokuapp.com/")

driver.implicitly_wait(2)

editor_div = driver.find_element(by=By.ID, value="editor")
textarea = editor_div.find_element(by=By.CLASS_NAME, value="ace_text-input")

for name_py in test_py:
    # Clear content
    textarea.send_keys(Keys.CONTROL, Keys.HOME)
    textarea.send_keys(Keys.CONTROL, Keys.SHIFT, Keys.END)
    textarea.send_keys(Keys.DELETE)
    # Read the file
    contents = Path(name_py).read_text()
    # Put it on the clipboard
    pyperclip.copy(contents)
    # Paste it into the control
    textarea.send_keys(Keys.CONTROL, 'v')
    textarea.send_keys(Keys.CONTROL, Keys.HOME)
    # Give it time to validate
    time.sleep(1)
    # Take a screenshot
    driver.save_screenshot(
        screenshot_name(project_root, output_folder, name_py))
