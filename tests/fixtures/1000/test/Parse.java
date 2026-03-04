import java.util.Scanner;
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        Scanner sc = new Scanner(input);
        int a = sc.nextInt();
        int b = sc.nextInt();
        return String.valueOf(sol.solve(a, b));
    }
}
