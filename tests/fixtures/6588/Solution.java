public class Solution {
    private static final int MAX = 1_000_001;
    private static final boolean[] notPrime = new boolean[MAX];

    static {
        notPrime[0] = notPrime[1] = true;
        for (int i = 2; i < MAX; i++) {
            if (!notPrime[i]) {
                for (long j = (long) i * i; j < MAX; j += i) {
                    notPrime[(int) j] = true;
                }
            }
        }
    }

    public String solve(int n) {
        for (int a = 3; a <= n / 2; a += 2) {
            if (!notPrime[a] && !notPrime[n - a]) {
                return n + " = " + a + " + " + (n - a);
            }
        }
        return "Goldbach's conjecture is wrong.";
    }
}
