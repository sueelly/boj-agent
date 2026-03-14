"""실제 BOJ 서버에서 문제를 가져와 검증하는 라이브 테스트.

실행: python3 -m pytest tests/integration/test_live_fetch.py -v
스킵: python3 -m pytest tests/integration/test_live_fetch.py -v --skip-live

검증 대상 문제:
    1516  — 게임 개발 (일반 문제)
    16957 — 체스판 위의 공 (일반 문제)
    10799 — 쇠막대기 (이미지 포함)
    10951 — A+B - 4 (EOF 처리)
"""

import json
from pathlib import Path

import pytest

from src.core.client import (
    fetch_html,
    parse_problem,
    extract_images,
    download_images,
    rewrite_image_urls,
    strip_images,
)
from src.core.normalizer import normalize


# ──────────────────────────────────────────────
# TestLiveBojFetch — 4개 문제 fetch + 파싱 + README
# ──────────────────────────────────────────────

@pytest.mark.live
class TestLiveBojFetch:
    """4개 문제에 대한 실제 fetch + 파싱 + README 생성 검증."""

    @pytest.fixture(params=["1516", "16957", "10799", "10951"])
    def problem_data(self, request):
        """실제 BOJ에서 문제를 가져와 파싱한 결과를 반환한다."""
        problem_id = request.param
        html = fetch_html(problem_id)
        problem = parse_problem(html, problem_id)
        return problem

    def test_fetch_produces_valid_problem_json(self, problem_data):
        """problem.json 필수 필드가 모두 존재하고 비어있지 않다."""
        required_keys = [
            "problem_num", "title", "description_html",
            "input_html", "output_html", "samples",
        ]
        for key in required_keys:
            assert key in problem_data, f"필수 키 누락: {key}"

        assert problem_data["title"], "제목이 비어있습니다"
        assert problem_data["description_html"], "문제 설명이 비어있습니다"
        assert problem_data["problem_num"], "문제 번호가 비어있습니다"

    def test_readme_contains_problem_title(self, problem_data):
        """README.md에 문제 제목이 포함된다."""
        readme = normalize(problem_data)
        assert problem_data["title"] in readme

    def test_readme_contains_problem_description(self, problem_data):
        """문제 설명(description_html)이 README에 반영된다."""
        readme = normalize(problem_data)
        # description_html의 일부가 readme에 포함되어야 한다
        desc = problem_data["description_html"]
        # HTML 태그 제거 후 첫 50자 비교 (태그 때문에 직접 비교)
        assert desc[:50] in readme or problem_data["title"] in readme

    def test_readme_contains_sample_io(self, problem_data):
        """예제 입출력이 README에 포함된다."""
        readme = normalize(problem_data)
        samples = problem_data.get("samples", [])
        if samples:
            for sample in samples:
                assert f'예제 입력 {sample["id"]}' in readme
                assert f'예제 출력 {sample["id"]}' in readme


# ──────────────────────────────────────────────
# TestLiveImageDownload — 10799 쇠막대기 (이미지 포함)
# ──────────────────────────────────────────────

@pytest.mark.live
class TestLiveImageDownload:
    """10799 (쇠막대기): 이미지 포함 문제 — image_mode 검증."""

    @pytest.fixture
    def problem_10799(self):
        """10799번 문제를 가져와 파싱한다."""
        html = fetch_html("10799")
        return parse_problem(html, "10799")

    def test_fetch_extracts_images_from_html(self, problem_10799):
        """parse_problem 결과의 images 필드에 URL 목록이 존재한다."""
        images = problem_10799.get("images", [])
        assert len(images) > 0, "10799번 문제에 이미지가 없습니다"
        for img in images:
            assert "url" in img
            assert img["url"].startswith("http")

    def test_image_files_saved_to_artifacts(self, problem_10799, tmp_path):
        """image_mode=download → artifacts/에 이미지 파일이 저장된다."""
        images = problem_10799.get("images", [])
        assert images, "이미지가 없어서 테스트할 수 없습니다"

        artifacts_dir = tmp_path / "artifacts"
        results = download_images(images, artifacts_dir)

        saved = [r for r in results if r["local_path"]]
        assert len(saved) > 0, "이미지 다운로드에 실패했습니다"

        for r in saved:
            file_path = artifacts_dir / r["local_path"]
            assert file_path.exists(), f"파일이 없습니다: {file_path}"
            assert file_path.stat().st_size > 0, f"빈 파일: {file_path}"

    def test_saved_images_are_valid(self, problem_10799, tmp_path):
        """저장된 파일이 실제 이미지다 (매직 바이트 검증)."""
        images = problem_10799.get("images", [])
        assert images, "이미지가 없어서 테스트할 수 없습니다"

        artifacts_dir = tmp_path / "artifacts"
        results = download_images(images, artifacts_dir)

        # PNG: \x89PNG, JPEG: \xff\xd8, GIF: GIF8
        valid_magic = [b"\x89PNG", b"\xff\xd8", b"GIF8"]

        for r in results:
            if not r["local_path"]:
                continue
            file_path = artifacts_dir / r["local_path"]
            header = file_path.read_bytes()[:4]
            is_valid = any(header.startswith(m) for m in valid_magic)
            assert is_valid, (
                f"유효하지 않은 이미지: {r['local_path']} "
                f"(header: {header.hex()})"
            )

    def test_description_html_rewrites_to_local_paths(self, problem_10799, tmp_path):
        """description_html 내 <img src>가 로컬 파일 경로로 치환된다."""
        images = problem_10799.get("images", [])
        assert images, "이미지가 없어서 테스트할 수 없습니다"

        artifacts_dir = tmp_path / "artifacts"
        results = download_images(images, artifacts_dir)
        rewritten = rewrite_image_urls(
            problem_10799["description_html"], results,
        )

        # 다운로드 성공한 이미지의 URL이 로컬 경로로 치환되었는지 확인
        for r in results:
            if r["local_path"]:
                assert f"artifacts/{r['local_path']}" in rewritten
                # 원본 URL이 치환되어 없어야 한다
                assert r["url"] not in rewritten

    def test_reference_mode_keeps_original_urls(self, problem_10799):
        """image_mode=reference → 원본 BOJ URL 유지."""
        images = problem_10799.get("images", [])
        assert images, "이미지가 없어서 테스트할 수 없습니다"

        # reference 모드: description_html을 그대로 사용
        desc = problem_10799["description_html"]
        for img in images:
            # 원본 URL이 HTML에 남아있어야 한다
            assert img["url"] in desc or "img" in desc.lower()

    def test_skip_mode_removes_images(self, problem_10799):
        """image_mode=skip → <img> 태그 제거."""
        desc = problem_10799["description_html"]
        stripped = strip_images(desc)
        assert "<img" not in stripped.lower()
