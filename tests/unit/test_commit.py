"""src/core/commit.py 단위 테스트.

Issue #68 -- boj commit Python 마이그레이션.
edge-cases CT1-CT9 커버리지.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.commit import (
    build_commit_message,
    check_git_email,
    check_git_repo,
    fetch_boj_stats,
    git_commit,
    has_staged_changes,
    stage_problem_files,
)
from src.core.exceptions import BojError


# ---------------------------------------------------------------------------
# check_git_repo
# ---------------------------------------------------------------------------

class TestCheckGitRepo:
    """git repo 확인."""

    def test_passes_in_git_repo(self, tmp_path):
        """정상: git repo이면 예외 없이 통과한다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # 예외 없이 통과
        check_git_repo(tmp_path)

    def test_raises_when_not_git_repo(self, tmp_path):
        """CT2: git repo가 아니면 BojError를 발생시킨다."""
        with pytest.raises(BojError, match="git 저장소가 아닙니다"):
            check_git_repo(tmp_path)


# ---------------------------------------------------------------------------
# check_git_email
# ---------------------------------------------------------------------------

class TestCheckGitEmail:
    """git user.email 확인."""

    def test_passes_when_email_set(self, tmp_path):
        """정상: email이 설정되어 있으면 통과한다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # 예외 없이 통과
        check_git_email(tmp_path)

    def test_raises_when_email_not_set(self, tmp_path, monkeypatch):
        """CT8: email이 설정되지 않으면 BojError를 발생시킨다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        # 글로벌 config 상속을 차단하여 email이 없는 상태를 보장
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        with pytest.raises(BojError, match="user.email"):
            check_git_email(tmp_path)


# ---------------------------------------------------------------------------
# fetch_boj_stats
# ---------------------------------------------------------------------------

class TestFetchBojStats:
    """BOJ 통계 조회."""

    def test_returns_stats_on_success(self):
        """정상: 메모리/시간 파싱 성공 시 통계 문자열을 반환한다."""
        html = """
        <html><body>
        <table>
        <tr><td>12345</td><td>맞았습니다</td><td>1234 KB</td><td>56 ms</td></tr>
        </table>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.text = html

        with patch("src.core.commit.requests.get", return_value=mock_resp):
            result = fetch_boj_stats("1000", "session123", "testuser")

        assert result == "[✓ 56ms 1234KB]"

    def test_returns_no_session_when_empty(self):
        """CT4 변형: 세션이 비어있으면 세션 없음을 반환한다."""
        result = fetch_boj_stats("1000", "", "testuser")

        assert "세션 없음" in result

    def test_returns_no_username_when_empty(self):
        """CT4: username이 비어있으면 사용자 ID 없음을 반환한다."""
        result = fetch_boj_stats("1000", "session123", "")

        assert "사용자 ID 없음" in result

    def test_returns_network_error_on_timeout(self):
        """CT6: 타임아웃 시 네트워크 오류를 반환한다."""
        import requests

        with patch(
            "src.core.commit.requests.get",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            result = fetch_boj_stats("1000", "session123", "testuser")

        assert "네트워크 오류" in result

    def test_returns_no_accepted_when_not_found(self):
        """CT7: Accepted 제출이 없으면 Accepted 없음을 반환한다."""
        html = "<html><body><table><tr><td>틀렸습니다</td></tr></table></body></html>"
        mock_resp = MagicMock()
        mock_resp.text = html

        with patch("src.core.commit.requests.get", return_value=mock_resp):
            result = fetch_boj_stats("1000", "session123", "testuser")

        assert "Accepted 없음" in result

    def test_returns_parse_error_when_accepted_but_no_stats(self):
        """CT5 변형: 맞았습니다가 있으나 메모리/시간 파싱 실패."""
        html = "<html><body><td>맞았습니다</td></body></html>"
        mock_resp = MagicMock()
        mock_resp.text = html

        with patch("src.core.commit.requests.get", return_value=mock_resp):
            result = fetch_boj_stats("1000", "session123", "testuser")

        assert "파싱 실패" in result

    def test_returns_empty_response(self):
        """응답이 비어있으면 응답 없음을 반환한다."""
        mock_resp = MagicMock()
        mock_resp.text = ""

        with patch("src.core.commit.requests.get", return_value=mock_resp):
            result = fetch_boj_stats("1000", "session123", "testuser")

        assert "응답 없음" in result


# ---------------------------------------------------------------------------
# build_commit_message
# ---------------------------------------------------------------------------

class TestBuildCommitMessage:
    """커밋 메시지 생성."""

    def test_auto_message_with_stats(self):
        """정상: 자동 메시지에 문제 이름과 통계가 포함된다."""
        msg = build_commit_message(
            "99999-두수의합",
            "[✓ 56ms 1234KB]",
        )

        assert "99999-두수의합" in msg
        assert "풀이 완료" in msg
        assert "56ms" in msg

    def test_auto_message_without_stats(self):
        """통계 실패 시에도 자동 메시지가 생성된다."""
        msg = build_commit_message(
            "99999-두수의합",
            "[BOJ 통계: 네트워크 오류]",
        )

        assert "99999-두수의합" in msg
        assert "네트워크 오류" in msg

    def test_custom_message_overrides(self):
        """사용자 지정 메시지가 우선한다."""
        msg = build_commit_message(
            "99999-두수의합",
            "[✓ 56ms 1234KB]",
            custom_message="my custom message",
        )

        assert msg == "my custom message"


# ---------------------------------------------------------------------------
# stage_problem_files
# ---------------------------------------------------------------------------

class TestStageProblemFiles:
    """문제 폴더 파일 staging."""

    def test_stages_existing_files(self, tmp_path):
        """존재하는 화이트리스트 파일만 staging한다."""
        # git init
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Tester"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # 문제 폴더 생성
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        (prob_dir / "README.md").write_text("# Test")
        (prob_dir / "Solution.java").write_text("class S {}")
        test_dir = prob_dir / "test"
        test_dir.mkdir()
        (test_dir / "test_cases.json").write_text('{"testCases": []}')

        result = stage_problem_files(prob_dir, cwd=tmp_path)

        assert "99999-test/README.md" in result
        assert "99999-test/Solution.java" in result
        assert "99999-test/test/test_cases.json" in result

    def test_returns_empty_when_no_files(self, tmp_path):
        """화이트리스트 파일이 없으면 빈 리스트를 반환한다."""
        prob_dir = tmp_path / "99999-empty"
        prob_dir.mkdir()

        result = stage_problem_files(prob_dir, cwd=tmp_path)

        assert result == []

    def test_ignores_nonwhitelist_files(self, tmp_path):
        """화이트리스트에 없는 파일은 staging하지 않는다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        (prob_dir / "random.txt").write_text("not whitelisted")
        (prob_dir / "README.md").write_text("# Test")

        result = stage_problem_files(prob_dir, cwd=tmp_path)

        assert "99999-test/README.md" in result
        assert "99999-test/random.txt" not in result


# ---------------------------------------------------------------------------
# has_staged_changes
# ---------------------------------------------------------------------------

class TestHasStagedChanges:
    """staging area 변경사항 확인."""

    def test_returns_false_when_clean(self, tmp_path):
        """staging area가 비어있으면 False를 반환한다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        assert has_staged_changes(tmp_path) is False

    def test_returns_true_when_staged(self, tmp_path):
        """staging된 파일이 있으면 True를 반환한다."""
        subprocess.run(
            ["git", "init", "-q"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        (tmp_path / "file.txt").write_text("hello")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        assert has_staged_changes(tmp_path) is True


# ---------------------------------------------------------------------------
# git_commit
# ---------------------------------------------------------------------------

class TestGitCommit:
    """git commit 실행."""

    def test_commits_successfully(self, tmp_path):
        """정상: staging된 파일을 커밋한다."""
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True, capture_output=True)

        (tmp_path / "file.txt").write_text("hello")
        subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True, capture_output=True)

        git_commit("test commit", cwd=tmp_path)

        # 커밋 확인
        log = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert "test commit" in log.stdout

    def test_raises_when_nothing_staged(self, tmp_path):
        """커밋할 것이 없으면 BojError를 발생시킨다."""
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True, capture_output=True)

        with pytest.raises(BojError, match="commit 실패"):
            git_commit("empty commit", cwd=tmp_path)
