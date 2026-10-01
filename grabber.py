#!/usr/bin/env python

import fnmatch
import os
import time
import pycodestyle
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from itertools import groupby


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


def screenshot_rel_path(rel_path):
    if rel_path == "":
        rel_path = "index"
    if rel_path[-1] == "/":
        rel_path = rel_path[0:-1]
    no_extension = os.path.splitext(rel_path)[0]
    png_name = no_extension.replace('/', '-') + ".png"
    return png_name


def set_control_text(control, text):
    # Put it on the clipboard
    pyperclip.copy(text)
    # Paste it into the control
    control.send_keys(Keys.CONTROL, 'v')
    control.send_keys(Keys.CONTROL, Keys.HOME)


# Program execution starts here

# For testing on Chromium without scrollbars need css:
# html {
#     scrollbar-width: none;
# }
root = "http://127.0.0.1:8000/"
output_rel_path = "resp-chrome"
md_file_name = "resp-chrome.md"

customer = {
    "u": "usernameForCustomer",
    "p": "password"
}

staff = {
    "u": "usernameForStaff",
    "p": "password"
}

urls = [
    {"url": ""},
    {"url": "menu/"},
    {"url": "hours"},
    {"url": "contact"},
    {"url": "accounts/login/", "user": customer},
    {"url": "reservations"},
    {"url": "reservations/2026-10-30"},
    {"url": "profile"},
    {"url": "accounts/login/", "user": staff},
    {"url": "reservations/admin"},
    {"url": "reservations/2026-10-1/admin"},
    {"url": "menu/admin"},
    {"url": "menu/course/1/add"},
    {"url": "menu/dish/54/edit"},
    {"url": "menu/course/1/toggle"},
    {"url": "menu/course/1/arrange"},
]

sizes = [
    {"name": "mobile", "w": 450, "h": 900},
    {"name": "tablet", "w": 768, "h": 640},
    {"name": "desktop", "w": 1200, "h": 1024},
]

images = []

for size in sizes:
    driver = webdriver.Chrome()
    driver.set_window_position(0, 0)
    driver.set_window_size(size["w"], size["h"])

    size_path = os.path.join(output_rel_path, size["name"])
    try:
        os.makedirs(size_path)
    except FileExistsError:
        pass

    for url_def in urls:
        user = url_def.get("user")
        if user:
            driver.delete_all_cookies()
        rel_url = url_def["url"]
        shot_name = screenshot_rel_path(rel_url)
        shot_path = os.path.join(size_path, shot_name)
        print(shot_path)
        url = root + rel_url
        driver.get(url)
        # Give it a moment
        time.sleep(1)
        driver.save_screenshot(shot_path)
        images.append(
            {"path": shot_path, "size": size["name"], "url": rel_url}
        )

        if user:
            input_u = driver.find_element(by=By.ID, value="id_login")
            input_p = driver.find_element(by=By.ID, value="id_password")
            input_u.send_keys(user["u"])
            input_p.send_keys(user["p"])
            input_p.send_keys(Keys.ENTER)
            time.sleep(2)

    driver.close()

# Remove duplicates (i.e. the login page)
images.sort(key=lambda i: i["path"])
images = [next(g) for k, g in groupby(images, key=lambda i: i["path"])]

with open(md_file_name, "w") as md_file:
    md_file.write("|Page|Mobile|Tablet|Desktop|\n")
    md_file.write("|-|-|-|-|\n")
    for url_def in urls:
        rel_url = url_def["url"]
        entry = f"|{rel_url}|"
        for size in sizes:
            for image in images:
                if image["size"] == size["name"] and image["url"] == rel_url:
                    entry += f"![]({os.path.join("docs", image["path"])})|"
        md_file.write(entry)
        md_file.write("\n")
