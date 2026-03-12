"""boj-agent 코어 예외 정의.

core 레이어는 sys.exit()을 사용하지 않고 예외를 raise한다.
CLI 레이어에서 잡아서 사용자 메시지 출력 + exit code 처리.
"""


class BojError(Exception):
    """boj-agent 최상위 예외."""


class FetchError(BojError):
    """BOJ HTML fetch 실패 (네트워크, 403, 404 등)."""


class ParseError(BojError):
    """HTML/JSON 파싱 실패."""


class ProblemExistsError(BojError):
    """문제 폴더가 이미 존재하고 force=False."""


class SpecError(BojError):
    """spec 파일 미생성 또는 유효하지 않은 JSON."""
