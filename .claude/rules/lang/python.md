# Python 코딩 표준 (Python 3.10+)

## 네이밍 규칙
- **클래스**: PascalCase — `UserRepository`, `MessageProcessor`
- **함수/변수**: snake_case — `get_user_by_id()`, `order_count`
- **상수**: SCREAMING_SNAKE_CASE — `MAX_RETRY_COUNT`
- **모듈**: snake_case — `user_service.py`
- **비공개**: 앞에 `_` — `_internal_method()`
- 약어 지양, 의미 있는 이름 사용

## 코드 포맷
- **들여쓰기**: 공백 4칸
- **한 줄 최대 88자** (Black 기본값)
- **자동 포맷터 필수**: `black`, `isort`
- **린터**: `flake8` 또는 `ruff`

## 타입 힌트 (필수)
```python
# O — 타입 힌트 명시
def get_user(user_id: int) -> Optional[User]:
    ...

def process_messages(messages: list[Message]) -> dict[str, int]:
    ...

# O — Union type (Python 3.10+)
def find(id: int) -> User | None:
    ...

# X — 타입 힌트 없음
def get_user(user_id):
    ...
```

## 데이터 모델
```python
# O — dataclass (Python 3.7+)
from dataclasses import dataclass, field

@dataclass
class UserResponse:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)

# O — Pydantic (FastAPI/검증 필요 시)
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# X — dict 직접 사용 (타입 안전 X)
user = {"id": 1, "name": "test"}
```

## 에러 처리
```python
# O — 구체적인 예외
try:
    user = get_user(user_id)
except UserNotFoundError as e:
    logger.warning("User not found: %s", user_id)
    raise HTTPException(status_code=404, detail=str(e))

# X — 광범위한 except
try:
    ...
except Exception:
    pass  # 예외 묵살 금지
```

## 주석 & 문서화
```python
# O — docstring (Google 스타일)
def calculate_retry_delay(attempt: int, base_delay: float) -> float:
    """Calculates exponential backoff delay.

    Args:
        attempt: The current retry attempt number (0-indexed).
        base_delay: The initial delay in seconds.

    Returns:
        The calculated delay in seconds.

    Raises:
        ValueError: If attempt is negative.
    """
```

- **이유를 설명** (무엇이 아닌 왜)
- **TODO에 이슈 번호**: `# TODO(#42): refactor after migration`
- **매직 넘버/문자열 → 상수**

## 코드 구조
- **함수 단일 책임**: 권장 20줄 이하
- **이른 반환**: guard clause 활용
- **f-string 사용** (`%` 또는 `.format()` 지양):
  ```python
  # O
  message = f"User {user.name} created at {user.created_at}"
  # X
  message = "User %s created at %s" % (user.name, user.created_at)
  ```

## 테스트
- **pytest** 필수
- **파일명**: `test_<module_name>.py`
- **함수명**: `test_<behavior>_when_<condition>`
- **모킹**: `unittest.mock.patch`, `pytest-mock`
- `unittest.TestCase` 상속 대신 일반 함수 형태 권장
