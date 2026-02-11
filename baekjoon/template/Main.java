import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.StringTokenizer;

/**
 * 백준 제출용 메인 클래스
 * 표준 입력 파싱 → Solution 호출 → 표준 출력
 */
public class Main {

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(System.out));
        
        // ===== 입력 파싱 =====
        // TODO: 문제에 맞게 입력 파싱 수정
        
        // 예시 1: 한 줄에 정수 하나
        // int n = Integer.parseInt(br.readLine().trim());
        
        // 예시 2: 한 줄에 공백으로 구분된 여러 정수
        // StringTokenizer st = new StringTokenizer(br.readLine());
        // int a = Integer.parseInt(st.nextToken());
        // int b = Integer.parseInt(st.nextToken());
        
        // 예시 3: 첫 줄에 개수, 다음 줄에 배열
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());
        
        int[] arr = new int[n];
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            arr[i] = Integer.parseInt(st.nextToken());
        }
        
        // ===== Solution 호출 =====
        Solution sol = new Solution();
        String result = sol.solve(arr);
        
        // ===== 출력 =====
        // TODO: 문제에 맞게 출력 형식 수정
        bw.write(String.valueOf(result));
        bw.newLine();
        
        bw.flush();
        bw.close();
        br.close();
    }
}
