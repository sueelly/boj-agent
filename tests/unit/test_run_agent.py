"""run_agent 디버깅 테스트 — 에이전트 subprocess 호출 검증."""

import shlex
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.make import run_agent, generate_spec
from src.core.exceptions import SpecError


class TestRunAgentCommand:
    """run_agent가 올바른 명령어를 구성하는지 검증."""

    def test_prompt_content_passed_via_stdin(self, tmp_path):
        """프롬프트 내용이 stdin으로 에이전트에 전달되는지 확인."""
        problem_dir = tmp_path / "10799-쇠막대기"
        problem_dir.mkdir()

        captured = {}

        def mock_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["input"] = kwargs.get("input")
            captured["cwd"] = kwargs.get("cwd")
            result = MagicMock()
            result.returncode = 0
            return result

        with patch("src.core.make.subprocess.run", side_effect=mock_run):
            run_agent(problem_dir, "claude -p --", "make-spec")

        cmd = captured["cmd"]
        assert cmd == ["claude", "-p", "--"], "cmd에는 프롬프트 내용이 포함되지 않아야 함"
        # 프롬프트는 stdin(input)으로 전달
        stdin_content = captured["input"]
        assert "BOJ ProblemSpec Generator" in stdin_content, "프롬프트 내용이 stdin에 포함되어야 함"
        assert str(problem_dir) in stdin_content, "문제 디렉터리 경로가 stdin에 포함되어야 함"
        # cwd는 boj-agent 루트여야 한다 (reference/ 상대 경로 해석을 위해)
        boj_root = Path(__file__).resolve().parent.parent.parent
        assert captured["cwd"] == str(boj_root)

    def test_context_files_included_in_stdin(self, tmp_path):
        """context_files로 지정한 파일 내용이 stdin에 포함되는지 확인."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        problem_json = artifacts / "problem.json"
        problem_json.write_text('{"title": "쇠막대기"}', encoding="utf-8")

        captured = {}

        def mock_run(cmd, **kwargs):
            captured["input"] = kwargs.get("input")
            result = MagicMock()
            result.returncode = 0
            return result

        with patch("src.core.make.subprocess.run", side_effect=mock_run):
            run_agent(problem_dir, "claude -p --", "make-spec", context_files={
                "problem.json": problem_json,
            })

        prompt = captured["input"]
        assert f"문제 디렉터리: {problem_dir}" in prompt
        assert "쇠막대기" in prompt, "context_files 내용이 프롬프트에 포함되어야 함"
        assert "### problem.json" in prompt, "파일 이름이 헤더로 표시되어야 함"

    def test_missing_context_file_skipped(self, tmp_path):
        """존재하지 않는 context_file은 무시."""
        problem_dir = tmp_path / "10799"
        problem_dir.mkdir()

        captured = {}

        def mock_run(cmd, **kwargs):
            captured["input"] = kwargs.get("input")
            result = MagicMock()
            result.returncode = 0
            return result

        with patch("src.core.make.subprocess.run", side_effect=mock_run):
            run_agent(problem_dir, "claude -p --", "make-spec", context_files={
                "problem.json": problem_dir / "artifacts" / "problem.json",
            })

        prompt = captured["input"]
        assert "### problem.json" not in prompt, "없는 파일은 포함되지 않아야 함"

    def test_template_vars_substituted_in_prompt(self, tmp_path):
        """template_vars로 지정한 변수가 프롬프트 내 {{KEY}}를 치환하는지 확인."""
        problem_dir = tmp_path / "10799"
        problem_dir.mkdir()

        captured = {}

        def mock_run(cmd, **kwargs):
            captured["input"] = kwargs.get("input")
            result = MagicMock()
            result.returncode = 0
            return result

        with patch("src.core.make.subprocess.run", side_effect=mock_run):
            run_agent(problem_dir, "claude -p --", "make-skeleton", template_vars={
                "LANG": "java",
                "EXT": "java",
                "SUPPORTS_PARSE": "true",
                "PROBLEM_DIR": str(problem_dir),
                "PROBLEM_JSON": '{"title": "test"}',
            })

        prompt = captured["input"]
        # 치환된 값이 프롬프트에 포함
        assert "{{LANG}}" not in prompt, "플레이스홀더가 치환되어야 함"
        assert "`java`" in prompt
        assert '{"title": "test"}' in prompt

    def test_prompt_file_must_exist(self, tmp_path):
        """존재하지 않는 프롬프트 파일은 FileNotFoundError."""
        problem_dir = tmp_path / "10799"
        problem_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            run_agent(problem_dir, "claude -p --", "nonexistent-prompt")


class TestRunAgentErrorHandling:
    """run_agent 에러 처리 검증."""

    def test_returns_nonzero_on_agent_failure(self, tmp_path):
        """에이전트 실패 시 0이 아닌 returncode를 반환."""
        problem_dir = tmp_path / "10799"
        problem_dir.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: something went wrong"

        with patch("src.core.make.subprocess.run", return_value=mock_result):
            result = run_agent(problem_dir, "claude -p --", "make-spec")

        assert result.returncode != 0

    def test_result_contains_stderr(self, tmp_path):
        """반환된 CompletedProcess에 stderr가 포함되어 있어 호출자가 활용 가능."""
        problem_dir = tmp_path / "10799"
        problem_dir.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Agent error: timeout"
        mock_result.stdout = ""

        with patch("src.core.make.subprocess.run", return_value=mock_result):
            result = run_agent(problem_dir, "claude -p --", "make-spec")

        assert result.stderr == "Agent error: timeout"


class TestGenerateSpecErrorFlow:
    """generate_spec이 에이전트 실패를 처리하는 방식 검증."""

    def test_raises_when_agent_fails_and_no_spec(self, tmp_path):
        """에이전트 실패 + spec 미생성 → SpecError."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 1
        result.stderr = "claude: command not found"
        result.stdout = ""

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="problem.spec.json이 생성되지 않았습니다"):
                generate_spec(problem_dir, "claude -p --")

    def test_ignores_agent_returncode_when_spec_exists(self, tmp_path):
        """에이전트 returncode 비정상이어도 spec 파일이 있으면 성공."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        # spec 파일을 미리 생성
        spec_path = artifacts / "problem.spec.json"
        spec_path.write_text('{"input_format": "two integers"}')

        result = MagicMock()
        result.returncode = 1  # 에이전트는 실패했지만

        with patch("src.core.make.subprocess.run", return_value=result):
            spec = generate_spec(problem_dir, "claude -p --")

        assert spec["input_format"] == "two integers"

    def test_agent_stderr_surfaced_in_error(self, tmp_path):
        """에이전트 stderr가 SpecError 메시지에 포함되는지 확인."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 127
        result.stderr = "bash: claude: command not found"
        result.stdout = ""

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="command not found"):
                generate_spec(problem_dir, "claude -p --")

    def test_agent_success_but_no_spec_shows_stdout(self, tmp_path):
        """에이전트 exit 0이지만 spec 미생성 시 stdout을 에러에 포함."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        result.stdout = "I completed the task"

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="I completed the task"):
                generate_spec(problem_dir, "claude -p --")

    def test_agent_fails_but_empty_stderr_shows_returncode(self, tmp_path):
        """에이전트 실패 + stderr 비어있음 → exit code가 에러에 포함."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 1
        result.stderr = ""
        result.stdout = ""

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="exit code: 1"):
                generate_spec(problem_dir, "claude -p --")

    def test_stdout_json_written_to_spec_file(self, tmp_path):
        """에이전트 stdout에 유효한 JSON이 있으면 spec 파일로 저장."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        spec_json = '{"specLevel": 1, "input": {"stream": "single"}}'
        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        result.stdout = spec_json

        with patch("src.core.make.subprocess.run", return_value=result):
            spec = generate_spec(problem_dir, "claude -p --")

        assert spec["specLevel"] == 1
        # 파일도 실제로 생성되었는지 확인
        assert (artifacts / "problem.spec.json").exists()

    def test_stdout_markdown_with_json_extracted(self, tmp_path):
        """에이전트 stdout이 마크다운+JSON 혼합이면 JSON만 추출하여 저장."""
        problem_dir = tmp_path / "1516"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        spec_json = '{"specLevel": 2, "input": {"stream": "single"}}'
        mixed_stdout = (
            "**Analysis:**\n"
            "- **Stream**: `single`\n\n"
            "```json\n"
            f"{spec_json}\n"
            "```\n"
        )
        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        result.stdout = mixed_stdout

        with patch("src.core.make.subprocess.run", return_value=result):
            spec = generate_spec(problem_dir, "claude -p --")

        assert spec["specLevel"] == 2
        assert (artifacts / "problem.spec.json").exists()

    def test_stdout_non_json_still_raises(self, tmp_path):
        """에이전트 stdout이 유효한 JSON이 아니면 에러 발생."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        result.stdout = "This is just a description, not JSON"

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="just a description"):
                generate_spec(problem_dir, "claude -p --")

    def test_agent_success_no_output_no_spec_gives_base_message(self, tmp_path):
        """에이전트 exit 0 + 출력 없음 + spec 미생성 → 기본 에러 메시지만."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)

        result = MagicMock()
        result.returncode = 0
        result.stderr = ""
        result.stdout = ""

        with patch("src.core.make.subprocess.run", return_value=result):
            with pytest.raises(SpecError, match="생성되지 않았습니다") as exc_info:
                generate_spec(problem_dir, "claude -p --")
        # exit code, stderr, stdout 정보 없이 기본 메시지만
        assert "exit code" not in str(exc_info.value)
        assert "stderr" not in str(exc_info.value)
        assert "stdout" not in str(exc_info.value)
