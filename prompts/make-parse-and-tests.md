# Spec to Parse.java / test_cases.json Generator

You are a generator for this BOJ local test harness.

Your input is an already-created `problem.spec.json`.
Your job is to generate files for the following harness shape:

- `test/Parse.java`
- optionally `test/test_cases.json`

Do NOT generate full BOJ `Main.java`.
Do NOT rewrite `Test.java`.
Do NOT rewrite `ParseAndCallSolve.java`.
Do NOT rewrite `Solution.java` except when the user explicitly asks for a stub.

---

## Files you must read before generating anything

Read these in order:

1. `reference/spec/problem-spec-contract.md`
2. `reference/spec/spec-to-parse-rules.md`
3. `reference/spec/parse-pattern-catalog.md`
4. `reference/spec/output-format-catalog.md`
5. `reference/spec/spec-to-parse-fewshots.md`
6. the target `problem.spec.json`
7. existing `Solution.java` if present

Priority order when conflicts happen:
- explicit user instruction
- `problem.spec.json`
- `reference/spec/spec-to-parse-rules.md`
- catalogs
- fewshots

If `Solution.java` exists and its `solve(...)` signature conflicts with `problem.spec.json`, stop and report the mismatch instead of guessing.

---

## Goal

Generate a problem-specific `test/Parse.java` that:

1. implements `ParseAndCallSolve`
2. parses the raw BOJ-style stdin string passed as `input`
3. calls `Solution.solve(...)` with the correct parameters
4. converts the return value to the exact stdout string format required by the spec
5. returns that final string

When sample cases are available from the user or from nearby files, you may also generate `test/test_cases.json`.
If no sample input/output is available, do not invent expected outputs.
You may generate a template with empty expected strings only if the user explicitly asks for it.

---

## Required output behavior

### If only `Parse.java` can be generated safely
Output only the content for `test/Parse.java`.

### If both `Parse.java` and `test_cases.json` can be generated safely
Output both clearly labeled file contents.

### If the spec is insufficient
Do not hallucinate.
Report exactly what field is missing or ambiguous.

---

## Required Parse.java shape

The generated file must compile on Java 11+.

It must follow this overall structure:

```java
import java.io.*;
import java.math.*;
import java.util.*;

public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);
        // parse according to spec
        // call sol.solve(...)
        // format according to spec.output.presentation
        // return final string
    }

    // helper methods if needed

    static final class InputReader {
        ...
    }
}
```

You may omit unused imports.

---

## Core translation rules

### 1. Parsing source
Always parse from the given `String input`.
Do not read from `System.in`.

### 2. User API shape
Use `problem.spec.json.userApi` to decide how to call `sol.solve(...)`.

- `inputStyle = flatten` -> pass flattened parameters in order
- `inputStyle = input_record` -> pass a single `Input` object
- `returnStyle = direct_model` -> format the direct return value
- `returnStyle = output_record` -> format the `Output` record

### 3. Input parsing
Use `problem.spec.json.input` for parsing decisions.
Important fields:
- `locals`
- `model`
- `stream`
- `normalization`

If the spec contains parse-only locals, parse them but do not pass them to `solve(...)` unless they are visible in the logical model or in flattened parameters.

### 4. Output formatting
Use `problem.spec.json.output.presentation` only.
Do not infer stdout format from return type alone.

### 5. Determinism
If parsing order is not deterministically recoverable from the spec, fail rather than guessing.

---

## InputReader requirements

Generate a lightweight string-based reader inside `Parse.java`.
It must support at least:

- `String next()`
- `int nextInt()`
- `long nextLong()`
- `double nextDouble()`
- `String nextLine()`
- `boolean hasNext()`

It must correctly support mixed usage of token-based and line-based reading.

---

## Scalar mapping

Use these defaults:

- `int` -> `in.nextInt()`
- `long` -> `in.nextLong()`
- `double` -> `in.nextDouble()`
- `string` -> token mode: `in.next()` / line mode: `in.nextLine()`
- `char` -> token mode: `in.next().charAt(0)`
- `bigint` -> `new BigInteger(in.next())`
- `bigdecimal` -> `new BigDecimal(in.next())`

Never use reflection to map values.

---

## Formatting rules

Use `problem.spec.json.output.presentation.style`.
Supported default styles:

- `single_line_scalar`
- `boolean_mapping`
- `space_separated_single_line`
- `one_per_line`
- `matrix_rows`
- `fixed_precision_scalar`
- `single_line_record`
- `multi_section`
- `raw_block`

If an unsupported style appears, stop and report it.

---

## test_cases.json generation rules

Generate `test/test_cases.json` only when input/output examples are explicitly available.

Expected shape:

```json
{
  "testCases": [
    {
      "id": 1,
      "description": "sample",
      "input": "...",
      "expected": "..."
    }
  ]
}
```

Rules:
- preserve newlines as `\n`
- do not invent expected outputs
- do not generate random cases unless explicitly requested

---

## Anti-patterns

Do NOT do the following:

1. Read from `System.in`
2. Print directly to `System.out` inside `parseAndCallSolve`
3. Use reflection to discover `solve(...)`
4. Return `null` for unimplemented formatting
5. Infer output formatting from Java return type only
6. Ignore `userApi` and call a guessed signature
7. Swallow malformed-spec errors silently
8. Modify common harness files

---

## Final checklist before producing Parse.java

1. Does `Parse` implement `ParseAndCallSolve`?
2. Does it parse from the input string only?
3. Does it call the exact `solve(...)` signature described by the spec?
4. Does it preserve BOJ stdout formatting exactly?
5. Does it compile on Java 11+?
6. Does it avoid reflection?
7. Does it avoid writing to stdout?
8. If `test_cases.json` is generated, are all expected outputs sourced from real samples?

Produce only the requested file contents.
