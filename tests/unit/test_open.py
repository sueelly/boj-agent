"""src/core/open.py 단위 테스트.

Issue #66 — boj open Python 마이그레이션.
edge-cases O1-O4 커버리지.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.exceptions import BojError


# ---------------------------------------------------------------------------
# find_or_create_problem_dir
# ---------------------------------------------------------------------------

class TestFindOrCreateProblemDir:
    """문제 폴더 검색."""

    def test_returns_path_when_dir_exists(self, tmp_path):
        """문제 폴더가 존재하면 경로를 반환한다."""
        from src.core.open import find_or_create_problem_dir

        prob_dir = tmp_path / "99999-두수의합"
        prob_dir.mkdir()

        result = find_or_create_problem_dir("99999", base_dir=tmp_path)

        assert result == prob_dir

    def test_raises_when_dir_missing(self, tmp_path):
        """O1: 문제 폴더가 없으면 BojError를 발생시킨다."""
        from src.core.open import find_or_create_problem_dir

        with pytest.raises(BojError, match="문제 폴더가 없습니다"):
            find_or_create_problem_dir("99999", base_dir=tmp_path)

    def test_raises_message_suggests_make(self, tmp_path):
        """O1: 에러 메시지에 boj make 안내가 포함된다."""
        from src.core.open import find_or_create_problem_dir

        with pytest.raises(BojError, match="boj make"):
            find_or_create_problem_dir("12345", base_dir=tmp_path)

    def test_uses_config_when_base_dir_none(self, tmp_path):
        """base_dir이 None이면 config에서 solution_root를 읽는다."""
        from src.core.open import find_or_create_problem_dir

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.config_get", return_value=str(tmp_path)):
            result = find_or_create_problem_dir("99999")

        assert result == prob_dir


# ---------------------------------------------------------------------------
# open_in_editor
# ---------------------------------------------------------------------------

class TestOpenInEditor:
    """에디터로 문제 폴더 열기."""

    def test_calls_popen_with_editor_and_dir(self, tmp_path):
        """에디터 명령어와 폴더 경로로 Popen을 호출한다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value="/usr/bin/code"), \
             patch("src.core.open.subprocess.Popen") as mock_popen:
            open_in_editor(prob_dir, "code")

        mock_popen.assert_called_once_with(
            ["code", str(prob_dir)],
            cwd=str(prob_dir),
        )

    def test_handles_editor_with_args(self, tmp_path):
        """에디터 명령어에 인수가 포함된 경우를 처리한다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value="/usr/bin/code"), \
             patch("src.core.open.subprocess.Popen") as mock_popen:
            open_in_editor(prob_dir, "code --new-window")

        mock_popen.assert_called_once_with(
            ["code", "--new-window", str(prob_dir)],
            cwd=str(prob_dir),
        )

    def test_raises_when_editor_empty(self, tmp_path):
        """O2: 에디터가 비어있으면 BojError를 발생시킨다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with pytest.raises(BojError, match="에디터가 설정되지 않았습니다"):
            open_in_editor(prob_dir, "")

    def test_raises_when_editor_none(self, tmp_path):
        """O2: 에디터가 None이면 BojError를 발생시킨다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with pytest.raises(BojError, match="에디터가 설정되지 않았습니다"):
            open_in_editor(prob_dir, None)

    def test_raises_when_editor_whitespace_only(self, tmp_path):
        """O2: 에디터가 공백만 있으면 BojError를 발생시킨다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with pytest.raises(BojError, match="에디터가 설정되지 않았습니다"):
            open_in_editor(prob_dir, "   ")

    def test_raises_when_editor_not_in_path(self, tmp_path):
        """O4: 에디터가 PATH에 없으면 BojError를 발생시킨다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value=None):
            with pytest.raises(BojError, match="찾을 수 없습니다"):
                open_in_editor(prob_dir, "nonexistent-editor")

    def test_error_message_includes_editor_name(self, tmp_path):
        """O4: 에러 메시지에 에디터 이름이 포함된다."""
        from src.core.open import open_in_editor

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value=None):
            with pytest.raises(BojError, match="mycustom"):
                open_in_editor(prob_dir, "mycustom")


# ---------------------------------------------------------------------------
# open_problem (통합 단위)
# ---------------------------------------------------------------------------

class TestOpenProblem:
    """open_problem() 전체 흐름."""

    def test_opens_existing_dir_with_editor(self, tmp_path):
        """정상 경로: 폴더 존재 + 에디터 설정 → Popen 호출."""
        from src.core.open import open_problem

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value="/usr/bin/code"), \
             patch("src.core.open.subprocess.Popen") as mock_popen:
            result = open_problem(
                "99999", editor="code", base_dir=tmp_path,
            )

        assert result == prob_dir
        mock_popen.assert_called_once()

    def test_editor_override_takes_precedence(self, tmp_path):
        """O3: --editor flag가 config보다 우선한다."""
        from src.core.open import open_problem

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value="/usr/bin/vim"), \
             patch("src.core.open.subprocess.Popen") as mock_popen, \
             patch("src.core.open.config_get", return_value="code"):
            open_problem("99999", editor="vim", base_dir=tmp_path)

        # vim이 사용되어야 함 (code가 아님)
        args = mock_popen.call_args[0][0]
        assert args[0] == "vim"

    def test_uses_config_editor_when_no_override(self, tmp_path):
        """에디터 미지정 시 config에서 읽는다."""
        from src.core.open import open_problem

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value="/usr/bin/cursor"), \
             patch("src.core.open.subprocess.Popen") as mock_popen, \
             patch("src.core.open.config_get", return_value="cursor"):
            open_problem("99999", editor=None, base_dir=tmp_path)

        args = mock_popen.call_args[0][0]
        assert args[0] == "cursor"

    def test_raises_when_dir_missing(self, tmp_path):
        """O1: 폴더 없으면 BojError."""
        from src.core.open import open_problem

        with pytest.raises(BojError, match="문제 폴더가 없습니다"):
            open_problem("99999", editor="code", base_dir=tmp_path)

    def test_raises_when_editor_not_found(self, tmp_path):
        """O4: 에디터 PATH 없으면 BojError."""
        from src.core.open import open_problem

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.open.shutil.which", return_value=None):
            with pytest.raises(BojError, match="찾을 수 없습니다"):
                open_problem(
                    "99999", editor="nonexistent", base_dir=tmp_path,
                )
