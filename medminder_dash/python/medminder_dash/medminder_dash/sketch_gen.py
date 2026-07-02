"""medminder_dash/python/medminder_dash/medminder_dash/sketch_gen.py

Generate and parse alarm.hpp sketch files from medicine data.

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

import re
from pathlib import Path
from typing import Any

from medminder_dash.medicines_state import Medicine


_ENTRY_RE = re.compile(
    r"\{\s*"
    r"(\d+)\s*,\s*"
    r"(\d+)\s*,\s*"
    r"(\d+)\s*,\s*"
    r"(\d+)\s*,\s*"
    r'"((?:[^"\\]|\\.)*)"\s*'
    r"\}"
)


def unesc_text(text: str) -> str:
    """Unescape backslash-escaped quotes and backslashes in text."""
    return text.replace('\\"', '"').replace("\\\\", "\\")


def parse_alarm_hpp(path: str | Path) -> list[dict[str, Any]]:
    """Parse alarm.hpp file and return list of medicine dicts.

    Args:
        path: Path to the alarm.hpp file.

    Returns:
        List of dicts with keys name, hour, minute, day_of_week, day_of_month.
    """
    try:
        text = Path(path).read_text()
    except FileNotFoundError:
        return []
    meds = []
    for line in text.splitlines():
        m = _ENTRY_RE.match(line.strip())
        if not m:
            continue
        meds.append(
            {
                "name": unesc_text(m.group(5)),
                "hour": int(m.group(3)),
                "minute": int(m.group(4)) * 10,
                "day_of_week": int(m.group(2)),
                "day_of_month": int(m.group(1)),
            }
        )
    return meds


def minute_to_decade(minute: int) -> int:
    """Convert minute (0, 10, 20, 30, 40, 50) to a decade index (0-5).

    Args:
        minute: Minute value, must be a multiple of 10 in 0-50.

    Returns:
        Decade index (minute / 10).
    """
    if minute not in (0, 10, 20, 30, 40, 50):
        raise ValueError(f"Invalid minute: {minute} (must be 0, 10, 20, 30, 40, or 50)")
    return minute // 10


def validate_hour(hour: int) -> int:
    """Validate hour is in 1-24 range.

    Args:
        hour: Hour value to validate.

    Returns:
        The validated hour.
    """
    if not (1 <= hour <= 24):
        raise ValueError(f"Invalid hour: {hour} (must be 1-24)")
    return hour


def esc_text(text: str) -> str:
    """Escape backslashes and double-quotes for C string inclusion."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return escaped


def generate_alarm_hpp(medicines: list[Medicine]) -> str:
    """Generate alarm.hpp content from a list of enabled medicines.

    Args:
        medicines: List of Medicine dataclass instances.

    Returns:
        The full alarm.hpp file content as a string.
    """
    sections = []
    for med in medicines:
        if not med.enabled:
            continue
        decade = minute_to_decade(med.minute)
        hour = validate_hour(med.hour)
        safe_text = esc_text(med.name)
        sections.append(
            f'  {{{med.day_of_month}, {med.day_of_week}, {hour}, {decade}, "{safe_text}"}},'
        )

    lines = [
        "#ifndef ALARM_HPP",
        "#define ALARM_HPP",
        "",
        "struct Medicine {",
        "  uint8_t     dayOfMonth;",
        "  uint8_t     dayOfWeek;",
        "  uint8_t     hour;",
        "  uint8_t     decade;",
        "  const char* text;",
        "};",
        "",
    ]
    if sections:
        lines.append("const Medicine medicines[] = {")
        lines.extend(sections)
        lines.append("};")
    else:
        lines.append("const Medicine medicines[] = {};")

    lines.extend(
        [
            "",
            "#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))",
            "",
            "#endif  // ALARM_HPP",
            "",
        ]
    )
    return "\n".join(lines)

