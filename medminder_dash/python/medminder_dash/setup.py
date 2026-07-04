"""medminder_dash/python/medminder_dash/setup.py

medminder-dash — Medicine reminder web app for the Arduino MedMinderV2.

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from medminder_dash import __version__

from setuptools import setup, find_packages

setup(
    name="medminder-dash",
    version=__version__,
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

