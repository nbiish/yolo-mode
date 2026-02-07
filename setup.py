
from setuptools import setup, find_packages

setup(
    name="yolo-mode",
    version="0.1.0",
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
