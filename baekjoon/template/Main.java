import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.StringTokenizer;

/**
 * 백준 제출용 메인 클래스
 * 
 * 역할: 표준 입력 파싱 → Solution 호출 → 표준 출력
 * Solution에는 파싱된 값들을 직접 전달
 */
public class Main {

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(System.out));
        
        // ===== 입력 파싱 (문제에 맞게 수정) =====
        
        // 예시 1: 한 줄에 정수 하나
        // int n = Integer.parseInt(br.readLine().trim());
        
        // 예시 2: 한 줄에 공백으로 구분된 여러 정수
        // StringTokenizer st = new StringTokenizer(br.readLine());
        // int a = Integer.parseInt(st.nextToken());
        // int b = Integer.parseInt(st.nextToken());
        
        // 예시 3: n, 배열, x (3273번 두 수의 합)
        // int n = Integer.parseInt(br.readLine().trim());
        // int[] arr = new int[n];
        // StringTokenizer st = new StringTokenizer(br.readLine());
        // for (int i = 0; i < n; i++) {
        //     arr[i] = Integer.parseInt(st.nextToken());
        // }
        // int x = Integer.parseInt(br.readLine().trim());
        
        // ===== Solution 호출 =====
        Solution sol = new Solution();
        // int result = sol.solve(파라미터들);
        
        // ===== 출력 =====
        // bw.write(String.valueOf(result));
        // bw.newLine();
        
        bw.flush();
        bw.close();
        br.close();
    }
}
