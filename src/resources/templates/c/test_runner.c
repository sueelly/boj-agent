/**
 * 공통 테스트 러너 (C11)
 * test/test_cases.json 을 읽고 parse_and_solve(input, out, size) 호출 후 기대값과 비교.
 * 계약: void parse_and_solve(const char* input, char* output, size_t out_size);
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

extern void parse_and_solve(const char* input, char* output, size_t out_size);

#define BUF_SIZE 65536
#define MAX_CASES 256

typedef struct {
    int id;
    char description[256];
    char input[BUF_SIZE];
    char expected[BUF_SIZE];
} TestCase;

static void unescape(const char* in, char* out, size_t out_len) {
    size_t j = 0;
    for (; *in && j < out_len - 1; in++) {
        if (*in == '\\' && in[1]) {
            if (in[1] == 'n') { out[j++] = '\n'; in++; continue; }
            if (in[1] == 't') { out[j++] = '\t'; in++; continue; }
            if (in[1] == '"') { out[j++] = '"'; in++; continue; }
            if (in[1] == '\\') { out[j++] = '\\'; in++; continue; }
        }
        out[j++] = *in;
    }
    out[j] = '\0';
}

static void normalize(const char* in, char* out, size_t out_len) {
    size_t j = 0;
    while (*in && isspace((unsigned char)*in)) in++;
    const char* end = in + strlen(in);
    while (end > in && isspace((unsigned char)*(end-1))) end--;
    int space = 0;
    for (; in < end && j < out_len - 1; in++) {
        if (isspace((unsigned char)*in)) { space = 1; continue; }
        if (space && j > 0) out[j++] = ' ';
        out[j++] = *in;
        space = 0;
    }
    out[j] = '\0';
}

static int load_cases(const char* path, TestCase* cases, int max_n) {
    FILE* f = fopen(path, "r");
    if (!f) return 0;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* json = malloc((size_t)len + 1);
    if (!json) { fclose(f); return 0; }
    fread(json, 1, (size_t)len, f);
    json[len] = '\0';
    fclose(f);
    int n = 0;
    char* p = strstr(json, "\"input\"");
    while (p && n < max_n) {
        p = strchr(p, '"');
        if (!p) break;
        p = strchr(p + 1, '"');
        if (!p) break;
        p += 1; /* start of value */
        char* start = p;
        while (*p && !(*p == '"' && *(p-1) != '\\')) p++;
        *p = '\0';
        unescape(start, cases[n].input, sizeof(cases[n].input));
        *p = '"';
        char* exp = strstr(p, "\"expected\"");
        if (!exp) break;
        exp = strchr(exp, '"');
        if (!exp) break;
        exp = strchr(exp + 1, '"');
        if (!exp) break;
        exp = strchr(exp + 1, '"');
        if (!exp) break;
        exp += 1;
        start = exp;
        while (*exp && !(*exp == '"' && *(exp-1) != '\\')) exp++;
        *exp = '\0';
        unescape(start, cases[n].expected, sizeof(cases[n].expected));
        *exp = '"';
        cases[n].id = n + 1;
        cases[n].description[0] = '\0';
        n++;
        p = strstr(exp + 1, "\"input\"");
    }
    free(json);
    return n;
}

int main(void) {
    TestCase cases[MAX_CASES];
    int n = load_cases("test/test_cases.json", cases, MAX_CASES);
    if (n == 0) {
        fprintf(stderr, "❌ Error: test/test_cases.json 을 읽을 수 없습니다.\n");
        return 1;
    }
    int passed = 0, failed = 0;
    char result[BUF_SIZE], nresult[BUF_SIZE], nexp[BUF_SIZE];
    printf("🧪 테스트 시작\n==========================================\n");
    for (int i = 0; i < n; i++) {
        parse_and_solve(cases[i].input, result, sizeof(result));
        normalize(result, nresult, sizeof(nresult));
        normalize(cases[i].expected, nexp, sizeof(nexp));
        if (strcmp(nresult, nexp) == 0) {
            passed++;
            printf("✅ 테스트 %d: 통과\n", cases[i].id);
        } else {
            failed++;
            printf("❌ 테스트 %d: 실패\n   기대값: %s\n   결과값: %s\n", cases[i].id, cases[i].expected, result);
        }
    }
    printf("==========================================\n");
    if (failed == 0 && n > 0)
        printf("📊 결과: %d/%d 통과 🎉 All Passed!\n", passed, n);
    else if (n == 0)
        printf("📊 결과: 테스트 케이스 없음\n");
    else
        printf("📊 결과: %d/%d 통과 (%d개 실패)\n", passed, n, failed);
    return failed ? 1 : 0;
}
