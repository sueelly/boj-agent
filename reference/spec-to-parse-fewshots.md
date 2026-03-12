# Spec to Parse Few-Shot Examples

이 문서는 `problem.spec.json` 에서 `test/Parse.java` 를 만드는 few-shot 예시를 담는다.

예시는 설명보다 **최종 코드 모양**을 학습시키기 위한 것이다.
상위 규칙과 충돌하면 규칙이 우선한다.

---

## Few-shot 1. Array sum

### Simplified spec
```json
{
  "input": {
    "locals": [{ "name": "n", "type": "int" }],
    "model": {
      "kind": "array",
      "element": { "kind": "scalar", "type": "int" },
      "lengthFrom": "n",
      "readAs": "tokens"
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "token"
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "long" },
    "presentation": { "style": "single_line_scalar" }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      {
        "name": "nums",
        "type": {
          "kind": "array",
          "element": { "kind": "scalar", "type": "int" },
          "lengthFrom": "n",
          "readAs": "tokens"
        }
      }
    ],
    "returnStyle": "direct_model"
  }
}
```

### Expected Parse.java core
```java
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);

        int n = in.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = in.nextInt();

        long result = sol.solve(nums);
        return String.valueOf(result);
    }
}
```

---

## Few-shot 2. Graph edge list

### Simplified spec
```json
{
  "input": {
    "locals": [
      { "name": "n", "type": "int" },
      { "name": "m", "type": "int" }
    ],
    "model": {
      "kind": "record",
      "name": "Input",
      "fields": [
        { "name": "n", "type": { "kind": "scalar", "type": "int" } },
        {
          "name": "edges",
          "type": {
            "kind": "array",
            "lengthFrom": "m",
            "readAs": "tokens",
            "element": {
              "kind": "record",
              "name": "WeightedEdge",
              "fields": [
                { "name": "from", "type": { "kind": "scalar", "type": "int" } },
                { "name": "to", "type": { "kind": "scalar", "type": "int" } },
                { "name": "weight", "type": { "kind": "scalar", "type": "int" } }
              ]
            }
          }
        }
      ]
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "token"
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "long" },
    "presentation": { "style": "single_line_scalar" }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      { "name": "n", "type": { "kind": "scalar", "type": "int" } },
      {
        "name": "edges",
        "type": {
          "kind": "array",
          "lengthFrom": "m",
          "readAs": "tokens",
          "element": {
            "kind": "record",
            "name": "WeightedEdge",
            "fields": [
              { "name": "from", "type": { "kind": "scalar", "type": "int" } },
              { "name": "to", "type": { "kind": "scalar", "type": "int" } },
              { "name": "weight", "type": { "kind": "scalar", "type": "int" } }
            ]
          }
        }
      }
    ],
    "returnStyle": "direct_model"
  }
}
```

### Expected Parse.java core
```java
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);

        int n = in.nextInt();
        int m = in.nextInt();
        WeightedEdge[] edges = new WeightedEdge[m];
        for (int i = 0; i < m; i++) {
            edges[i] = new WeightedEdge(in.nextInt(), in.nextInt(), in.nextInt());
        }

        long result = sol.solve(n, edges);
        return String.valueOf(result);
    }
}
```

---

## Few-shot 3. Character board

### Simplified spec
```json
{
  "input": {
    "locals": [
      { "name": "n", "type": "int" },
      { "name": "m", "type": "int" }
    ],
    "model": {
      "kind": "matrix",
      "cellType": "char",
      "rowsFrom": "n",
      "colsFrom": "m",
      "rowEncoding": "char_line"
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "mixed"
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "int" },
    "presentation": { "style": "single_line_scalar" }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      {
        "name": "board",
        "type": {
          "kind": "matrix",
          "cellType": "char",
          "rowsFrom": "n",
          "colsFrom": "m",
          "rowEncoding": "char_line"
        }
      }
    ],
    "returnStyle": "direct_model"
  }
}
```

### Expected Parse.java core
```java
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);

        int n = in.nextInt();
        int m = in.nextInt();
        char[][] board = new char[n][];
        for (int i = 0; i < n; i++) {
            board[i] = in.next().toCharArray();
        }

        int result = sol.solve(board);
        return String.valueOf(result);
    }
}
```

---

## Few-shot 4. Query stream with line parsing

### Simplified spec
```json
{
  "input": {
    "locals": [{ "name": "q", "type": "int" }],
    "model": {
      "kind": "array",
      "lengthFrom": "q",
      "readAs": "lines",
      "element": {
        "kind": "tagged_union",
        "name": "Query",
        "tagField": "op",
        "tagType": "string",
        "variants": [
          {
            "tagValue": "push",
            "name": "Push",
            "fields": [
              { "name": "x", "type": { "kind": "scalar", "type": "int" } }
            ]
          },
          { "tagValue": "pop", "name": "Pop", "fields": [] }
        ]
      }
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "mixed"
    }
  },
  "output": {
    "model": {
      "kind": "array",
      "element": { "kind": "scalar", "type": "int" }
    },
    "presentation": { "style": "one_per_line" }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      {
        "name": "queries",
        "type": {
          "kind": "array",
          "lengthFrom": "q",
          "readAs": "lines",
          "element": {
            "kind": "tagged_union",
            "name": "Query",
            "tagField": "op",
            "tagType": "string",
            "variants": [
              {
                "tagValue": "push",
                "name": "Push",
                "fields": [
                  { "name": "x", "type": { "kind": "scalar", "type": "int" } }
                ]
              },
              { "tagValue": "pop", "name": "Pop", "fields": [] }
            ]
          }
        }
      }
    ],
    "returnStyle": "direct_model"
  }
}
```

### Expected Parse.java core
```java
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);

        int q = in.nextInt();
        in.nextLine();

        Query[] queries = new Query[q];
        for (int i = 0; i < q; i++) {
            String line = in.nextLine();
            StringTokenizer st = new StringTokenizer(line);
            String op = st.nextToken();
            switch (op) {
                case "push":
                    queries[i] = new Push(Integer.parseInt(st.nextToken()));
                    break;
                case "pop":
                    queries[i] = new Pop();
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + op);
            }
        }

        int[] result = sol.solve(queries);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append('\n');
            sb.append(result[i]);
        }
        return sb.toString();
    }
}
```

---

## Few-shot 5. output_record + multi_section

### Simplified spec
```json
{
  "input": {
    "model": {
      "kind": "record",
      "name": "Input",
      "fields": [
        { "name": "n", "type": { "kind": "scalar", "type": "int" } }
      ]
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "token"
    }
  },
  "output": {
    "model": {
      "kind": "record",
      "name": "Output",
      "fields": [
        { "name": "count", "type": { "kind": "scalar", "type": "int" } },
        {
          "name": "path",
          "type": {
            "kind": "array",
            "element": { "kind": "scalar", "type": "int" }
          }
        }
      ]
    },
    "presentation": {
      "style": "multi_section",
      "sections": [
        { "field": "count", "style": "single_line_scalar" },
        { "field": "path", "style": "space_separated_single_line", "separator": " " }
      ]
    }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "input_record",
    "returnStyle": "output_record"
  }
}
```

### Expected Parse.java core
```java
public class Parse implements ParseAndCallSolve {
    @Override
    public String parseAndCallSolve(Solution sol, String input) {
        InputReader in = new InputReader(input);

        int n = in.nextInt();
        Input data = new Input(n);
        Output result = sol.solve(data);

        StringBuilder sb = new StringBuilder();
        sb.append(result.count());
        sb.append('\n');
        for (int i = 0; i < result.path().length; i++) {
            if (i > 0) sb.append(' ');
            sb.append(result.path()[i]);
        }
        return sb.toString();
    }
}
```

---

## Few-shot 6. test_cases.json

### When sample I/O exists
Use this exact shape:

```json
{
  "testCases": [
    {
      "id": 1,
      "description": "sample",
      "input": "8\n20\n42\n0",
      "expected": "8 = 3 + 5\n20 = 3 + 17\n42 = 5 + 37"
    }
  ]
}
```

### Important
- keep literal newlines escaped as `\n`
- never invent `expected`
- multiple sample cases become multiple objects in `testCases`
