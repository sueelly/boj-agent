"""src/core/review.py 단위 테스트.

Issue #67 -- boj review Python 마이그레이션.
edge-cases RV1-RV4 커버리지.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# find_solution_file
# ---------------------------------------------------------------------------

class TestFindSolutionFile:
    """Solution 파일 탐색 테스트."""

    def test_finds_java_solution(self, tmp_path):
        """Solution.java가 있으면 경로를 반환한다."""
        from src.core.review import find_solution_file

        (tmp_path / "Solution.java").write_text("class Solution {}")

        result = find_solution_file(tmp_path, lang="java")

        assert result is not None
        assert result.name == "Solution.java"

    def test_finds_python_solution_lowercase(self, tmp_path):
        """solution.py가 있으면 경로를 반환한다."""
        from src.core.review import find_solution_file

        (tmp_path / "solution.py").write_text("class Solution: pass")

        result = find_solution_file(tmp_path, lang="python")

        assert result is not None
        assert result.name == "solution.py"

    def test_finds_python_solution_uppercase(self, tmp_path):
        """Solution.py가 있으면 경로를 반환한다."""
        from src.core.review import find_solution_file

        (tmp_path / "Solution.py").write_text("class Solution: pass")

        result = find_solution_file(tmp_path, lang="python")

        assert result is not None
        # macOS는 case-insensitive FS이므로 solution.py 후보가 먼저 매칭될 수 있음
        assert result.name.lower() == "solution.py"

    def test_returns_none_when_missing(self, tmp_path):
        """RV2: Solution 파일이 없으면 None을 반환한다."""
        from src.core.review import find_solution_file

        result = find_solution_file(tmp_path, lang="java")

        assert result is None

    def test_finds_any_solution_when_lang_none(self, tmp_path):
        """lang=None이면 모든 Solution.*에서 탐색한다."""
        from src.core.review import find_solution_file

        (tmp_path / "Solution.java").write_text("class Solution {}")

        result = find_solution_file(tmp_path, lang=None)

        assert result is not None
        assert result.name == "Solution.java"

    def test_returns_none_when_no_solution_and_lang_none(self, tmp_path):
        """lang=None이고 Solution 파일이 없으면 None."""
        from src.core.review import find_solution_file

        result = find_solution_file(tmp_path)

        assert result is None


# ---------------------------------------------------------------------------
# build_review_prompt
# ---------------------------------------------------------------------------

class TestBuildReviewPrompt:
    """리뷰 프롬프트 빌드 테스트."""

    def test_includes_template_content(self, tmp_path):
        """프롬프트 템플릿 내용이 포함된다."""
        from src.core.review import build_review_prompt

        template = tmp_path / "review.md"
        template.write_text("# 코드 리뷰 지시")

        result = build_review_prompt(tmp_path, template)

        assert "코드 리뷰 지시" in result

    def test_includes_solution_content(self, tmp_path):
        """Solution 파일 내용이 프롬프트에 포함된다."""
        from src.core.review import build_review_prompt

        template = tmp_path / "review.md"
        template.write_text("# Review")
        (tmp_path / "Solution.java").write_text(
            "class Solution {\n    int solve() { return 42; }\n}"
        )

        result = build_review_prompt(tmp_path, template)

        assert "solve" in result
        assert "return 42" in result
        assert "Solution.java" in result

    def test_prompt_without_solution(self, tmp_path):
        """RV2: Solution 없어도 프롬프트가 생성된다."""
        from src.core.review import build_review_prompt

        template = tmp_path / "review.md"
        template.write_text("# Review template")

        result = build_review_prompt(tmp_path, template)

        assert "Review template" in result
        assert "리뷰해줘" in result

    def test_prompt_without_template(self, tmp_path):
        """템플릿 파일이 없어도 프롬프트가 생성된다."""
        from src.core.review import build_review_prompt

        nonexistent = tmp_path / "nonexistent.md"

        result = build_review_prompt(tmp_path, nonexistent)

        assert "리뷰해줘" in result

    def test_prompt_ends_with_review_request(self, tmp_path):
        """프롬프트는 '리뷰해줘'로 끝난다."""
        from src.core.review import build_review_prompt

        template = tmp_path / "review.md"
        template.write_text("# Review")

        result = build_review_prompt(tmp_path, template)

        assert result.rstrip().endswith("리뷰해줘")


# ---------------------------------------------------------------------------
# run_review
# ---------------------------------------------------------------------------

class TestRunReview:
    """에이전트 리뷰 실행 테스트."""

    @patch("src.core.review.subprocess.run")
    def test_calls_subprocess_with_correct_args(self, mock_run, tmp_path):
        """RV1: 에이전트를 올바른 인수로 호출한다."""
        from src.core.review import run_review

        mock_run.return_value = subprocess.CompletedProcess(
            args=["echo"], returncode=0, stdout="review done", stderr="",
        )

        result = run_review(tmp_path, "echo -p --", "리뷰해줘")

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["echo", "-p", "--", "리뷰해줘"]
        assert call_args[1]["cwd"] == str(tmp_path)
        assert result.returncode == 0

    @patch("src.core.review.subprocess.run")
    def test_raises_boj_error_when_agent_fails(self, mock_run, tmp_path):
        """RV4: 에이전트 exit code != 0이면 BojError."""
        from src.core.exceptions import BojError
        from src.core.review import run_review

        mock_run.return_value = subprocess.CompletedProcess(
            args=["agent"], returncode=1, stdout="", stderr="agent error",
        )

        with pytest.raises(BojError, match="에이전트 실행 실패"):
            run_review(tmp_path, "agent -p", "리뷰해줘")

    @patch("src.core.review.subprocess.run")
    def test_raises_boj_error_when_command_not_found(self, mock_run, tmp_path):
        """RV4: 에이전트 바이너리가 없으면 BojError."""
        from src.core.exceptions import BojError
        from src.core.review import run_review

        mock_run.side_effect = FileNotFoundError("No such file")

        with pytest.raises(BojError, match="에이전트 실행 실패"):
            run_review(tmp_path, "nonexistent-agent", "리뷰해줘")


# ---------------------------------------------------------------------------
# clipboard_fallback
# ---------------------------------------------------------------------------

class TestClipboardFallback:
    """클립보드 fallback 테스트."""

    @patch("src.core.review.subprocess.run")
    def test_returns_true_when_pbcopy_available(self, mock_run):
        """pbcopy가 있으면 True를 반환한다."""
        from src.core.review import clipboard_fallback

        mock_run.return_value = subprocess.CompletedProcess(
            args=["pbcopy"], returncode=0, stdout="", stderr="",
        )

        result = clipboard_fallback("리뷰해줘")

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["input"] == "리뷰해줘"

    @patch("src.core.review.subprocess.run")
    def test_returns_false_when_no_clipboard_tool(self, mock_run):
        """클립보드 도구가 없으면 False를 반환한다."""
        from src.core.review import clipboard_fallback

        mock_run.side_effect = FileNotFoundError("No such file")

        result = clipboard_fallback("리뷰해줘")

        assert result is False


# ---------------------------------------------------------------------------
# write_review_file
# ---------------------------------------------------------------------------

class TestWriteReviewFile:
    """submit/REVIEW.md 파일 쓰기 테스트."""

    def test_creates_submit_dir_and_writes_file(self, tmp_path):
        """submit/ 디렉터리를 생성하고 REVIEW.md를 쓴다."""
        from src.core.review import write_review_file

        content = "# 99999 두 수의 합 - 코드 리뷰\n\n리뷰 내용"
        result_path = write_review_file(tmp_path, content)

        assert result_path == tmp_path / "submit" / "REVIEW.md"
        assert result_path.exists()
        assert result_path.read_text(encoding="utf-8") == content

    def test_overwrites_existing_review(self, tmp_path):
        """기존 REVIEW.md가 있으면 덮어쓴다."""
        from src.core.review import write_review_file

        submit_dir = tmp_path / "submit"
        submit_dir.mkdir()
        (submit_dir / "REVIEW.md").write_text("old review")

        new_content = "# new review"
        result_path = write_review_file(tmp_path, new_content)

        assert result_path.read_text(encoding="utf-8") == new_content

    def test_handles_unicode_content(self, tmp_path):
        """한국어 리뷰 내용을 UTF-8로 저장한다."""
        from src.core.review import write_review_file

        content = "# 99999 두 수의 합 - 코드 리뷰\n\n## 접근 방식\n- 완전탐색"
        result_path = write_review_file(tmp_path, content)

        assert result_path.read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# review (메인 함수)
# ---------------------------------------------------------------------------

class TestReview:
    """review 메인 함수 테스트."""

    def test_raises_boj_error_when_problem_dir_missing(self, tmp_path):
        """RV3: 문제 폴더가 없으면 BojError."""
        from src.core.exceptions import BojError
        from src.core.review import review

        with pytest.raises(BojError, match="문제 폴더가 없습니다"):
            review(
                problem_num="99999",
                solution_root=tmp_path,
                agent_root=tmp_path,
            )

    def test_warns_when_solution_missing(self, tmp_path, capsys):
        """RV2: Solution 파일 없으면 Warning을 출력한다."""
        from src.core.review import review

        # 문제 폴더 생성 (Solution 없이)
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()

        with patch("src.core.review.config_get", return_value=""):
            result = review(
                problem_num="99999",
                solution_root=tmp_path,
                agent_root=tmp_path,
            )

        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "Solution" in captured.err

    @patch("src.core.review.run_review")
    @patch("src.core.review.config_get")
    def test_calls_agent_when_configured(
        self, mock_config, mock_run_review, tmp_path,
    ):
        """RV1: 에이전트가 설정되면 run_review를 호출하고 REVIEW.md를 생성한다."""
        from src.core.review import review

        # 문제 폴더 + Solution
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        (prob_dir / "Solution.java").write_text("class S {}")

        # prompts 폴더
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "review.md").write_text("# Review")

        mock_config.side_effect = lambda key, default="": {
            "agent": "claude",
            "solution_root": "",
            "boj_agent_root": "",
            "editor": "code",
        }.get(key, default)

        mock_run_review.return_value = subprocess.CompletedProcess(
            args=["claude"], returncode=0, stdout="# Review Content", stderr="",
        )

        result = review(
            problem_num="99999",
            solution_root=tmp_path,
            agent_root=tmp_path,
        )

        mock_run_review.assert_called_once()
        assert result is not None
        # REVIEW.md 파일이 생성되었는지 확인
        review_path = prob_dir / "submit" / "REVIEW.md"
        assert review_path.exists()
        assert review_path.read_text(encoding="utf-8") == "# Review Content"

    @patch("src.core.review.run_review")
    @patch("src.core.review.config_get")
    def test_does_not_write_review_when_stdout_empty(
        self, mock_config, mock_run_review, tmp_path,
    ):
        """에이전트 stdout이 빈 경우 REVIEW.md를 생성하지 않는다."""
        from src.core.review import review

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        (prob_dir / "Solution.java").write_text("class S {}")

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "review.md").write_text("# Review")

        mock_config.side_effect = lambda key, default="": {
            "agent": "claude",
            "solution_root": "",
            "boj_agent_root": "",
            "editor": "code",
        }.get(key, default)

        mock_run_review.return_value = subprocess.CompletedProcess(
            args=["claude"], returncode=0, stdout="", stderr="",
        )

        result = review(
            problem_num="99999",
            solution_root=tmp_path,
            agent_root=tmp_path,
        )

        review_path = prob_dir / "submit" / "REVIEW.md"
        assert not review_path.exists()

    @patch("src.core.review.clipboard_fallback")
    @patch("src.core.review.config_get")
    def test_falls_back_to_clipboard_when_no_agent(
        self, mock_config, mock_clipboard, tmp_path,
    ):
        """RV3: 에이전트 미설정 시 clipboard fallback."""
        from src.core.review import review

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        (prob_dir / "Solution.java").write_text("class S {}")

        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "review.md").write_text("# Review")

        mock_config.side_effect = lambda key, default="": {
            "agent": "",
            "solution_root": "",
            "boj_agent_root": "",
            "editor": "",
        }.get(key, default)

        mock_clipboard.return_value = True

        result = review(
            problem_num="99999",
            solution_root=tmp_path,
            agent_root=tmp_path,
        )

        assert result is None
        mock_clipboard.assert_called_once_with("리뷰해줘")
