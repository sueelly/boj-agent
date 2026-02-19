/**
 * 문제별 JSON input → Solution.solve() 파싱 로직 인터페이스.
 * 각 문제 폴더의 Parse.java가 이 인터페이스를 구현한다.
 */
public interface ParseAndCallSolve {
    String parseAndCallSolve(Solution sol, String input);
}
