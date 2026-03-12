#!/usr/bin/env bash
# ======================================
# [DEPRECATED] 이 스크립트는 scripts/install.py로 대체되었습니다.
# 새 설치: python3 scripts/install.py
# ======================================
# 기존 사용법: cd <boj-agent 레포> && ./src/setup-boj-cli.sh
# ======================================

echo "⚠️  이 스크립트는 deprecated 되었습니다."
echo "   새 설치 스크립트를 사용하세요: python3 scripts/install.py"
echo ""
echo "계속 진행하려면 Enter, 중단하려면 Ctrl+C"
read -r _

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BOJ_SCRIPT="$SCRIPT_DIR/boj"

# commands 실행 권한
chmod +x "$SCRIPT_DIR/commands"/*.sh 2>/dev/null || true

BIN_DIR="${BOJ_BIN_DIR:-$HOME/bin}"
mkdir -p "$BIN_DIR"
cp "$BOJ_SCRIPT" "$BIN_DIR/boj"
chmod +x "$BIN_DIR/boj"

mkdir -p "$HOME/.config/boj"
echo "$REPO_ROOT" > "$HOME/.config/boj/root"
echo "✅ $BIN_DIR/boj 에 설치했습니다. (레포 경로: $HOME/.config/boj/root)"
echo ""

if ! command -v agent &>/dev/null; then
  echo "에이전트 CLI(agent)가 없습니다. boj make / boj review 시 선택 사항입니다."
  echo "   설정: echo 'agent chat -f -p --' > ~/.config/boj/agent"
  echo ""
fi

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "⚠️  PATH에 $BIN_DIR 이 없습니다. 셸 설정에 추가하세요:"
  echo "   export PATH=\"\$HOME/bin:\$PATH\""
  if [[ -f "$HOME/.zshrc" ]]; then
    read -p "지금 .zshrc에 추가할까요? (y/N): " add_path
    if [[ "$add_path" =~ ^[Yy]$ ]]; then
      echo '' >> "$HOME/.zshrc"
      echo '# boj CLI' >> "$HOME/.zshrc"
      echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
      echo "   → .zshrc에 PATH를 추가했습니다."
    fi
  fi
  echo ""
fi

if ! grep -q 'BOJ_ROOT' "$HOME/.zshrc" 2>/dev/null; then
  read -p "어디서든 boj 를 쓰려면 BOJ_ROOT를 설정할까요? (Y/n): " add_boj_root
  if [[ "$add_boj_root" != [Nn] ]]; then
    echo '' >> "$HOME/.zshrc"
    echo '# boj-agent 레포 루트' >> "$HOME/.zshrc"
    echo "export BOJ_ROOT=\"$REPO_ROOT\"" >> "$HOME/.zshrc"
    echo "   → BOJ_ROOT=$REPO_ROOT 를 .zshrc에 추가했습니다."
  fi
  echo ""
fi

echo "사용법:"
echo "  boj run 4949      # 테스트"
echo "  boj commit 4949   # 커밋"
echo "  boj make 4949     # 환경 생성"
echo "  boj open 4949     # 문제 폴더만 열기"
echo "  boj review 4949   # 리뷰"
echo ""
echo "설정: ~/.config/boj/ (root, agent, lang, editor 등)"
echo "새 터미널을 열거나: source ~/.zshrc"
