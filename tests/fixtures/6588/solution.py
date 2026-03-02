class Solution:
    _MAX = 1_000_001
    _sieve: list = []

    @classmethod
    def _build_sieve(cls) -> list:
        sieve = bytearray(cls._MAX)
        sieve[0] = sieve[1] = 1
        for i in range(2, cls._MAX):
            if not sieve[i]:
                for j in range(i * i, cls._MAX, i):
                    sieve[j] = 1
        return sieve

    def solve(self, n: int) -> str:
        if not Solution._sieve:
            Solution._sieve = self._build_sieve()
        sieve = Solution._sieve
        a = 3
        while a <= n // 2:
            if not sieve[a] and not sieve[n - a]:
                return f"{n} = {a} + {n - a}"
            a += 2
        return "Goldbach's conjecture is wrong."
