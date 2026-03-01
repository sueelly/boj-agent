# 이번 변경 커밋 단위 제안

GitHub 이슈를 쓰는 경우 `[#N]`을 메시지 끝에 붙이면 됨. 이슈 없으면 생략.

---

## 옵션 A — 5개 커밋 (역할별)

| # | 커밋 메시지 | 포함 파일 |
|---|-------------|-----------|
| 1 | `chore(portability): remove hardcoded paths in hooks and skills` | `.claude/hooks/stop.sh`, `.claude/settings.json`, `.claude/skills/log/SKILL.md`, `.claude/skills/arch-setup/SKILL.md`, `docs/AGENT-GUIDE.md`, `templates/project/CLAUDE.md` |
| 2 | `feat(verify): add --quick option and consolidate build/test gate` | `.claude/skills/verify/SKILL.md` |
| 3 | `refactor(token): shorten code-reviewer checklist and CLAUDE.md table` | `.claude/agents/code-reviewer.md`, `CLAUDE.md`, `.claude/skills/log/SKILL.md` |
| 4 | `refactor(ci): replace claude.yml with sonarcloud, add Node job and dependabot` | `templates/github/workflows/ci.yml`, `templates/github/workflows/claude.yml`(삭제), `templates/github/workflows/sonarcloud.yml`, `templates/github/dependabot.yml` |
| 5 | `docs: add QUICKSTART, WHAT-TO-PUSH, verification and table dedup` | `docs/QUICKSTART.md`, `docs/VERIFICATION.md`, `docs/WORKFLOW.md`, `README.md`, `templates/project/.gitignore.claude`, 기타 새 문서(PR-REVIEW-AND-API, WHAT-TO-PUSH 등) |

---

## 옵션 B — 3개 커밋 (더 굵게)

| # | 커밋 메시지 | 포함 내용 |
|---|-------------|-----------|
| 1 | `chore(portability): use relative paths and repo root in hooks and skills` | 이식성 관련 전체 (stop.sh, settings.json, log, arch-setup, AGENT-GUIDE, templates/project/CLAUDE.md) |
| 2 | `refactor(verify,token,ci): --quick, token trim, sonarcloud and dependabot` | verify 스킬, code-reviewer·CLAUDE·log 토큰 절감, claude.yml 제거·sonarcloud·ci Node·dependabot |
| 3 | `docs: QUICKSTART, verification, what-to-push, table dedup` | QUICKSTART, VERIFICATION·WORKFLOW 수정, README 표 정리, WHAT-TO-PUSH, .gitignore.claude, PR-REVIEW 문서 등 |

---

## 추천

- **이슈 번호가 있으면** 옵션 A로 나누면 리뷰·히스토리 추적이 편함.
- **빠르게 올리려면** 옵션 B로 3개 커밋.

실제로 존재하는 파일만 스테이징하면 됨. (예: `PR-REVIEW-AND-API.md`, `WHAT-TO-PUSH.md` 등이 레포에 없으면 해당 커밋에서 제외.)
