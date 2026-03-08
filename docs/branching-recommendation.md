# 브랜칭 권장안: Python 재작성

## 맥락

프로젝트는 **쉘이 아닌 Python 코어로 재작성**할 예정이다(자세한 계획은 `docs/rewrite-plan.md` 참고).  
이때 **쉘로 작성된 테스트**는 “영구 보관용”이 아니라 **마이그레이션 동안만** 필요하다.  
각 명령을 Python으로 옮기면서 해당 명령의 동작이 기존과 같은지 검증하는 **명세 역할**로 쓰고, Python 쪽 단위/통합 테스트(pytest)가 자리 잡으면 해당 쉘 테스트는 대체·제거할 계획이다.  
롤백이나 참고를 위해 예전 쉘/테스트를 `legacy/` 폴더에 넣어두는 것은 선택 사항이다.

---

## 현재 상태

```
main:                    ... -> 6e701cc (PR #21 머지: 네이티브 슬래시 커맨드)
                                         |
test/issue-23-test-coverage:             +-- [11커밋] -> b7ace23 (HEAD)
                                             픽스처, 테스트 헬퍼, boj_client 테스트
```

## 옵션

| 옵션 | 방법 | 트레이드오프 |
|------|------|--------------|
| A. 현재 테스트 브랜치 HEAD에서 분기 | `git checkout -b rewrite/python-core` (b7ace23에서) | 아직 머지 안 된 테스트 인프라 포함. 바로 작업 가능. |
| B. #23 머지 후 main에서 분기 | PR #23 → main 머지 후, `git checkout -b rewrite/python-core` | 깔끔한 기준선. PR 리뷰/머지가 선행되어야 함. |
| C. #23 이전 main에서 분기 | `git checkout -b rewrite/python-core 6e701cc` | 이슈 #23 테스트 개선 분을 잃음. 비권장. |

## 권장: 옵션 B

**절차:**
1. 이슈 #23(테스트 커버리지 작업) 마무리: 테스트 통과 확인, PR 리뷰 후 main에 머지
2. `git checkout main && git pull`
3. `git checkout -b rewrite/python-core`
4. 이 기준선에서 Python 재작성 Phase 1 시작

**옵션 B를 쓰는 이유:**
- 이슈 #23이 추가하는 `tests/unit/test_boj_client.py`, 픽스처(99999, 1000, 6588, 9495), `test_helper.sh`는 Python 재작성의 필수 기반
- 머지된 기준선이면 `git log --oneline main`이 단순하게 유지됨
- `rewrite/python-core`는 이슈 브랜치와 구분되는 장기 기능 브랜치로 의미가 분명함

**옵션 A를 쓰지 않는 이유:**
- #23 테스트 커버리지 작업과 재작성을 한 브랜치에 섞으면 변경 내용과 이유가 불명확해짐
- 테스트 수정 + 전체 재작성이 한 PR에 들어가면 리뷰가 어려움

**옵션 C를 쓰지 않는 이유:**
- #23의 테스트 인프라를 버리기엔 가치가 큼
- 특히 `boj_client.py` 테스트는 재작성 후 테스트 스타일의 모델이 됨

## PR #23 머지 후

업데이트된 main에서 분기한다. `rewrite/python-core`의 첫 커밋은 예시처럼:

```
chore(setup): boj_core 패키지 구조 초기화 [#<새이슈번호>]
```

Python 재작성을 위한 GitHub 이슈를 새로 만들고(예: "feat: CLI를 Python 코어로 이전"), 재작성 관련 PR은 모두 그 이슈에 연결하면 된다.
