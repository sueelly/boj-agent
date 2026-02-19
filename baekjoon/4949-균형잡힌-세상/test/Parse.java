/**
 * 4949번: JSON input을 줄 단위로 나누어 '.' 전까지 각 줄에 대해 solve 호출 후 결과 이어 붙임
 */
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        String[] lines = input.split("\n");
        StringBuilder sb = new StringBuilder();
        for (String line : lines) {
            if (line.equals(".")) {
                break;
            }
            if (sb.length() > 0) {
                sb.append("\n");
            }
            sb.append(sol.solve(line));
            System.out.flush();
            System.err.flush();
        }
        return sb.toString();
    }
}
