# 첫 적용 체크리스트 (Quick Start)

보일러플레이트를 새 프로젝트에 적용할 때 5분 안에 한 바퀴 돌려보는 체크리스트.

---

## 1. 보일러플레이트 복사/클론

- 이 레포를 클론하거나, 사용 중인 프로젝트 루트에 `.claude/`, `templates/` 를 복사합니다.
- Hook 경로는 **워크스페이스 루트 기준 상대 경로** (`.claude/hooks/...`)를 사용하므로, 프로젝트 루트가 워크스페이스 루트와 같도록 열어두세요.

## 2. GitHub 템플릿 복사

```bash
cp -r templates/github/. .github/
```

- 이슈 템플릿, PR 템플릿, `workflows/ci.yml`, `workflows/sonarcloud.yml`(선택) 이 복사됩니다.
- Node를 쓰지 않으면 `ci.yml` 에서 `build-and-test-node` job 은 `package.json` 이 없을 때 자동으로 스킵됩니다.

## 3. (선택) PR 품질 검사 — SonarCloud

PR 올린 뒤 CI에서 품질 검사를 쓰려면 [SonarCloud](https://sonarcloud.io)에서 저장소 연결 후 `SONAR_TOKEN` 시크릿 추가. [PR-REVIEW-AND-API.md](PR-REVIEW-AND-API.md) 참고.

## 4. (선택) 프로젝트별 CLAUDE.md

```bash
cp templates/project/CLAUDE.md ./CLAUDE.md
```

- 스택(언어, 빌드, 테스트), 명령어, 아키텍처, 환경 변수만 채우면 됩니다.
- 이 파일이 있으면 루트 CLAUDE.md 공통 규칙을 오버라이드합니다.

## 5. 한 바퀴 돌려보기

1. **이슈 생성**: `/issue feat "테스트 이슈"`
2. **작업 시작**: `/start <이슈번호>`
3. **작업 후 완료**: `/done`  
   - 7단계 verify → push → PR 생성까지 한 번에 실행됩니다.

이 한 바퀴로 "자동 테스트 통과 후 PR", "규칙 코드 강제", "에이전트 변경사항 기록" 흐름을 확인할 수 있습니다.

---

## 추가로 해두면 좋은 것

- **아키텍처 테스트**: 새 프로젝트면 `/arch-setup` 한 번 실행 → ArchUnit/pytest 기반 규칙 강제.
- **Branch protection**: GitHub 저장소 설정에서 main에 "Require status checks (CI)" 활성화 → [VERIFICATION.md](VERIFICATION.md) 참고.