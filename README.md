# TestShot

Lint Python source code and take screen shots to prove it.

Screenshots are created in `docs/py-valid`.

If the lint fails it won't take any screenshots.

The `reject_file` function determines if a python file is included.  If your virtual environment folder is not called `.venv` you'll need to add it in, otherwise the tool will pick up a great many library files.

# Installation

Clone the project and in the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Usage

```bash
python3 testshot.py <path_to_my_project>
```
