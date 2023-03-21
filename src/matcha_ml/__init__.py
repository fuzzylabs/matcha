"""Initialize version of the project."""
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT_DIR, "VERSION")) as version_file:
    __version__: str = version_file.read().strip()
