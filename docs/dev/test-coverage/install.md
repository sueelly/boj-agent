# install — 테스트 커버리지 매트릭스

> `scripts/install.py` 설치 스크립트 엣지케이스 (IN1~IN8)
> 테스트 파일: `tests/unit/test_install.py`

## 엣지케이스

| # | 카테고리 | 케이스 | 기대 동작 | 자동복구 | 중단 |
|---|---------|--------|-----------|---------|------|
| IN1 | 파일시스템 | `~/bin` 없음 | 자동 생성 (`mkdir -p`) | 예 | 아니오 |
| IN2 | 파일시스템 | `~/.config/boj/` 없음 | 자동 생성 | 예 | 아니오 |
| IN3 | 파일시스템 | `~/.local/share/boj-agent/` 이미 존재 | `--force` 없으면 확인 요청, 있으면 덮어쓰기 | 사용자 선택 | 사용자 선택 |
| IN4 | 파일시스템 | self-move (src == dest) | 복사 스킵, 현재 위치 사용 | 예 | 아니오 |
| IN5 | 파일시스템 | 쓰기 권한 없음 (`~/bin` 또는 `~/.local/share/`) | `Error: 권한이 없습니다.` | 아니오 | 예 |
| IN6 | PATH | `~/bin` 이 PATH에 없음 | 셸 rc 수정 안내 메시지 출력 (계속 진행) | 아니오 | 아니오 |
| IN7 | subprocess | `boj setup` 실패 | `Warning: setup 실패. 수동 실행하세요.` | 아니오 | 아니오 |
| IN8 | 파일시스템 | `src/boj` 없음 (깨진 clone) | `Error: boj-agent 저장소가 아닙니다.` | 아니오 | 예 |

## 테스트 매핑

| 함수 | 테스트 클래스 | 커버 엣지케이스 |
|------|-------------|----------------|
| `resolve_repo_root` | `TestResolveRepoRoot` | IN8 |
| `copy_agent_files` | `TestCopyAgentFiles` | IN3, IN4, IN5 |
| `install_cli` | `TestInstallCli` | IN1, IN5 |
| `save_config` | `TestSaveConfig` | IN2 |
| `check_path` | `TestCheckPath` | IN6 |
| `detect_shell_rc` | `TestDetectShellRc` | IN6 |
| `print_path_advice` | `TestPrintPathAdvice` | IN6 |
| `run_setup` | `TestRunSetup` | IN7 |
| `main` | `TestMain` | IN1~IN8 통합 |

## Fixture

```python
@pytest.fixture
def install_env(tmp_path, monkeypatch):
    """fake repo + fake HOME 격리 환경."""
```

- `tmp_path`에 fake boj-agent repo 구조 생성 (src/boj, templates/)
- `monkeypatch`로 HOME, BOJ_CONFIG_DIR 오버라이드
- subprocess mock으로 boj setup 호출 격리
