/**
 * 공통 테스트 러너 (C++17)
 * test/test_cases.json 을 읽고 parse_and_solve(input) 호출 후 기대값과 비교.
 * 계약: parse_and_solve(const std::string& input) -> std::string (문제 쪽에서 구현)
 */
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <regex>

std::string unescape(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\\' && i + 1 < s.size()) {
            if (s[i+1] == 'n') { out += '\n'; ++i; continue; }
            if (s[i+1] == 't') { out += '\t'; ++i; continue; }
            if (s[i+1] == '"') { out += '"'; ++i; continue; }
            if (s[i+1] == '\\') { out += '\\'; ++i; continue; }
        }
        out += s[i];
    }
    return out;
}

std::string normalize(const std::string& s) {
    std::string t;
    bool space = false;
    size_t i = 0, j = s.size();
    while (i < s.size() && (s[i] == ' ' || s[i] == '\t')) ++i;
    while (j > i && (s[j-1] == ' ' || s[j-1] == '\t')) --j;
    for (; i < j; ++i) {
        if (s[i] == ' ' || s[i] == '\t' || s[i] == '\n') { space = true; continue; }
        if (space && !t.empty()) t += ' ';
        t += s[i];
        space = false;
    }
    return t;
}

// 문제에서 구현: 입력 문자열 -> 출력 문자열
extern std::string parse_and_solve(const std::string& input);

struct TestCase {
    int id;
    std::string description;
    std::string input;
    std::string expected;
};

std::vector<TestCase> load_cases(const std::string& path) {
    std::ifstream f(path);
    if (!f) return {};
    std::stringstream buf;
    buf << f.rdbuf();
    std::string json = buf.str();
    std::vector<TestCase> cases;
    std::regex id_re("\"id\"\\s*:\\s*(\\d+)");
    std::regex desc_re("\"description\"\\s*:\\s*\"([^\"]*)\"");
    std::regex input_re("\"input\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
    std::regex expected_re("\"expected\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
    std::smatch m;
    auto it = json.cbegin();
    while (std::regex_search(it, json.cend(), m, input_re)) {
        TestCase tc;
        std::string block(it, m[0].second);
        it = m[0].second;
        if (std::regex_search(block, m, id_re)) tc.id = std::stoi(m[1].str());
        if (std::regex_search(block, m, desc_re)) tc.description = m[1].str();
        if (std::regex_search(block, m, input_re)) tc.input = unescape(m[1].str());
        if (std::regex_search(block, m, expected_re)) tc.expected = unescape(m[1].str());
        if (!tc.input.empty() || !tc.expected.empty()) cases.push_back(tc);
    }
    return cases;
}

int main() {
    std::string path = "test/test_cases.json";
    auto cases = load_cases(path);
    if (cases.empty()) {
        std::cerr << "❌ Error: test/test_cases.json 을 읽을 수 없거나 testCases가 비어 있습니다.\n";
        return 1;
    }
    int passed = 0, failed = 0;
    std::cout << "🧪 테스트 시작\n==========================================\n";
    for (const auto& tc : cases) {
        try {
            std::string result = parse_and_solve(tc.input);
            std::string nresult = normalize(result);
            std::string nexp = normalize(tc.expected);
            if (nresult == nexp) {
                ++passed;
                std::cout << "✅ 테스트 " << tc.id << ": 통과";
                if (!tc.description.empty()) std::cout << " (" << tc.description << ")";
                std::cout << "\n";
            } else {
                ++failed;
                std::cout << "❌ 테스트 " << tc.id << ": 실패\n   입력: " << tc.input << "\n   기대값: " << tc.expected << "\n   결과값: " << result << "\n";
            }
        } catch (const std::exception& e) {
            ++failed;
            std::cout << "❌ 테스트 " << tc.id << ": 에러 - " << e.what() << "\n";
        }
    }
    std::cout << "==========================================\n";
    int total = passed + failed;
    if (failed == 0 && total > 0) std::cout << "📊 결과: " << passed << "/" << total << " 통과 🎉 All Passed!\n";
    else if (total == 0) std::cout << "📊 결과: 테스트 케이스 없음\n";
    else std::cout << "📊 결과: " << passed << "/" << total << " 통과 (" << failed << "개 실패)\n";
    return failed ? 1 : 0;
}
