"""Python make 명령어 단위 테스트 (src/core/make.py).

Issue #54 — TDD Red 단계.
edge-cases.md M1~M13 커버리지.

subprocess.CompletedProcess mock 헬퍼: _mock_agent_result().

엣지케이스 커버리지 매핑:
- M3  (폴더 존재, -f 없음)   → TestCheckExisting.test_raises_when_dir_exists_without_force
- M3a (폴더 존재, -f 있음)   → TestCheckExisting.test_allows_overwrite_when_force
- M9  (setup_done 없음)      → TestEnsureSetup.test_runs_setup_when_no_flag
- M12 (spec 생성 실패)       → TestGenerateSpec.test_raises_when_spec_file_missing
- M13 (--keep-artifacts)      → TestCleanupArtifacts.test_keeps_all_when_flag
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.exceptions import ProblemExistsError, SpecError
from src.core.normalizer import normalize
from src.core.make import (
    check_existing,
    fetch_problem,
    generate_readme,
    generate_spec,
    generate_skeleton,
    cleanup_artifacts,
    _validate_problem_id,
    _sanitize_title_slug,
    _get_lang_meta,
    _extract_json_manifest,
    _write_skeleton_files,
    _generate_test_cases_fallback,
)
from src.core.config import (
    config_get,
    config_set,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def config_env(tmp_path, monkeypatch):
    """격리된 config 환경 (test_config.py와 동일 패턴)."""
    config_dir = tmp_path / ".config" / "boj"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv("BOJ_CONFIG_DIR", str(config_dir))
    for key in (
        "BOJ_PROG_LANG", "BOJ_EDITOR", "BOJ_AGENT",
        "BOJ_USERNAME", "BOJ_SOLUTION_ROOT", "BOJ_AGENT_ROOT",
    ):
        monkeypatch.delenv(key, raising=False)

    return config_dir


@pytest.fixture
def problem_dir(tmp_path):
    """테스트용 문제 디렉터리 (artifacts/ 포함)."""
    prob = tmp_path / "99999-test-problem"
    prob.mkdir()
    artifacts = prob / "artifacts"
    artifacts.mkdir()
    return prob


# ──────────────────────────────────────────────
# TestValidateProblemId — 입력 검증
# ──────────────────────────────────────────────

class TestValidateProblemId:
    """problem_id 숫자 검증."""

    def test_valid_id(self):
        """양의 정수는 통과."""
        _validate_problem_id("1000")  # 예외 없음
        _validate_problem_id("99999")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="유효하지 않은"):
            _validate_problem_id("")

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError, match="유효하지 않은"):
            _validate_problem_id("abc")

    def test_rejects_zero(self):
        with pytest.raises(ValueError, match="유효하지 않은"):
            _validate_problem_id("0")

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="유효하지 않은"):
            _validate_problem_id("-1")

    def test_rejects_path_traversal(self):
        with pytest.raises(ValueError, match="유효하지 않은"):
            _validate_problem_id("../etc/passwd")


# ──────────────────────────────────────────────
# TestSanitizeTitleSlug — 디렉터리 이름 안전성
# ──────────────────────────────────────────────

class TestSanitizeTitleSlug:
    """title_slug 생성 규칙."""

    def test_basic_title(self):
        assert _sanitize_title_slug("두 수의 합") == "두-수의-합"

    def test_truncates_long_title(self):
        long_title = "A" * 50
        result = _sanitize_title_slug(long_title)
        assert len(result) <= 30

    def test_strips_special_chars(self):
        result = _sanitize_title_slug("Hello! @World# (2024)")
        assert result == "Hello-World-2024"

    def test_preserves_korean(self):
        result = _sanitize_title_slug("괄호의 값")
        assert result == "괄호의-값"

    def test_preserves_hyphens(self):
        result = _sanitize_title_slug("A-B-C")
        assert result == "A-B-C"


# ──────────────────────────────────────────────
# TestCheckExisting — M3, M3a
# ──────────────────────────────────────────────

class TestCheckExisting:
    """사전 조건: 기존 폴더 존재 시 -f 검증."""

    def test_raises_when_dir_exists_without_force(self, tmp_path):
        """M3: 폴더 존재 + -f 없으면 ProblemExistsError."""
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        with pytest.raises(ProblemExistsError, match="-f"):
            check_existing(prob_dir, force=False)

    def test_allows_overwrite_when_force(self, tmp_path):
        """M3a: 폴더 존재 + -f 있으면 정상 진행 (예외 없음)."""
        prob_dir = tmp_path / "99999-test"
        prob_dir.mkdir()
        check_existing(prob_dir, force=True)  # 예외 없음

    def test_passes_when_dir_not_exists(self, tmp_path):
        """폴더 미존재 시 정상 진행."""
        prob_dir = tmp_path / "99999-test"
        check_existing(prob_dir, force=False)  # 예외 없음

    def test_error_message_contains_folder_name(self, tmp_path):
        """에러 메시지에 폴더 이름과 -f 안내가 포함된다."""
        prob_dir = tmp_path / "4949-괄호의-값"
        prob_dir.mkdir()
        with pytest.raises(ProblemExistsError, match="4949") as exc_info:
            check_existing(prob_dir, force=False)
        assert "-f" in str(exc_info.value)


# ──────────────────────────────────────────────
# TestGenerateSpec — M12
# ──────────────────────────────────────────────

class TestGenerateSpec:
    """Step 2: problem.spec.json 생성."""

    def test_raises_when_spec_file_missing(self, problem_dir):
        """M12: 에이전트 실행 후 spec 파일 없으면 SpecError."""
        with patch("src.core.make.run_agent", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")):
            with pytest.raises(SpecError, match="생성되지 않았습니다"):
                generate_spec(problem_dir, "echo MOCK")

    def test_raises_when_spec_invalid_json(self, problem_dir):
        """M12: spec 파일이 유효하지 않은 JSON이면 SpecError."""
        spec_path = problem_dir / "artifacts" / "problem.spec.json"
        spec_path.write_text("NOT VALID JSON {{{")
        with patch("src.core.make.run_agent", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")):
            with pytest.raises(SpecError, match="유효하지 않은 JSON"):
                generate_spec(problem_dir, "echo MOCK")

    def test_succeeds_when_spec_valid(self, problem_dir):
        """유효한 spec 생성 시 정상 반환."""
        spec_path = problem_dir / "artifacts" / "problem.spec.json"
        spec_path.write_text(json.dumps({
            "schemaVersion": "1.0",
            "source": {"problemId": "99999"},
            "input": {},
            "output": {},
        }))
        with patch("src.core.make.run_agent", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")):
            result = generate_spec(problem_dir, "echo MOCK")
        assert result is not None

    def test_error_message_suggests_retry(self, problem_dir):
        """에러 메시지에 '-f 로 재시도' 안내가 포함된다."""
        with patch("src.core.make.run_agent", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")):
            with pytest.raises(SpecError, match="-f"):
                generate_spec(problem_dir, "echo MOCK")

    def test_raises_when_agent_fails_and_no_spec(self, problem_dir):
        """M10: 에이전트가 non-zero exit하고 spec 미생성 시 SpecError."""
        with patch("src.core.make.run_agent", return_value=subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="agent failed")):
            with pytest.raises(SpecError, match="생성되지 않았습니다"):
                generate_spec(problem_dir, "echo MOCK")


# ──────────────────────────────────────────────
# TestCleanupArtifacts — M13
# ──────────────────────────────────────────────

class TestCleanupArtifacts:
    """Step 5: 화이트리스트 기반 정리."""

    def test_keeps_whitelisted_deletes_rest(self, problem_dir):
        """화이트리스트(README, Solution, test/, artifacts 이미지)만 유지."""
        # 유지할 파일
        (problem_dir / "README.md").write_text("# readme")
        (problem_dir / "Solution.java").write_text("class Solution {}")
        test_dir = problem_dir / "test"
        test_dir.mkdir()
        (test_dir / "Parse.java").write_text("class Parse {}")
        artifacts = problem_dir / "artifacts"
        (artifacts / "image.png").write_bytes(b"PNG")

        # 삭제될 파일/디렉터리
        omc_dir = problem_dir / ".omc"
        omc_dir.mkdir()
        (omc_dir / "state.json").write_text("{}")
        (problem_dir / "random.txt").write_text("junk")
        (artifacts / "problem.json").write_text("{}")
        (artifacts / "problem.spec.json").write_text("{}")

        cleanup_artifacts(problem_dir, keep=False, lang="java")

        # 유지 확인
        assert (problem_dir / "README.md").exists()
        assert (problem_dir / "Solution.java").exists()
        assert (test_dir / "Parse.java").exists()
        assert (artifacts / "image.png").exists()
        # 삭제 확인
        assert not omc_dir.exists()
        assert not (problem_dir / "random.txt").exists()
        assert not (artifacts / "problem.json").exists()
        assert not (artifacts / "problem.spec.json").exists()

    def test_keeps_all_when_flag(self, problem_dir):
        """M13: --keep-artifacts 시 모든 파일 유지."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")
        (problem_dir / "random.txt").write_text("junk")

        cleanup_artifacts(problem_dir, keep=True)

        assert (artifacts / "problem.json").exists()
        assert (problem_dir / "random.txt").exists()

    def test_no_error_when_dir_missing(self, tmp_path):
        """problem_dir이 없어도 에러 없이 진행."""
        prob_dir = tmp_path / "99999-nonexistent"
        cleanup_artifacts(prob_dir, keep=False)  # 예외 없음

    def test_removes_empty_artifacts_dir(self, problem_dir):
        """artifacts/ 안에 이미지가 없으면 디렉터리 자체를 삭제."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")

        cleanup_artifacts(problem_dir, keep=False)

        assert not artifacts.exists()

    def test_keeps_artifacts_dir_with_images(self, problem_dir):
        """artifacts/ 안에 이미지가 있으면 디렉터리 유지."""
        artifacts = problem_dir / "artifacts"
        (artifacts / "problem.json").write_text("{}")
        (artifacts / "diagram.svg").write_text("<svg/>")

        cleanup_artifacts(problem_dir, keep=False)

        assert artifacts.exists()
        assert (artifacts / "diagram.svg").exists()
        assert not (artifacts / "problem.json").exists()

    def test_python_solution_file_kept(self, problem_dir):
        """lang=python이면 solution.py를 유지."""
        (problem_dir / "solution.py").write_text("class Solution: pass")
        (problem_dir / "random.txt").write_text("junk")

        cleanup_artifacts(problem_dir, keep=False, lang="python")

        assert (problem_dir / "solution.py").exists()
        assert not (problem_dir / "random.txt").exists()


# ──────────────────────────────────────────────
# Fixtures — fetch/readme 테스트용
# ──────────────────────────────────────────────

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

SAMPLE_PROBLEM = {
    "problem_num": "99999",
    "title": "두 수의 합",
    "time_limit": "1 초",
    "memory_limit": "256 MB",
    "description_html": "<p>두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.</p>",
    "input_html": "<p>첫째 줄에 A와 B가 주어진다.</p>",
    "output_html": "<p>첫째 줄에 A+B를 출력한다.</p>",
    "samples": [
        {"id": 1, "input": "1 2", "output": "3"},
        {"id": 2, "input": "3 4", "output": "7"},
    ],
    "images": [],
}


# ──────────────────────────────────────────────
# TestFetchProblem — Step 0
# ──────────────────────────────────────────────

class TestFetchProblem:
    """Step 0: BOJ fetch → problem.json."""

    def test_creates_problem_json_in_artifacts(self, tmp_path):
        """정상 동작: problem.json이 artifacts/에 생성된다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>") as mock_fetch,
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM) as mock_parse,
        ):
            result = fetch_problem("99999", problem_dir=tmp_path / "99999-두-수의-합")

        assert result.exists()
        problem_json = result / "artifacts" / "problem.json"
        assert problem_json.exists()
        data = json.loads(problem_json.read_text())
        assert data["problem_num"] == "99999"
        assert data["title"] == "두 수의 합"

    def test_raises_when_html_fetch_fails(self, tmp_path):
        """네트워크 실패 시 FetchError."""
        from src.core.exceptions import FetchError
        with patch("src.core.make.fetch_html", side_effect=FetchError("network error")):
            with pytest.raises(FetchError):
                fetch_problem("99999", problem_dir=tmp_path / "99999-test")

    def test_passes_image_mode_to_processing(self, tmp_path):
        """image_mode 파라미터가 이미지 처리에 전달된다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            result = fetch_problem(
                "99999",
                image_mode="skip",
                problem_dir=tmp_path / "99999-test",
            )
            # skip 모드: images 처리가 skip됨 (에러 없이 완료)
            assert result.exists()

    def test_rejects_invalid_problem_id(self, tmp_path):
        """유효하지 않은 problem_id는 ValueError."""
        with pytest.raises(ValueError, match="유효하지 않은"):
            fetch_problem("abc", problem_dir=tmp_path / "abc-test")

    def test_raises_when_dir_exists_without_force_before_creating_artifacts(self, tmp_path):
        """기존 폴더 존재 시 artifacts 생성 전에 ProblemExistsError."""
        # SAMPLE_PROBLEM의 제목을 기반으로 생성될 디렉터리 이름과 동일하게 미리 생성
        existing_dir = tmp_path / "99999-두-수의-합"
        existing_dir.mkdir()

        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
        ):
            with pytest.raises(ProblemExistsError):
                fetch_problem("99999", base_dir=tmp_path)

        # artifacts/ 디렉터리가 새로 생성되지 않았는지 확인
        assert not (existing_dir / "artifacts").exists()

    def test_raises_on_permission_error(self, tmp_path):
        """M4: 쓰기 권한 없으면 PermissionError가 전파된다."""
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=SAMPLE_PROBLEM),
            patch("pathlib.Path.mkdir", side_effect=PermissionError("permission denied")),
        ):
            with pytest.raises(PermissionError, match="permission denied"):
                fetch_problem("99999", problem_dir=tmp_path / "99999-test")

    def test_image_mode_reference_preserves_urls(self, tmp_path):
        """M5: image_mode='reference'이면 이미지 URL을 원본 그대로 유지한다."""
        problem_with_images = {
            **SAMPLE_PROBLEM,
            "description_html": '<p>설명 <img src="https://acmicpc.net/img.png"></p>',
            "images": [{"url": "https://acmicpc.net/img.png", "alt": ""}],
        }
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=problem_with_images),
        ):
            result = fetch_problem(
                "99999",
                image_mode="reference",
                problem_dir=tmp_path / "99999-test",
            )

        problem_json = result / "artifacts" / "problem.json"
        data = json.loads(problem_json.read_text())
        # reference 모드: description_html의 img src가 변경되지 않음
        assert "https://acmicpc.net/img.png" in data["description_html"]

    def test_image_download_error_propagates(self, tmp_path):
        """M6: 이미지 다운로드 실패 시 예외가 전파된다."""
        problem_with_images = {
            **SAMPLE_PROBLEM,
            "description_html": '<p><img src="https://acmicpc.net/img.png"></p>',
            "images": [{"url": "https://acmicpc.net/img.png", "alt": ""}],
        }
        with (
            patch("src.core.make.fetch_html", return_value="<html></html>"),
            patch("src.core.make.parse_problem", return_value=problem_with_images),
            patch("src.core.client.download_images", side_effect=OSError("download failed")),
        ):
            with pytest.raises(OSError, match="download failed"):
                fetch_problem(
                    "99999",
                    image_mode="download",
                    problem_dir=tmp_path / "99999-test",
                )


# ──────────────────────────────────────────────
# TestGenerateReadme — Step 1
# ──────────────────────────────────────────────

class TestGenerateReadme:
    """Step 1: problem.json → README.md 생성."""

    def test_creates_readme_from_problem_json(self, tmp_path):
        """정상 동작: problem.json에서 README.md를 생성한다."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir()
        problem_json = artifacts / "problem.json"
        problem_json.write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        readme_path = generate_readme(problem_json)

        assert readme_path.exists()
        content = readme_path.read_text()
        assert "99999번: 두 수의 합" in content

    def test_raises_when_problem_json_missing(self, tmp_path):
        """problem.json이 없으면 FileNotFoundError."""
        missing = tmp_path / "nonexistent" / "artifacts" / "problem.json"
        with pytest.raises(FileNotFoundError):
            generate_readme(missing)

    def test_readme_contains_problem_title(self, tmp_path):
        """README에 문제 제목이 포함된다."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir()
        problem_json = artifacts / "problem.json"
        problem_json.write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        readme_path = generate_readme(problem_json)
        content = readme_path.read_text()

        assert "두 수의 합" in content
        assert "예제 입력 1" in content
        assert "예제 출력 1" in content

    def test_readme_matches_fixture_snapshot(self, tmp_path):
        """fixture 99999의 problem.json → normalize() 결과와 동일한 README를 생성한다.

        problem.json을 tmp_path에 복사해 generate_readme()를 실행한다.
        fixture 디렉터리의 readme.md를 오염/삭제하지 않도록 tmp_path를 사용한다.
        """
        fixture_dir = FIXTURES_DIR / "99999"
        problem_json_src = fixture_dir / "problem.json"
        problem = json.loads(problem_json_src.read_text(encoding="utf-8"))
        expected = normalize(problem)

        # tmp_path에 problem.json 복사 후 거기서 생성
        tmp_problem_json = tmp_path / "problem.json"
        tmp_problem_json.write_text(
            problem_json_src.read_text(encoding="utf-8"), encoding="utf-8"
        )

        readme_path = generate_readme(tmp_problem_json, problem_dir=tmp_path)
        result = readme_path.read_text()
        assert result == expected


# ──────────────────────────────────────────────
# TestGetLangMeta — 언어 메타데이터
# ──────────────────────────────────────────────

class TestGetLangMeta:
    """_get_lang_meta: languages.json에서 메타데이터 추출."""

    def test_java_meta(self):
        meta = _get_lang_meta("java")
        assert meta["ext"] == "java"
        assert meta["supports_parse"] == "true"
        assert meta["solution_file"] == "Solution.java"

    def test_python_meta(self):
        meta = _get_lang_meta("python")
        assert meta["ext"] == "py"
        assert meta["supports_parse"] == "true"
        assert meta["solution_file"] == "solution.py"

    def test_cpp_no_parse(self):
        meta = _get_lang_meta("cpp")
        assert meta["ext"] == "cpp"
        assert meta["supports_parse"] == "false"

    def test_unknown_lang_fallback(self):
        meta = _get_lang_meta("brainfuck")
        assert meta["ext"] == "brainfuck"
        assert meta["supports_parse"] == "false"
        assert meta["solution_file"] == "Solution.brainfuck"


# ──────────────────────────────────────────────
# TestExtractJsonManifest — stdout JSON 추출
# ──────────────────────────────────────────────

class TestExtractJsonManifest:
    """_extract_json_manifest: stdout에서 JSON 추출."""

    def test_pure_json(self):
        stdout = '{"files": {"Solution.java": "code"}}'
        result = _extract_json_manifest(stdout)
        assert result == {"files": {"Solution.java": "code"}}

    def test_json_in_code_fence(self):
        stdout = 'Here is the result:\n```json\n{"files": {"a.java": "x"}}\n```\nDone.'
        result = _extract_json_manifest(stdout)
        assert result["files"]["a.java"] == "x"

    def test_json_with_surrounding_text(self):
        stdout = 'Output: {"files": {"b.py": "y"}} end'
        result = _extract_json_manifest(stdout)
        assert result["files"]["b.py"] == "y"

    def test_no_json_returns_none(self):
        assert _extract_json_manifest("no json here") is None

    def test_invalid_json_returns_none(self):
        assert _extract_json_manifest("{broken json") is None


# ──────────────────────────────────────────────
# TestWriteSkeletonFiles — manifest → 파일 생성
# ──────────────────────────────────────────────

class TestWriteSkeletonFiles:
    """_write_skeleton_files: JSON manifest에서 파일 생성."""

    def test_writes_files_from_manifest(self, tmp_path):
        result = MagicMock()
        result.stdout = json.dumps({
            "files": {
                "Solution.java": "public class Solution {}",
                "test/Parse.java": "public class Parse {}",
                "test/test_cases.json": '{"testCases": []}',
            }
        })

        written = _write_skeleton_files(tmp_path, result)

        assert written is True
        assert (tmp_path / "Solution.java").read_text() == "public class Solution {}"
        assert (tmp_path / "test" / "Parse.java").read_text() == "public class Parse {}"
        assert (tmp_path / "test" / "test_cases.json").exists()

    def test_returns_false_on_empty_stdout(self, tmp_path):
        result = MagicMock()
        result.stdout = ""
        assert _write_skeleton_files(tmp_path, result) is False

    def test_returns_false_on_no_files_key(self, tmp_path):
        result = MagicMock()
        result.stdout = '{"other": "data"}'
        assert _write_skeleton_files(tmp_path, result) is False


# ──────────────────────────────────────────────
# TestGenerateTestCasesFallback
# ──────────────────────────────────────────────

class TestGenerateTestCasesFallback:
    """_generate_test_cases_fallback: samples → test_cases.json."""

    def test_generates_from_samples(self, tmp_path):
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "problem.json").write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        _generate_test_cases_fallback(problem_dir)

        tc_path = problem_dir / "test" / "test_cases.json"
        assert tc_path.exists()
        data = json.loads(tc_path.read_text())
        assert len(data["testCases"]) == 2
        assert data["testCases"][0]["input"] == "1 2"
        assert data["testCases"][0]["expected"] == "3"

    def test_skips_when_no_problem_json(self, tmp_path):
        _generate_test_cases_fallback(tmp_path)
        assert not (tmp_path / "test" / "test_cases.json").exists()

    def test_skips_when_no_samples(self, tmp_path):
        problem_dir = tmp_path / "empty"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "problem.json").write_text('{"title": "no samples"}')

        _generate_test_cases_fallback(problem_dir)
        assert not (problem_dir / "test" / "test_cases.json").exists()


# ──────────────────────────────────────────────
# TestGenerateSkeleton — Step 3 통합
# ──────────────────────────────────────────────

class TestGenerateSkeleton:
    """generate_skeleton: 에이전트 stdout → 파일 생성 + fallback."""

    def test_writes_files_from_agent_stdout(self, tmp_path):
        """에이전트가 JSON manifest 출력 → 파일 생성."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "problem.json").write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        manifest = json.dumps({
            "files": {
                "Solution.java": "public class Solution { public int solve(int a, int b) { return 0; } }",
                "test/Parse.java": "public class Parse implements ParseAndCallSolve {}",
                "test/test_cases.json": json.dumps({"testCases": [{"input": "1 2", "expected": "3"}]}),
            }
        })
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = manifest
        mock_result.stderr = ""

        with patch("src.core.make.run_agent", return_value=mock_result):
            generate_skeleton(problem_dir, "java", "claude -p --")

        assert (problem_dir / "Solution.java").exists()
        assert (problem_dir / "test" / "Parse.java").exists()
        assert (problem_dir / "test" / "test_cases.json").exists()

    def test_fallback_test_cases_when_agent_fails(self, tmp_path):
        """에이전트 실패해도 test_cases.json은 fallback으로 생성."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "problem.json").write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "agent failed"

        with patch("src.core.make.run_agent", return_value=mock_result):
            generate_skeleton(problem_dir, "java", "claude -p --")

        # Solution.java는 없지만 test_cases.json은 fallback으로 생성
        assert not (problem_dir / "Solution.java").exists()
        tc = problem_dir / "test" / "test_cases.json"
        assert tc.exists()
        data = json.loads(tc.read_text())
        assert len(data["testCases"]) == 2

    def test_template_vars_substituted(self, tmp_path):
        """template_vars가 run_agent에 전달되는지 확인."""
        problem_dir = tmp_path / "10799"
        artifacts = problem_dir / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "problem.json").write_text(json.dumps(SAMPLE_PROBLEM, ensure_ascii=False))

        captured = {}

        def mock_run_agent(pd, cmd, prompt, **kwargs):
            captured["template_vars"] = kwargs.get("template_vars")
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        with patch("src.core.make.run_agent", side_effect=mock_run_agent):
            generate_skeleton(problem_dir, "java", "claude -p --")

        tv = captured["template_vars"]
        assert tv["LANG"] == "java"
        assert tv["EXT"] == "java"
        assert tv["SUPPORTS_PARSE"] == "true"
        assert str(problem_dir) in tv["PROBLEM_DIR"]


# TestRunPipelineCallOrder — M17/M18/M19
# ──────────────────────────────────────────────

class TestRunPipelineCallOrder:
    """M17/M18/M19: _run_pipeline에서 open_editor 호출 순서 검증."""

    def _config_get(self, key, default=""):
        return {
            "agent": "echo mock",
            "prog_lang": "java",
            "solution_root": "",
            "editor": "code",
        }.get(key, default)

    @pytest.fixture
    def problem_fixture(self, tmp_path):
        """problem_dir + artifacts 구조."""
        problem_dir = tmp_path / "99999-test"
        problem_dir.mkdir()
        (problem_dir / "artifacts").mkdir()
        (problem_dir / "artifacts" / "problem.json").write_text("{}")
        return problem_dir

    def test_open_editor_called_after_readme_before_spec(self, problem_fixture):
        """M17: open_editor는 generate_readme 이후, generate_spec 이전에 호출된다."""
        from src.cli.boj_make import _run_pipeline, parse_args

        call_order = []

        def mock_readme(*a, **kw):
            call_order.append("readme")

        def mock_editor(*a, **kw):
            call_order.append("editor")

        def mock_spec(*a, **kw):
            call_order.append("spec")

        def mock_skeleton(*a, **kw):
            call_order.append("skeleton")

        args = parse_args(["99999"])
        with (

            patch("src.cli.boj_make.config_get", side_effect=self._config_get),
            patch("src.cli.boj_make.fetch_problem", return_value=problem_fixture),
            patch("src.cli.boj_make.generate_readme", side_effect=mock_readme),
            patch("src.cli.boj_make.open_editor", side_effect=mock_editor),
            patch("src.cli.boj_make.generate_spec", side_effect=mock_spec),
            patch("src.cli.boj_make.generate_skeleton", side_effect=mock_skeleton),
            patch("src.cli.boj_make.cleanup_artifacts"),
        ):
            result = _run_pipeline(args)

        assert result == 0
        assert "readme" in call_order
        assert "editor" in call_order
        assert "spec" in call_order
        readme_idx = call_order.index("readme")
        editor_idx = call_order.index("editor")
        spec_idx = call_order.index("spec")
        assert editor_idx > readme_idx, "에디터는 README 생성 이후에 열려야 한다"
        assert editor_idx < spec_idx, "에디터는 spec 생성 이전에 열려야 한다"

    def test_no_open_skips_editor_entirely(self, problem_fixture):
        """M18: --no-open이면 open_editor가 전혀 호출되지 않는다."""
        from src.cli.boj_make import _run_pipeline, parse_args

        args = parse_args(["99999", "--no-open"])
        with (

            patch("src.cli.boj_make.config_get", side_effect=self._config_get),
            patch("src.cli.boj_make.fetch_problem", return_value=problem_fixture),
            patch("src.cli.boj_make.generate_readme"),
            patch("src.cli.boj_make.open_editor") as mock_editor,
            patch("src.cli.boj_make.generate_spec"),
            patch("src.cli.boj_make.generate_skeleton"),
            patch("src.cli.boj_make.cleanup_artifacts"),
        ):
            result = _run_pipeline(args)

        assert result == 0
        mock_editor.assert_not_called()

    def test_no_editor_config_skips_early_open(self, problem_fixture):
        """M19: 에디터 미설정이면 open_editor가 호출되지 않는다."""
        from src.cli.boj_make import _run_pipeline, parse_args

        def config_no_editor(key, default=""):
            return {
                "agent": "echo mock",
                "prog_lang": "java",
                "solution_root": "",
                "editor": "",
            }.get(key, default)

        args = parse_args(["99999"])
        with (

            patch("src.cli.boj_make.config_get", side_effect=config_no_editor),
            patch("src.cli.boj_make.fetch_problem", return_value=problem_fixture),
            patch("src.cli.boj_make.generate_readme"),
            patch("src.cli.boj_make.open_editor") as mock_editor,
            patch("src.cli.boj_make.generate_spec"),
            patch("src.cli.boj_make.generate_skeleton"),
            patch("src.cli.boj_make.cleanup_artifacts"),
        ):
            result = _run_pipeline(args)

        assert result == 0
        mock_editor.assert_not_called()


# ──────────────────────────────────────────────
# TestOpenEditor
# ──────────────────────────────────────────────

class TestOpenEditor:
    """open_editor가 subprocess.Popen(non-blocking)을 사용하는지 검증."""

    def test_uses_popen_not_run(self, tmp_path):
        """Popen으로 실행 — subprocess.run은 호출되지 않아야 한다."""
        from src.core.make import open_editor

        with (
            patch("src.core.make.subprocess.Popen") as mock_popen,
            patch("src.core.make.subprocess.run") as mock_run,
        ):
            open_editor(tmp_path, "code")

        mock_popen.assert_called_once()
        mock_run.assert_not_called()

    def test_passes_problem_dir_as_arg(self, tmp_path):
        """problem_dir이 에디터 커맨드 인자로 전달된다."""
        from src.core.make import open_editor

        with patch("src.core.make.subprocess.Popen") as mock_popen:
            open_editor(tmp_path, "code")

        args, _ = mock_popen.call_args
        cmd = args[0]
        assert str(tmp_path) in cmd

    def test_skips_when_editor_cmd_empty(self, tmp_path):
        """editor_cmd가 빈 문자열이면 Popen을 호출하지 않는다."""
        from src.core.make import open_editor

        with patch("src.core.make.subprocess.Popen") as mock_popen:
            open_editor(tmp_path, "")

        mock_popen.assert_not_called()

    def test_skips_when_editor_cmd_none(self, tmp_path):
        """editor_cmd가 None이면 Popen을 호출하지 않는다."""
        from src.core.make import open_editor

        with patch("src.core.make.subprocess.Popen") as mock_popen:
            open_editor(tmp_path, None)

        mock_popen.assert_not_called()
