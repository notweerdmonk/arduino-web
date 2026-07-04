"""arduino_sketch_tools/python/arduino_sketch_tools/arduino_sketch_tools/__init__.py

Arduino Sketch Tools — Flask Extension for compile/upload

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

__version__ = "0.1.0"

from arduino_sketch_tools.extension import ArduinoSketchTools
from arduino_sketch_tools.sketch_registry import SketchRegistry

__all__ = ["ArduinoSketchTools", "SketchRegistry"]

