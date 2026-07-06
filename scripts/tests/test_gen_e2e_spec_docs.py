"""scripts/tests/test_gen_e2e_spec_docs.py

Tests for gen_e2e_spec_docs script.

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

from __future__ import annotations

from unittest import mock

# ---------------------------------------------------------------------------
# Module skeleton
# ---------------------------------------------------------------------------


class TestSkeleton:
    def test_module_imports(self, gen_e2e_spec_docs_module):
        assert gen_e2e_spec_docs_module is not None

    def test_module_has_parse_spec(self, gen_e2e_spec_docs_module):
        assert callable(getattr(gen_e2e_spec_docs_module, "parse_spec", None))

    def test_module_has_generate(self, gen_e2e_spec_docs_module):
        assert callable(getattr(gen_e2e_spec_docs_module, "generate", None))

    def test_module_has_constants(self, gen_e2e_spec_docs_module, repo_root):
        assert gen_e2e_spec_docs_module.REPO_ROOT == repo_root
        assert gen_e2e_spec_docs_module.SPECS_DIR == repo_root / "e2e" / "specs"
        assert gen_e2e_spec_docs_module.OUTPUT == (
            repo_root / "e2e" / "docs" / "reference" / "specs.md"
        )

    def test_module_has_compiled_regex(self, gen_e2e_spec_docs_module):
        assert hasattr(gen_e2e_spec_docs_module, "DESCRIBE_RE")
        assert hasattr(gen_e2e_spec_docs_module, "TEST_RE")


# ---------------------------------------------------------------------------
# parse_spec — orphan tests (no describe blocks)
# ---------------------------------------------------------------------------


class TestParseSpecOrphans:
    def test_empty_file_returns_empty_list(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "empty.spec.ts"
        f.write_text("")
        assert gen_e2e_spec_docs_module.parse_spec(f) == []

    def test_only_comments_returns_empty_list(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "comments.spec.ts"
        f.write_text("// just a comment\n/* block */\n")
        assert gen_e2e_spec_docs_module.parse_spec(f) == []

    def test_orphan_test_collected_under_unnamed(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "orphan.spec.ts"
        f.write_text("test('my test', () => {});\n")
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("(unnamed)", ["my test"])]

    def test_multiple_orphan_tests(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "multi-orphan.spec.ts"
        f.write_text(
            "test('a', () => {});\n"
            "test('b', () => {});\n"
            "test('c', () => {});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("(unnamed)", ["a", "b", "c"])]

    def test_orphan_tests_with_various_test_modifiers(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "modifiers.spec.ts"
        f.write_text(
            "test('plain', () => {});\n"
            "test.only('only one', () => {});\n"
            "test.skip('skipped', () => {});\n"
            "test.fixme('fix me', () => {});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [
            ("(unnamed)", ["plain", "only one", "skipped", "fix me"])
        ]

    def test_orphan_test_ignores_describe_matches(self, gen_e2e_spec_docs_module, tmp_path):
        # Known limitation: regex-based parsing cannot distinguish
        # comments from code. "test.describe" appearing in a comment
        # IS matched by DESCRIBE_RE, creating a spurious suite.
        f = tmp_path / "no-match.spec.ts"
        f.write_text("// test.describe('should not match')\ntest('real test', () => {});\n")
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("should not match", ["real test"])]


# ---------------------------------------------------------------------------
# parse_spec — single describe block
# ---------------------------------------------------------------------------


class TestParseSpecSingleDescribe:
    def test_single_describe_with_tests(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "single.spec.ts"
        f.write_text(
            "test.describe('My Suite', () => {\n"
            "  test('test one', () => {});\n"
            "  test('test two', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("My Suite", ["test one", "test two"])]

    def test_single_describe_empty_suite(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "empty-suite.spec.ts"
        f.write_text("test.describe('Empty', () => {});\n")
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Empty", [])]

    def test_single_describe_uses_double_quotes(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "double-quotes.spec.ts"
        f.write_text(
            'test.describe("Suite", () => {\n'
            '  test("t1", () => {});\n'
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Suite", ["t1"])]

    def test_single_describe_with_test_modifiers(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "modifiers.spec.ts"
        f.write_text(
            "test.describe('Suite', () => {\n"
            "  test.only('only', () => {});\n"
            "  test.skip('skip', () => {});\n"
            "  test.fixme('fixme', () => {});\n"
            "  test('plain', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Suite", ["only", "skip", "fixme", "plain"])]

    def test_describe_with_only_modifier(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "describe-only.spec.ts"
        f.write_text(
            "test.describe.only('Focused Suite', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Focused Suite", ["t1"])]

    def test_describe_with_skip_modifier(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "describe-skip.spec.ts"
        f.write_text(
            "test.describe.skip('Skipped Suite', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Skipped Suite", ["t1"])]


# ---------------------------------------------------------------------------
# parse_spec — multiple describe blocks
# ---------------------------------------------------------------------------


class TestParseSpecMultipleDescribe:
    def test_two_describe_blocks(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "two-suites.spec.ts"
        f.write_text(
            "test.describe('First', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
            "test.describe('Second', () => {\n"
            "  test('t2', () => {});\n"
            "  test('t3', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("First", ["t1"]), ("Second", ["t2", "t3"])]

    def test_three_describe_blocks_with_empty_middle(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "three-suites.spec.ts"
        f.write_text(
            "test.describe('A', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
            "test.describe('B', () => {});\n"
            "test.describe('C', () => {\n"
            "  test('t2', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("A", ["t1"]), ("B", []), ("C", ["t2"])]

    def test_realistic_spec_pattern(self, gen_e2e_spec_docs_module, tmp_path):
        # Mimics the actual structure of e2e spec files
        f = tmp_path / "dashboard.spec.ts"
        f.write_text(
            "import { test, expect } from '@playwright/test';\n"
            "\n"
            "test.describe('Dashboard - Page Load', () => {\n"
            "  test('should display title', () => {});\n"
            "  test('should show boards', () => {});\n"
            "});\n"
            "\n"
            "test.describe('Dashboard - Compile', () => {\n"
            "  test('should compile sketch', () => {});\n"
            "});\n"
            "\n"
            "test.describe('Dashboard - Upload', () => {\n"
            "  test('should upload to board', () => {});\n"
            "  test('should handle errors', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [
            ("Dashboard - Page Load", ["should display title", "should show boards"]),
            ("Dashboard - Compile", ["should compile sketch"]),
            ("Dashboard - Upload", ["should upload to board", "should handle errors"]),
        ]


# ---------------------------------------------------------------------------
# parse_spec — edge cases and known limitations
# ---------------------------------------------------------------------------


class TestParseSpecEdgeCases:
    def test_describe_label_with_special_chars(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "special.spec.ts"
        f.write_text(
            "test.describe('Suite with $pecial chars (v1.0)', () => {\n"
            "  test('test with / slashes', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [
            ("Suite with $pecial chars (v1.0)", ["test with / slashes"])
        ]

    def test_describe_label_with_escaped_quotes(self, gen_e2e_spec_docs_module, tmp_path):
        # Known limitation: regex-based parsing stops at the first
        # unescaped single-quote, so escaped quotes (\') terminate
        # the label early. The label becomes "Suite with \" (trailing
        # backslash before the escaped quote).
        f = tmp_path / "escaped.spec.ts"
        f.write_text(
            "test.describe('Suite with \\'quote\\'', () => {\n"
            "  test('inner', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("Suite with \\", ["inner"])]

    def test_only_orphan_tests_no_describe_keyword_in_strings(
        self, gen_e2e_spec_docs_module, tmp_path
    ):
        # Make sure "test.describe" appearing inside a string literal
        # does not create spurious matches.
        f = tmp_path / "string-literal.spec.ts"
        f.write_text(
            "const label = 'test.describe should not match';\n"
            "test('real test', () => {});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("(unnamed)", ["real test"])]

    def test_irrelevant_imports_dont_create_matches(
        self, gen_e2e_spec_docs_module, tmp_path
    ):
        f = tmp_path / "imports.spec.ts"
        f.write_text(
            "import { test } from '@playwright/test';\n"
            "import { expect } from '@playwright/test';\n"
            "\n"
            "test.describe('My Suite', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
        )
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert result == [("My Suite", ["t1"])]

    def test_parse_spec_returns_list_of_tuples(self, gen_e2e_spec_docs_module, tmp_path):
        f = tmp_path / "type-check.spec.ts"
        f.write_text("test('x', () => {});\n")
        result = gen_e2e_spec_docs_module.parse_spec(f)
        assert isinstance(result, list)
        if result:
            suite = result[0]
            assert isinstance(suite, tuple)
            assert len(suite) == 2
            assert isinstance(suite[0], str)
            assert isinstance(suite[1], list)
            assert all(isinstance(t, str) for t in suite[1])


# ---------------------------------------------------------------------------
# generate — output structure and content
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_generate_no_spec_files_returns_1(self, gen_e2e_spec_docs_module, tmp_path):
        # Point SPECS_DIR to an empty temp directory
        specs_dir = tmp_path / "e2e" / "specs"
        specs_dir.mkdir(parents=True)
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", specs_dir),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 1
        assert not output.exists()

    def test_generate_single_spec(self, gen_e2e_spec_docs_module, tmp_path):
        specs_dir = tmp_path / "e2e" / "specs" / "arduino_dash"
        specs_dir.mkdir(parents=True)
        spec_file = specs_dir / "dashboard.spec.ts"
        spec_file.write_text(
            "test.describe('Page Load', () => {\n"
            "  test('shows title', () => {});\n"
            "});\n"
        )
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", tmp_path / "e2e" / "specs"),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 0
        assert output.exists()

        text = output.read_text()
        assert "# E2E Spec Reference" in text
        assert "dashboard.spec.ts" in text
        assert "../../specs/arduino_dash/dashboard.spec.ts" in text
        assert "Page Load" in text
        assert "shows title" in text
        assert "Do not edit manually" in text

    def test_generate_multiple_spec_files(self, gen_e2e_spec_docs_module, tmp_path):
        # Create two spec groups
        dash_dir = tmp_path / "e2e" / "specs" / "arduino_dash"
        med_dir = tmp_path / "e2e" / "specs" / "medminder_dash"
        dash_dir.mkdir(parents=True)
        med_dir.mkdir(parents=True)

        (dash_dir / "admin.spec.ts").write_text(
            "test.describe('Admin', () => {\n"
            "  test('list users', () => {});\n"
            "});\n"
        )
        (med_dir / "medicines.spec.ts").write_text(
            "test.describe('Medicines', () => {\n"
            "  test('add medicine', () => {});\n"
            "  test('delete medicine', () => {});\n"
            "});\n"
        )
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", tmp_path / "e2e" / "specs"),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 0

        text = output.read_text()
        assert "**Total**: 2 spec files, 3 tests" in text
        # Both groups appear
        assert "arduino_dash" in text
        assert "medminder_dash" in text
        # Correct relative paths
        assert "../../specs/arduino_dash/admin.spec.ts" in text
        assert "../../specs/medminder_dash/medicines.spec.ts" in text
        # Check links are not bare filenames
        assert "[admin.spec.ts](admin.spec.ts)" not in text

    def test_generate_output_is_deterministic(self, gen_e2e_spec_docs_module, tmp_path):
        # Run twice on the same input -> output should be identical
        specs_dir = tmp_path / "e2e" / "specs" / "arduino_dash"
        specs_dir.mkdir(parents=True)

        (specs_dir / "test.spec.ts").write_text(
            "test.describe('Suite', () => {\n"
            "  test('t1', () => {});\n"
            "});\n"
        )

        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", tmp_path / "e2e" / "specs"),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            gen_e2e_spec_docs_module.generate()
            first = output.read_text()
            gen_e2e_spec_docs_module.generate()
            second = output.read_text()

        assert first == second

    def test_generate_with_orphan_tests(self, gen_e2e_spec_docs_module, tmp_path):
        specs_dir = tmp_path / "e2e" / "specs" / "arduino_dash"
        specs_dir.mkdir(parents=True)
        (specs_dir / "orphan.spec.ts").write_text(
            "test('standalone test', () => {});\n"
            "test.only('another one', () => {});\n"
        )
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", tmp_path / "e2e" / "specs"),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 0

        text = output.read_text()
        assert "(unnamed)" in text
        assert "standalone test" in text
        assert "another one" in text


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


class TestGenerateExitCodes:
    def test_generate_exits_1_when_no_specs(self, gen_e2e_spec_docs_module, tmp_path):
        specs_dir = tmp_path / "e2e" / "specs"
        specs_dir.mkdir(parents=True)
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", specs_dir),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 1

    def test_generate_exits_0_on_success(self, gen_e2e_spec_docs_module, tmp_path):
        specs_dir = tmp_path / "e2e" / "specs" / "arduino_dash"
        specs_dir.mkdir(parents=True)
        (specs_dir / "ok.spec.ts").write_text(
            "test.describe('A', () => {\n  test('b', () => {});\n});\n"
        )
        output = tmp_path / "output.md"

        with (
            mock.patch.object(gen_e2e_spec_docs_module, "REPO_ROOT", tmp_path),
            mock.patch.object(gen_e2e_spec_docs_module, "SPECS_DIR", tmp_path / "e2e" / "specs"),
            mock.patch.object(gen_e2e_spec_docs_module, "OUTPUT", output),
        ):
            rc = gen_e2e_spec_docs_module.generate()
        assert rc == 0
