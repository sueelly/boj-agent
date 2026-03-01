use std::io::{self, BufRead, Write};

// solve 함수를 구현하세요.
// 파싱된 인자를 받아 결과를 반환합니다.
fn solve(/* 파라미터 */) -> String {
    // TODO: 알고리즘 구현
    String::new()
}

fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = io::BufWriter::new(stdout.lock());

    let mut lines = stdin.lock().lines();

    // TODO: 입력 파싱 후 solve() 호출
    // let n: usize = lines.next().unwrap().unwrap().trim().parse().unwrap();
    // writeln!(out, "{}", solve(n)).unwrap();
}
