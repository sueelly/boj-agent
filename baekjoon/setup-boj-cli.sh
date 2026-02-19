#!/usr/bin/env bash
# ======================================
# boj CLI 설치 — 한 번 실행 후 어디서든 boj 사용
# ======================================
# 실행: cd <algorithm>/baekjoon && ./setup-boj-cli.sh
# ======================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BOJ_SCRIPT="$SCRIPT_DIR/boj"

# ~/bin 이 없으면 생성
BIN_DIR="${BOJ_BIN_DIR:-$HOME/bin}"
mkdir -p "$BIN_DIR"

# boj 스크립트 복사 및 실행 권한
cp "$BOJ_SCRIPT" "$BIN_DIR/boj"
chmod +x "$BIN_DIR/boj"

# 레포 경로를 파일로 저장 — BOJ_ROOT가 로드되지 않는 터미널(Cursor 등)에서도 boj 동작
mkdir -p "$HOME/.config/boj"
echo "$REPO_ROOT" > "$HOME/.config/boj/root"
echo "✅ $BIN_DIR/boj 에 설치했습니다. (레포 경로: $HOME/.config/boj/root)"
echo ""

# Cursor Agent CLI (boj make / boj review용)
if ! command -v agent &>/dev/null; then
  echo "Cursor Agent CLI가 없습니다. boj make / boj review 를 쓰려면 필요합니다."
  read -p "지금 설치할까요? (Y/n): " install_agent
  if [[ "$install_agent" != [Nn] ]]; then
    echo "Cursor Agent CLI 설치 중..."
    if curl -fsSL https://cursor.com/install | bash; then
      echo "   → Cursor Agent CLI 설치 완료. 새 터미널에서 'agent' 명령을 사용할 수 있습니다."
    else
      echo "   → 설치 실패. 수동 설치: curl https://cursor.com/install -fsSL | bash"
    fi
  else
    echo "   나중에 설치: curl https://cursor.com/install -fsSL | bash"
  fi
  echo ""
fi

# PATH 확인
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "⚠️  PATH에 $BIN_DIR 이 없습니다. 아래를 셸 설정 파일에 추가하세요:"
  echo ""
  if [[ -f "$HOME/.zshrc" ]]; then
    echo "   export PATH=\"\$HOME/bin:\$PATH\""
    echo ""
    read -p "지금 .zshrc에 추가할까요? (y/N): " add_path
    if [[ "$add_path" =~ ^[Yy]$ ]]; then
      echo '' >> "$HOME/.zshrc"
      echo '# boj CLI' >> "$HOME/.zshrc"
      echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
      echo "   → .zshrc에 PATH를 추가했습니다. 새 터미널에서 boj 를 사용할 수 있습니다."
    fi
  fi
fi

# BOJ_ROOT: algorithm 루트 설정 (어디서든 boj 사용 시 필요)
if ! grep -q 'BOJ_ROOT' "$HOME/.zshrc" 2>/dev/null; then
  echo ""
  read -p "어디서든 'boj' 를 쓰려면 BOJ_ROOT를 설정해야 합니다. 지금 추가할까요? (Y/n): " add_boj_root
  if [[ "$add_boj_root" != [Nn] ]]; then
    echo '' >> "$HOME/.zshrc"
    echo '# boj: algorithm repo 루트 (boj make/review 등 어디서든 사용)' >> "$HOME/.zshrc"
    echo "export BOJ_ROOT=\"$REPO_ROOT\"" >> "$HOME/.zshrc"
    echo "   → BOJ_ROOT=$REPO_ROOT 를 .zshrc에 추가했습니다."
  fi
fi

echo ""
echo "사용법:"
echo "  boj run 4949          # 테스트"
echo "  boj commit 4949       # 커밋"
echo "  boj make 4949         # Cursor Agent로 환경 생성 (또는 에디터+클립보드)"
echo "  boj review 4949       # Cursor Agent로 리뷰 (또는 에디터+클립보드)"
echo ""
echo "새 터미널을 열거나: source ~/.zshrc"
