/**
 * 1475번: 방 번호 - JSON input(숫자 문자열)을 int로 파싱 후 Solution.solve(n) 호출
 */
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        int n = Integer.parseInt(input.trim());
        return String.valueOf(sol.solve(n));
    }
}
