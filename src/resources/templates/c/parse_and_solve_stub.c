/**
 * 문제별 test/parse_and_solve.c 가 구현할 계약:
 *   void parse_and_solve(const char* input, char* output, size_t out_size);
 * output 에 null 종료 문자열로 결과 저장.
 */
#include <stddef.h>

void parse_and_solve(const char* input, char* output, size_t out_size) {
    (void)input;
    if (out_size > 0) output[0] = '\0';
}
