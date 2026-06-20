"""
medminder-dash — Medicine reminder web app for the Arduino MedMinderV2.

A small Flask dashboard that shows the medicine schedule, the next
reminder, and a live WebSocket feed of board/port events from the
BoardManagerService. It is the dashboard that
``python -m medminder_dash`` starts.

Local-source convention
-----------------------
The dependencies declared in ``pyproject.toml`` (``flask``,
``gunicorn``) use the standard PyPI package names so the package also
works with a normal ``pip install medminder-dash`` from a remote
index. In this monorepo the sibling ``*-grpc``, ``board-manager``,
``board-manager-client`` and ``arduino-sketch-tools`` packages are
installed separately (e.g. from local wheels in the Pipfile) and
therefore intentionally do **not** appear in ``pyproject.toml``'s
``dependencies`` list.
"""

from setuptools import setup, find_packages

setup(
    name="medminder-dash",
    version="0.1.0",
    description="Medicine reminder web app for Arduino MedMinderV2",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="notweerdmonk",
    author_email="wrdmnk@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(include=["medminder_dash*"]),
    install_requires=[
        "flask>=3.0",
        "gunicorn>=20.0",
    ],
    entry_points={
        "console_scripts": [
            "medminder-dash=medminder_dash.__main__:main",
        ],
    },
    package_data={
        "medminder_dash": [
            "templates/**/*",
            "static/**/*",
            "sketches/MedMinderV2/**/*",
        ],
    },
    include_package_data=True,
    keywords=["arduino", "medicine", "reminder", "dashboard", "flask"],
)
