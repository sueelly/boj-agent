#!/usr/bin/env python3
"""boj_client.py HTTP fetch / login 테스트

실제 HTTP 연결을 사용:
  A) 로컬 Python HTTP 서버 — 네트워크 불필요, Cookie/403/404/bypass/login 검증
  B) 실제 BOJ 연결 — BOJ_SESSION 또는 BOJ_USERNAME+BOJ_PASSWORD 미설정 시 자동 스킵
"""

import http.server
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import parse_qs

# src/lib를 임포트 경로에 추가
_SRC_LIB = Path(__file__).resolve().parent.parent.parent / "src" / "lib"
sys.path.insert(0, str(_SRC_LIB))

import boj_client  # noqa: E402


# ── 로컬 HTTP 서버 헬퍼 ──────────────────────────────────────────────────────

def _make_handler(status: int, body: bytes = b"", record_into: list = None):
    """지정한 상태코드/바디를 반환하는 HTTP 핸들러 클래스를 생성한다.
    record_into가 주어지면 수신된 요청 헤더 딕셔너리를 append한다.
    """
    _record = record_into

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if _record is not None:
                _record.append(dict(self.headers))
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass  # 테스트 출력 억제

    return _Handler


def _start_server(handler_class):
    """로컬 HTTP 서버를 백그라운드 스레드로 시작한다. (server, port) 반환."""
    server = http.server.HTTPServer(("127.0.0.1", 0), handler_class)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, port


def _stop_server(server):
    """서버를 정지하고 소켓을 닫는다."""
    server.shutdown()
    server.server_close()


def _start_login_server():
    """boj_login() 테스트용 모의 로그인 서버를 시작한다.

    - GET  /signin → 200 (로그인 페이지)
    - POST /signin, 자격증명 testuser/testpass → 302 + Set-Cookie: OnlineJudge=FAKE_SESSION
    - POST /signin, 기타 자격증명 → 200 (로그인 실패 페이지, 쿠키 없음)
    - GET  /        → 200 (리다이렉트 후 홈)
    """
    port_ref = [0]  # 서버 바인딩 후 채워짐

    class _LoginHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body>page</body></html>")

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = parse_qs(body)
            uid = params.get("login_user_id", [""])[0]
            pwd = params.get("login_password", [""])[0]

            if uid == "testuser" and pwd == "testpass":
                port = port_ref[0]
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{port}/")
                self.send_header("Set-Cookie", "OnlineJudge=FAKE_SESSION; Path=/")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body>login failed</body></html>")

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), _LoginHandler)
    port_ref[0] = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, port_ref[0]


# ── Part A: 로컬 HTTP 서버 테스트 — fetch ────────────────────────────────────

class TestFetchWithLocalServer(unittest.TestCase):
    """로컬 서버를 이용한 HTTP fetch 단위 테스트 — 네트워크 불필요."""

    def test_session_cookie_sent_when_configured(self):
        """세션 파일이 있으면 Cookie: OnlineJudge=<값> 헤더를 전송해야 한다."""
        captured = []
        server, port = _start_server(
            _make_handler(200, b"<html><body>ok</body></html>", record_into=captured)
        )
        try:
            with tempfile.TemporaryDirectory() as cfg_dir:
                Path(cfg_dir, "session").write_text("MYSESSION123", encoding="utf-8")
                os.environ["BOJ_BASE_URL_OVERRIDE"] = f"http://127.0.0.1:{port}"
                os.environ["BOJ_CONFIG_DIR"] = cfg_dir
                try:
                    boj_client._fetch_html("1000")
                finally:
                    os.environ.pop("BOJ_BASE_URL_OVERRIDE", None)
                    os.environ.pop("BOJ_CONFIG_DIR", None)
        finally:
            _stop_server(server)

        self.assertTrue(len(captured) > 0, "서버가 요청을 받지 못했습니다")
        cookie = captured[0].get("Cookie", "")
        self.assertIn("OnlineJudge=MYSESSION123", cookie,
                      f"Cookie 헤더에 세션값이 없습니다: {cookie!r}")

    def test_no_cookie_when_no_session(self):
        """세션 파일이 없으면 Cookie 헤더를 전송하지 않아야 한다."""
        captured = []
        server, port = _start_server(
            _make_handler(200, b"<html></html>", record_into=captured)
        )
        try:
            with tempfile.TemporaryDirectory() as cfg_dir:
                # 세션 파일 생성 안 함
                os.environ["BOJ_BASE_URL_OVERRIDE"] = f"http://127.0.0.1:{port}"
                os.environ["BOJ_CONFIG_DIR"] = cfg_dir
                try:
                    boj_client._fetch_html("1000")
                finally:
                    os.environ.pop("BOJ_BASE_URL_OVERRIDE", None)
                    os.environ.pop("BOJ_CONFIG_DIR", None)
        finally:
            _stop_server(server)

        self.assertTrue(len(captured) > 0, "서버가 요청을 받지 못했습니다")
        cookie = captured[0].get("Cookie", "")
        self.assertNotIn("OnlineJudge", cookie,
                         f"세션 없는데 Cookie 헤더가 전송됨: {cookie!r}")

    def test_403_exits_with_error(self):
        """서버가 403을 반환하면 exit(1)해야 한다."""
        server, port = _start_server(_make_handler(403))
        with tempfile.TemporaryDirectory() as cfg_dir:
            os.environ["BOJ_BASE_URL_OVERRIDE"] = f"http://127.0.0.1:{port}"
            os.environ["BOJ_CONFIG_DIR"] = cfg_dir
            try:
                with self.assertRaises(SystemExit) as cm:
                    boj_client._fetch_html("1000")
            finally:
                _stop_server(server)
                os.environ.pop("BOJ_BASE_URL_OVERRIDE", None)
                os.environ.pop("BOJ_CONFIG_DIR", None)

        self.assertEqual(cm.exception.code, 1, "403 응답 시 exit(1)이 아님")

    def test_404_exits_with_error(self):
        """서버가 404를 반환하면 exit(1)해야 한다."""
        server, port = _start_server(_make_handler(404))
        with tempfile.TemporaryDirectory() as cfg_dir:
            os.environ["BOJ_BASE_URL_OVERRIDE"] = f"http://127.0.0.1:{port}"
            os.environ["BOJ_CONFIG_DIR"] = cfg_dir
            try:
                with self.assertRaises(SystemExit) as cm:
                    boj_client._fetch_html("99999")
            finally:
                _stop_server(server)
                os.environ.pop("BOJ_BASE_URL_OVERRIDE", None)
                os.environ.pop("BOJ_CONFIG_DIR", None)

        self.assertEqual(cm.exception.code, 1, "404 응답 시 exit(1)이 아님")

    def test_boj_client_test_html_bypasses_http(self):
        """BOJ_CLIENT_TEST_HTML 설정 시 HTTP 호출 없이 로컬 파일을 읽어야 한다."""
        with tempfile.NamedTemporaryFile(
            suffix=".html", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write("<html><body>로컬 테스트 콘텐츠</body></html>")
            html_path = f.name

        # HTTP 서버 없이도 성공해야 한다 (서버를 시작하지 않음)
        os.environ["BOJ_CLIENT_TEST_HTML"] = html_path
        try:
            result = boj_client._fetch_html("1000")
        finally:
            os.environ.pop("BOJ_CLIENT_TEST_HTML", None)
            Path(html_path).unlink(missing_ok=True)

        self.assertIn("로컬 테스트 콘텐츠", result)


# ── Part A: 로컬 HTTP 서버 테스트 — login ────────────────────────────────────

class TestLoginWithLocalServer(unittest.TestCase):
    """boj_login() 로컬 서버 기반 테스트 — 네트워크 불필요."""

    def test_successful_login_returns_session_cookie(self):
        """올바른 자격증명으로 로그인 시 OnlineJudge 쿠키 값을 반환해야 한다."""
        server, port = _start_login_server()
        try:
            os.environ["BOJ_LOGIN_URL_OVERRIDE"] = f"http://127.0.0.1:{port}/signin"
            try:
                result = boj_client.boj_login("testuser", "testpass")
            finally:
                os.environ.pop("BOJ_LOGIN_URL_OVERRIDE", None)
        finally:
            _stop_server(server)

        self.assertEqual(result, "FAKE_SESSION",
                         f"예상 쿠키 'FAKE_SESSION', 실제: {result!r}")

    def test_failed_login_raises_value_error(self):
        """잘못된 자격증명으로 로그인 시 ValueError를 발생시켜야 한다."""
        server, port = _start_login_server()
        try:
            os.environ["BOJ_LOGIN_URL_OVERRIDE"] = f"http://127.0.0.1:{port}/signin"
            try:
                with self.assertRaises(ValueError):
                    boj_client.boj_login("wronguser", "wrongpass")
            finally:
                os.environ.pop("BOJ_LOGIN_URL_OVERRIDE", None)
        finally:
            _stop_server(server)


# ── Part B: 실제 BOJ 연결 테스트 ─────────────────────────────────────────────

class TestFetchLiveBOJ(unittest.TestCase):
    """실제 acmicpc.net 연결 테스트 — 자격증명 미설정 시 자동 스킵."""

    @classmethod
    def setUpClass(cls):
        cls.session = os.environ.get("BOJ_SESSION", "")
        if not cls.session:
            username = os.environ.get("BOJ_USERNAME", "")
            password = os.environ.get("BOJ_PASSWORD", "")
            if username and password:
                try:
                    cls.session = boj_client.boj_login(username, password)
                except Exception as e:
                    raise AssertionError(
                        f"BOJ 자동 로그인 실패: {e}\n"
                        "아이디/비밀번호를 확인하세요."
                    )
            else:
                raise AssertionError(
                    "실제 BOJ 테스트를 실행하려면 다음 환경변수 중 하나를 설정하세요:\n"
                    "  BOJ_SESSION=<OnlineJudge 쿠키값>\n"
                    "  또는\n"
                    "  BOJ_USERNAME=<아이디> BOJ_PASSWORD=<비밀번호>"
                )

    def test_live_fetch_problem_1000(self):
        """실제 BOJ에서 문제 1000(A+B)을 가져와 제목과 샘플을 검증한다."""
        with tempfile.TemporaryDirectory() as cfg_dir:
            Path(cfg_dir, "session").write_text(self.session, encoding="utf-8")
            os.environ["BOJ_CONFIG_DIR"] = cfg_dir
            try:
                html = boj_client._fetch_html("1000")
            finally:
                os.environ.pop("BOJ_CONFIG_DIR", None)

        problem = boj_client.parse_problem(html, "1000")
        self.assertEqual(problem["problem_num"], "1000")
        self.assertIn("A+B", problem["title"],
                      f"문제 1000 제목에 'A+B'가 없습니다: {problem['title']!r}")
        self.assertGreater(len(problem["samples"]), 0, "샘플 입출력이 없습니다")


if __name__ == "__main__":
    unittest.main(verbosity=2)
