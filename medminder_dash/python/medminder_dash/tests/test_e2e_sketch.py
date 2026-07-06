"""medminder_dash/python/medminder_dash/tests/test_e2e_sketch.py

End-to-end tests for sketch generation.

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

import os
import tempfile

import pytest
from medminder_dash.medicines_state import Medicine
from medminder_dash.sketch_gen import generate_alarm_hpp

SKETCH_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), *[".."] * 4, "sketches", "MedMinderV2")
)
SKETCH_PATH = os.path.join(SKETCH_DIR, "MedMinderV2.ino")


class TestMedMinderV2SketchModified:
    """Verify MedMinderV2.ino has been correctly modified to use alarm.hpp"""

    def test_sketch_file_exists(self):
        assert os.path.exists(SKETCH_PATH), f"MedMinderV2.ino not found at {SKETCH_PATH}"

    def test_sketch_includes_alarm_hpp(self):
        with open(SKETCH_PATH) as f:
            content = f.read()
        assert '#include "alarm.hpp"' in content, "MedMinderV2.ino must include alarm.hpp"

    def test_sketch_no_longer_has_inline_struct(self):
        """The struct Medicine, medicines[], and N_MED should be gone from .ino"""
        with open(SKETCH_PATH) as f:
            content = f.read()
        # The struct definition should not appear
        assert "struct Medicine {" not in content, (
            "struct Medicine should be in alarm.hpp, not in MedMinderV2.ino"
        )
        # The medicines array declaration should not appear in the .ino
        assert "const Medicine medicines[]" not in content, (
            "medicines[] should be in alarm.hpp, not in MedMinderV2.ino"
        )
        # N_MED should not be defined in .ino
        assert "#define N_MED" not in content, (
            "N_MED should be in alarm.hpp, not in MedMinderV2.ino"
        )

    def test_sketch_still_has_other_key_content(self):
        with open(SKETCH_PATH) as f:
            content = f.read()
        assert "dismissed[N_MED]" in content, "dismissed array needs N_MED"
        assert "medicines[i]" in content, "alarm logic uses medicines[]"
        assert "void setup()" in content
        assert "void loop()" in content


class TestEndToEndGenerateAndSketch:
    """Generate alarm.hpp and verify consistency with the sketch"""

    @pytest.fixture
    def temp_sketch_dir(self):
        tmpdir = tempfile.mkdtemp()
        alarm_path = os.path.join(tmpdir, "alarm.hpp")
        return tmpdir, alarm_path

    def test_generated_alarm_works_with_sketch(self, temp_sketch_dir):
        """Generate alarm.hpp with known medicines, verify elements
        referenced by the sketch appear correctly."""
        tmpdir, alarm_path = temp_sketch_dir
        meds = [
            Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0),
            Medicine(name="PaRa", hour=20, minute=0, day_of_week=0, day_of_month=0),
        ]
        content = generate_alarm_hpp(meds)
        with open(alarm_path, "w") as f:
            f.write(content)

        assert os.path.exists(alarm_path)
        assert "#ifndef ALARM_HPP" in content
        assert "#define ALARM_HPP" in content
        assert "struct Medicine {" in content
        assert "medicines[]" in content
        assert "N_MED" in content
        assert '"Ibup"' in content
        assert '"PaRa"' in content

    def test_disabled_medicines_excluded(self, temp_sketch_dir):
        """Disabled medicines are skipped in generated alarm.hpp"""
        tmpdir, alarm_path = temp_sketch_dir
        meds = [
            Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0),
            Medicine(name="PaRa", hour=20, minute=0, day_of_week=0, day_of_month=0),
        ]
        meds[0].enabled = False
        content = generate_alarm_hpp(meds)
        assert '"Ibup"' not in content
        assert '"PaRa"' in content

    def test_empty_schedule_produces_empty_array(self, temp_sketch_dir):
        """No medicines -> empty array, N_MED = 0"""
        content = generate_alarm_hpp([])
        assert "const Medicine medicines[] = {};" in content
        assert "N_MED  (sizeof(medicines) / sizeof(medicines[0]))" in content
