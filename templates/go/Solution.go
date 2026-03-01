package main

import (
	"bufio"
	"fmt"
	"os"
)

var reader *bufio.Reader
var writer *bufio.Writer

// solve 함수를 구현하세요.
// 파싱된 인자를 받아 결과를 반환합니다.
func solve( /* 파라미터 */ ) interface{} {
	// TODO: 알고리즘 구현
	return nil
}

func main() {
	reader = bufio.NewReader(os.Stdin)
	writer = bufio.NewWriter(os.Stdout)
	defer writer.Flush()

	// TODO: 입력 파싱 후 solve() 호출
	// var n int
	// fmt.Fscan(reader, &n)
	// fmt.Fprintln(writer, solve(n))
}
