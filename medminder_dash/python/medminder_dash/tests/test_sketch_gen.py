from pathlib import Path

from medminder_dash.sketch_gen import generate_alarm_hpp, minute_to_decade, parse_alarm_hpp, unesc_text, validate_hour
from medminder_dash.medicines_state import Medicine
import pytest


class TestMinuteToDecade:
    def test_zero(self):
        assert minute_to_decade(0) == 0

    def test_ten(self):
        assert minute_to_decade(10) == 1

    def test_fifty(self):
        assert minute_to_decade(50) == 5

    def test_invalid_minute_raises(self):
        with pytest.raises(ValueError):
            minute_to_decade(15)
        with pytest.raises(ValueError):
            minute_to_decade(7)


class TestValidateHour:
    def test_one(self):
        assert validate_hour(1) == 1

    def test_twenty_four(self):
        assert validate_hour(24) == 24

    def test_invalid_hour_raises(self):
        with pytest.raises(ValueError):
            validate_hour(0)
        with pytest.raises(ValueError):
            validate_hour(25)


class TestGenerateAlarmHpp:
    def test_empty_medicines(self):
        result = generate_alarm_hpp([])
        assert "#ifndef ALARM_HPP" in result
        assert "#define ALARM_HPP" in result
        assert "const Medicine medicines[] = {};" in result
        assert "#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))" in result
        assert "#endif  // ALARM_HPP" in result

    def test_single_medicine(self):
        meds = [Medicine(name="Ibup", hour=8, minute=30, day_of_week=1)]
        result = generate_alarm_hpp(meds)
        assert "{0, 1, 8, 3, \"Ibup\"}" in result
        assert "const Medicine medicines[] = {" in result

    def test_multiple_medicines(self):
        meds = [
            Medicine(name="Ibup", hour=8, minute=30, day_of_week=1),
            Medicine(name="PaRa", hour=8, minute=0, day_of_week=0),
        ]
        result = generate_alarm_hpp(meds)
        assert "{0, 1, 8, 3, \"Ibup\"}" in result
        assert "{0, 0, 8, 0, \"PaRa\"}" in result

    def test_disabled_medicine_skipped(self):
        meds = [
            Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, enabled=True),
            Medicine(name="PaRa", hour=8, minute=0, day_of_week=0, enabled=False),
        ]
        result = generate_alarm_hpp(meds)
        assert "\"Ibup\"" in result
        assert "\"PaRa\"" not in result

    def test_struct_definition_present(self):
        result = generate_alarm_hpp([])
        assert "struct Medicine {" in result
        assert "uint8_t     dayOfMonth;" in result
        assert "uint8_t     dayOfWeek;" in result
        assert "uint8_t     hour;" in result
        assert "uint8_t     decade;" in result
        assert "const char* text;" in result

    def test_hour_24_midnight(self):
        meds = [Medicine(name="Midn", hour=24, minute=0)]
        result = generate_alarm_hpp(meds)
        assert ", 24, 0, \"" in result
        assert "\"Midn\"" in result

    def test_day_of_month(self):
        meds = [Medicine(name="Bill", hour=9, minute=0, day_of_month=15)]
        result = generate_alarm_hpp(meds)
        assert "{15, 0, 9, 0, \"Bill\"}" in result

    def test_text_with_quotes_and_backslashes(self):
        meds = [Medicine(name='Te"st', hour=8, minute=0)]
        result = generate_alarm_hpp(meds)
        assert '"Te\\"st"' in result

    def test_full_output_matches_expected_format(self):
        meds = [
            Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0),
            Medicine(name="PaRa", hour=8, minute=0, day_of_week=0, day_of_month=0),
        ]
        result = generate_alarm_hpp(meds)
        expected = (
            "#ifndef ALARM_HPP\n"
            "#define ALARM_HPP\n"
            "\n"
            "struct Medicine {\n"
            "  uint8_t     dayOfMonth;\n"
            "  uint8_t     dayOfWeek;\n"
            "  uint8_t     hour;\n"
            "  uint8_t     decade;\n"
            "  const char* text;\n"
            "};\n"
            "\n"
            "const Medicine medicines[] = {\n"
            "  {0, 1, 8, 3, \"Ibup\"},\n"
            "  {0, 0, 8, 0, \"PaRa\"},\n"
            "};\n"
            "\n"
            "#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))\n"
            "\n"
            "#endif  // ALARM_HPP\n"
        )
        assert result == expected


class TestUnescText:
    def test_plain_text(self):
        assert unesc_text("Ibup") == "Ibup"

    def test_escaped_quotes(self):
        assert unesc_text('Te\\"st') == 'Te"st'

    def test_escaped_backslashes(self):
        assert unesc_text("foo\\\\bar") == "foo\\bar"

    def test_both_escapes(self):
        assert unesc_text('a\\"b\\\\c\\"d') == 'a"b\\c"d'


class TestParseAlarmHpp:
    def test_empty_array(self, tmp_path: Path):
        p = tmp_path / "alarm.hpp"
        p.write_text("const Medicine medicines[] = {};")
        assert parse_alarm_hpp(p) == []

    def test_single_entry(self, tmp_path: Path):
        p = tmp_path / "alarm.hpp"
        p.write_text(
            '#ifndef ALARM_HPP\n'
            '#define ALARM_HPP\n'
            'struct Medicine { ... };\n'
            'const Medicine medicines[] = {\n'
            '  {0, 2, 12, 3, "Test"},\n'
            '};\n'
            '#define N_MED ...\n'
            '#endif\n'
        )
        result = parse_alarm_hpp(p)
        assert len(result) == 1
        assert result[0] == {"name": "Test", "hour": 12, "minute": 30, "day_of_week": 2, "day_of_month": 0}

    def test_multiple_entries(self, tmp_path: Path):
        p = tmp_path / "alarm.hpp"
        p.write_text(
            'const Medicine medicines[] = {\n'
            '  {0, 1, 8, 3, "Ibup"},\n'
            '  {0, 0, 8, 0, "PaRa"},\n'
            '};\n'
        )
        result = parse_alarm_hpp(p)
        assert len(result) == 2
        assert result[0] == {"name": "Ibup", "hour": 8, "minute": 30, "day_of_week": 1, "day_of_month": 0}
        assert result[1] == {"name": "PaRa", "hour": 8, "minute": 0, "day_of_week": 0, "day_of_month": 0}

    def test_file_not_found(self):
        assert parse_alarm_hpp("/nonexistent/alarm.hpp") == []

    def test_c_string_escapes(self, tmp_path: Path):
        p = tmp_path / "alarm.hpp"
        p.write_text(
            'const Medicine medicines[] = {\n'
            '  {0, 0, 8, 0, "Te\\"st"},\n'
            '  {0, 0, 9, 0, "foo\\\\bar"},\n'
            '};\n'
        )
        result = parse_alarm_hpp(p)
        assert result[0]["name"] == 'Te"st'
        assert result[1]["name"] == "foo\\bar"

    def test_decade_conversion(self, tmp_path: Path):
        p = tmp_path / "alarm.hpp"
        p.write_text(
            'const Medicine medicines[] = {\n'
            '  {0, 0, 10, 5, "Last"},\n'
            '};\n'
        )
        result = parse_alarm_hpp(p)
        assert result[0]["minute"] == 50

    def test_roundtrip(self, tmp_path: Path):
        meds = [
            Medicine(name="Test", hour=8, minute=30, day_of_week=1, day_of_month=0),
            Medicine(name='Qu"ot', hour=12, minute=0, day_of_week=0, day_of_month=15),
        ]
        path = tmp_path / "alarm.hpp"
        path.write_text(generate_alarm_hpp(meds))
        parsed = parse_alarm_hpp(path)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "Test"
        assert parsed[1]["name"] == 'Qu"ot'
