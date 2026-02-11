import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/**
 * JSON 기반 테스트 러너
 * 
 * test_cases.json의 input 문자열을 파싱하여 Solution에 전달
 * 
 * ⚠️ 문제마다 parseAndCallSolve() 메서드를 수정해야 함!
 */
public class Test {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        try {
            String jsonContent = new String(Files.readAllBytes(Paths.get("test_cases.json")));
            runTests(jsonContent);
            printSummary();
        } catch (IOException e) {
            System.err.println("❌ Error: test_cases.json 파일을 읽을 수 없습니다.");
            System.exit(1);
        }
    }

    /**
     * ⚠️ 문제마다 이 메서드를 수정해야 함!
     * 
     * input 문자열을 파싱하여 Solution.solve()에 전달하고 결과 반환
     */
    private static String parseAndCallSolve(Solution sol, String input) {
        // 예시: 3273번 두 수의 합
        // String[] lines = input.split("\n");
        // int n = Integer.parseInt(lines[0].trim());
        // int[] arr = Arrays.stream(lines[1].split(" ")).mapToInt(Integer::parseInt).toArray();
        // int x = Integer.parseInt(lines[2].trim());
        // return String.valueOf(sol.solve(n, arr, x));
        
        // TODO: 문제에 맞게 파싱 로직 작성
        return "";
    }

    // ========== 아래는 수정 불필요 ==========

    private static void runTests(String jsonContent) {
        Solution sol = new Solution();
        
        System.out.println("🧪 테스트 시작");
        System.out.println("==========================================");
        
        List<TestCase> testCases = parseTestCases(jsonContent);
        
        for (TestCase tc : testCases) {
            runSingleTest(sol, tc);
        }
    }

    private static void runSingleTest(Solution sol, TestCase tc) {
        try {
            String result = parseAndCallSolve(sol, tc.input);
            
            String normalizedResult = normalizeOutput(result);
            String normalizedExpected = normalizeOutput(tc.expected);
            
            boolean isPassed = normalizedResult.equals(normalizedExpected);
            
            if (isPassed) {
                passed++;
                System.out.printf("✅ 테스트 %d: 통과", tc.id);
            } else {
                failed++;
                System.out.printf("❌ 테스트 %d: 실패%n", tc.id);
                System.out.printf("   입력: %s%n", tc.input.replace("\n", "\\n"));
                System.out.printf("   기대값: %s%n", tc.expected);
                System.out.printf("   결과값: %s%n", result);
            }
            
            if (tc.description != null && !tc.description.isEmpty()) {
                System.out.printf(" (%s)", tc.description);
            }
            System.out.println();
            
        } catch (Exception e) {
            failed++;
            System.out.printf("❌ 테스트 %d: 에러 - %s%n", tc.id, e.getMessage());
        }
    }

    private static String normalizeOutput(String output) {
        return output.trim().replaceAll("\\s+", " ");
    }

    private static List<TestCase> parseTestCases(String json) {
        List<TestCase> testCases = new ArrayList<>();
        
        Pattern arrayPattern = Pattern.compile("\"testCases\"\\s*:\\s*\\[([\\s\\S]*?)\\]\\s*\\}", Pattern.MULTILINE);
        Matcher arrayMatcher = arrayPattern.matcher(json);
        
        if (!arrayMatcher.find()) {
            System.err.println("⚠️ Warning: testCases 배열을 찾을 수 없습니다.");
            return testCases;
        }
        
        String arrayContent = arrayMatcher.group(1);
        Pattern objPattern = Pattern.compile("\\{([^{}]*)\\}");
        Matcher objMatcher = objPattern.matcher(arrayContent);
        
        while (objMatcher.find()) {
            String objContent = objMatcher.group(1);
            TestCase tc = new TestCase();
            
            Pattern idPattern = Pattern.compile("\"id\"\\s*:\\s*(\\d+)");
            Matcher idMatcher = idPattern.matcher(objContent);
            if (idMatcher.find()) tc.id = Integer.parseInt(idMatcher.group(1));
            
            Pattern descPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]*)\"");
            Matcher descMatcher = descPattern.matcher(objContent);
            if (descMatcher.find()) tc.description = descMatcher.group(1);
            
            Pattern inputPattern = Pattern.compile("\"input\"\\s*:\\s*\"([^\"]*)\"");
            Matcher inputMatcher = inputPattern.matcher(objContent);
            if (inputMatcher.find()) tc.input = unescapeJson(inputMatcher.group(1));
            
            Pattern expectedPattern = Pattern.compile("\"expected\"\\s*:\\s*\"([^\"]*)\"");
            Matcher expectedMatcher = expectedPattern.matcher(objContent);
            if (expectedMatcher.find()) tc.expected = unescapeJson(expectedMatcher.group(1));
            
            if (tc.input != null && tc.expected != null) testCases.add(tc);
        }
        
        return testCases;
    }

    private static String unescapeJson(String str) {
        return str.replace("\\n", "\n").replace("\\t", "\t")
                  .replace("\\\"", "\"").replace("\\\\", "\\");
    }

    private static void printSummary() {
        System.out.println("==========================================");
        int total = passed + failed;
        System.out.printf("📊 결과: %d/%d 통과", passed, total);
        if (failed == 0 && total > 0) System.out.println(" 🎉 All Passed!");
        else if (total == 0) System.out.println(" (테스트 케이스 없음)");
        else System.out.printf(" (%d개 실패)%n", failed);
    }

    static class TestCase {
        int id;
        String description;
        String input;
        String expected;
    }
}
