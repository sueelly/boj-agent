import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/**
 * JSON 기반 테스트 러너
 * test_cases.json 파일을 읽어서 테스트 수행
 * 
 * 이 파일은 수정할 필요 없음!
 * 테스트 케이스는 test_cases.json에 추가하면 됨
 */
public class Test {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        try {
            // JSON 파일 읽기
            String jsonContent = new String(Files.readAllBytes(Paths.get("test_cases.json")));
            
            // 테스트 케이스 파싱 및 실행
            runTests(jsonContent);
            
            // 결과 출력
            printSummary();
            
        } catch (IOException e) {
            System.err.println("❌ Error: test_cases.json 파일을 읽을 수 없습니다.");
            System.err.println("   " + e.getMessage());
            System.exit(1);
        }
    }

    private static void runTests(String jsonContent) {
        Solution sol = new Solution();
        
        System.out.println("🧪 테스트 시작");
        System.out.println("==========================================");
        
        // 간단한 JSON 파싱 (testCases 배열 추출)
        List<TestCase> testCases = parseTestCases(jsonContent);
        
        for (TestCase tc : testCases) {
            runSingleTest(sol, tc);
        }
    }

    private static void runSingleTest(Solution sol, TestCase tc) {
        try {
            // Solution의 solve 메서드 호출
            String result = callSolve(sol, tc.input);
            
            // 결과 비교 (공백 정규화 후 비교)
            String normalizedResult = normalizeOutput(result);
            String normalizedExpected = normalizeOutput(tc.expected);
            
            boolean isPassed = normalizedResult.equals(normalizedExpected);
            
            if (isPassed) {
                passed++;
                System.out.printf("✅ 테스트 %d: 통과", tc.id);
                if (tc.description != null && !tc.description.isEmpty()) {
                    System.out.printf(" (%s)", tc.description);
                }
                System.out.println();
            } else {
                failed++;
                System.out.printf("❌ 테스트 %d: 실패", tc.id);
                if (tc.description != null && !tc.description.isEmpty()) {
                    System.out.printf(" (%s)", tc.description);
                }
                System.out.println();
                System.out.printf("   입력: %s%n", tc.input);
                System.out.printf("   기대값: %s%n", tc.expected);
                System.out.printf("   결과값: %s%n", result);
            }
        } catch (Exception e) {
            failed++;
            System.out.printf("❌ 테스트 %d: 에러 발생%n", tc.id);
            System.out.printf("   입력: %s%n", tc.input);
            System.out.printf("   에러: %s%n", e.getMessage());
        }
    }

    /**
     * Solution.solve() 호출하고 결과를 문자열로 반환
     * Solution의 반환 타입에 따라 적절히 변환
     */
    private static String callSolve(Solution sol, String input) {
        return sol.solve(Arrays.stream(input.split(" ")).mapToInt(Integer::parseInt).toArray());
    }

    /**
     * 결과를 문자열로 포맷팅
     */
    private static String formatResult(Object result) {
        if (result == null) {
            return "null";
        }
        
        if (result instanceof int[]) {
            int[] arr = (int[]) result;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < arr.length; i++) {
                sb.append(arr[i]);
                if (i < arr.length - 1) sb.append(" ");
            }
            return sb.toString();
        }
        
        if (result instanceof long[]) {
            long[] arr = (long[]) result;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < arr.length; i++) {
                sb.append(arr[i]);
                if (i < arr.length - 1) sb.append(" ");
            }
            return sb.toString();
        }
        
        if (result instanceof String[]) {
            return String.join(" ", (String[]) result);
        }
        
        if (result instanceof List) {
            List<?> list = (List<?>) result;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < list.size(); i++) {
                sb.append(list.get(i));
                if (i < list.size() - 1) sb.append(" ");
            }
            return sb.toString();
        }
        
        return result.toString();
    }

    /**
     * 출력 정규화 (비교를 위해)
     */
    private static String normalizeOutput(String output) {
        return output.trim().replaceAll("\\s+", " ");
    }

    /**
     * 간단한 JSON 파서 (외부 라이브러리 없이)
     */
    private static List<TestCase> parseTestCases(String json) {
        List<TestCase> testCases = new ArrayList<>();
        
        // testCases 배열 찾기
        Pattern arrayPattern = Pattern.compile("\"testCases\"\\s*:\\s*\\[([\\s\\S]*?)\\]\\s*\\}", Pattern.MULTILINE);
        Matcher arrayMatcher = arrayPattern.matcher(json);
        
        if (!arrayMatcher.find()) {
            System.err.println("⚠️ Warning: testCases 배열을 찾을 수 없습니다.");
            return testCases;
        }
        
        String arrayContent = arrayMatcher.group(1);
        
        // 각 테스트 케이스 객체 파싱
        Pattern objPattern = Pattern.compile("\\{([^{}]*)\\}");
        Matcher objMatcher = objPattern.matcher(arrayContent);
        
        while (objMatcher.find()) {
            String objContent = objMatcher.group(1);
            TestCase tc = new TestCase();
            
            // id 추출
            Pattern idPattern = Pattern.compile("\"id\"\\s*:\\s*(\\d+)");
            Matcher idMatcher = idPattern.matcher(objContent);
            if (idMatcher.find()) {
                tc.id = Integer.parseInt(idMatcher.group(1));
            }
            
            // description 추출
            Pattern descPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]*)\"");
            Matcher descMatcher = descPattern.matcher(objContent);
            if (descMatcher.find()) {
                tc.description = descMatcher.group(1);
            }
            
            // input 추출
            Pattern inputPattern = Pattern.compile("\"input\"\\s*:\\s*\"([^\"]*)\"");
            Matcher inputMatcher = inputPattern.matcher(objContent);
            if (inputMatcher.find()) {
                tc.input = unescapeJson(inputMatcher.group(1));
            }
            
            // expected 추출
            Pattern expectedPattern = Pattern.compile("\"expected\"\\s*:\\s*\"([^\"]*)\"");
            Matcher expectedMatcher = expectedPattern.matcher(objContent);
            if (expectedMatcher.find()) {
                tc.expected = unescapeJson(expectedMatcher.group(1));
            }
            
            if (tc.input != null && tc.expected != null) {
                testCases.add(tc);
            }
        }
        
        return testCases;
    }

    /**
     * JSON 이스케이프 문자 처리
     */
    private static String unescapeJson(String str) {
        return str.replace("\\n", "\n")
                  .replace("\\t", "\t")
                  .replace("\\\"", "\"")
                  .replace("\\\\", "\\");
    }

    private static void printSummary() {
        System.out.println("==========================================");
        int total = passed + failed;
        System.out.printf("📊 결과: %d/%d 통과", passed, total);
        
        if (failed == 0 && total > 0) {
            System.out.println(" 🎉 All Passed!");
        } else if (total == 0) {
            System.out.println(" (테스트 케이스 없음)");
        } else {
            System.out.printf(" (%d개 실패)%n", failed);
        }
    }

    static class TestCase {
        int id;
        String description;
        String input;
        String expected;
    }
}
