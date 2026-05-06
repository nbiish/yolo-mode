import re
from pathlib import Path

from setuptools import setup, find_packages


def _read_version() -> str:
    text = Path("yolo_mode/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to determine version.")
    return match.group(1)

setup(
    name="yolo-mode",
    version=_read_version(),
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "yolo-mode=yolo_mode.scripts.yolo_loop:main",
        ],
    },
    author="Trae User",
    description="Autonomous YOLO mode for Claude Code",
)
