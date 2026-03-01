import Foundation

// solve 함수를 구현하세요.
// 파싱된 인자를 받아 결과를 반환합니다.
func solve(/* 파라미터 */) -> String {
    // TODO: 알고리즘 구현
    return ""
}

// 빠른 입력용
var inputLines: [String] = []
var lineIndex = 0

func readLine() -> String? {
    if lineIndex < inputLines.count {
        let line = inputLines[lineIndex]
        lineIndex += 1
        return line
    }
    return nil
}

// 입력 전체 읽기
let allInput = AnyIterator { Swift.readLine() }.joined(separator: "\n")
inputLines = allInput.components(separatedBy: "\n")

// TODO: 입력 파싱 후 solve() 호출
// let n = Int(readLine()!)!
// print(solve(n))
