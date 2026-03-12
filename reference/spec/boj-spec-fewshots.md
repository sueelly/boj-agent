# BOJ Spec Few-Shot Examples

이 문서는 BOJ 문제 설명 일부를 보고 최종 `problem.spec.json`을 어떻게 구성하는지 보여주는 예시 모음입니다.

상위 우선순위:
- `problem-spec-format.md`
- `boj-spec-rules.md`

이 문서는 그 다음입니다.

---

## Few-shot 1. A + B

### Statement excerpt
- The first line contains two integers A and B.
- Print A + B.

### Expected interpretation
- simple scalar tuple input
- scalar output
- flatten input API
- direct scalar return

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "1000",
    "title": "A+B"
  },
  "input": {
    "locals": [],
    "model": {
      "kind": "record",
      "name": "Input",
      "fields": [
        { "name": "a", "type": { "kind": "scalar", "type": "int" } },
        { "name": "b", "type": { "kind": "scalar", "type": "int" } }
      ]
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "token"
    },
    "normalization": {
      "hiddenLocals": []
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "int" },
    "presentation": {
      "style": "single_line_scalar"
    }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      { "name": "a", "type": { "kind": "scalar", "type": "int" } },
      { "name": "b", "type": { "kind": "scalar", "type": "int" } }
    ],
    "returnStyle": "direct_model"
  }
}
```

---

## Few-shot 2. N followed by N integers

### Statement excerpt
- The first line contains N.
- The second line contains N integers.
- Print their sum.

### Expected interpretation
- `n` is count-only
- logical input is the integer array
- scalar output

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X001",
    "title": "Sum of Sequence"
  },
  "input": {
    "locals": [
      { "name": "n", "type": "int" }
    ],
    "model": {
      "kind": "array",
      "element": { "kind": "scalar", "type": "int" },
      "lengthFrom": "n",
      "readAs": "tokens"
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "token"
    },
    "normalization": {
      "hiddenLocals": ["n"]
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "long" },
    "presentation": {
      "style": "single_line_scalar"
    }
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
  },
  "notes": [
    "Hid n because it only describes the sequence length."
  ]
}
```

---

## Few-shot 3. Character board

### Statement excerpt
- The first line contains N and M.
- The next N lines each contain a string of length M.
- The board contains '.', '#', 'S', and 'E'.
- Print the minimum distance.

### Expected interpretation
- character board
- dimensions may stay hidden
- scalar output

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X002",
    "title": "Board Shortest Path"
  },
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
    },
    "normalization": {
      "hiddenLocals": ["n", "m"]
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "int" },
    "presentation": {
      "style": "single_line_scalar"
    }
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
  },
  "notes": [
    "Used char matrix because the board is manipulated cell-by-cell."
  ]
}
```

---

## Few-shot 4. Weighted graph

### Statement excerpt
- The first line contains N and M.
- The next M lines contain A B C, meaning an edge from A to B with cost C.
- Find the shortest path cost from 1 to N.

### Expected interpretation
- graph remains raw
- keep n visible
- use named record array for edges

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X003",
    "title": "Weighted Shortest Path"
  },
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
    },
    "normalization": {
      "hiddenLocals": ["m"],
      "indexBase": 1
    }
  },
  "output": {
    "model": { "kind": "scalar", "type": "long" },
    "presentation": {
      "style": "single_line_scalar"
    }
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
  },
  "notes": [
    "Kept n visible because graph algorithms usually require vertex count explicitly."
  ]
}
```

---

## Few-shot 5. Query stream

### Statement excerpt
- The first line contains Q.
- The next Q lines contain one command:
  - push X
  - pop
  - top
  - size
  - empty
- Print outputs only for commands that require output.

### Expected interpretation
- command stream
- query array
- tagged union
- output is homogeneous results

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X004",
    "title": "Stack Commands"
  },
  "input": {
    "locals": [
      { "name": "q", "type": "int" }
    ],
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
          {
            "tagValue": "pop",
            "name": "Pop",
            "fields": []
          },
          {
            "tagValue": "top",
            "name": "Top",
            "fields": []
          },
          {
            "tagValue": "size",
            "name": "Size",
            "fields": []
          },
          {
            "tagValue": "empty",
            "name": "Empty",
            "fields": []
          }
        ]
      }
    },
    "stream": {
      "topLevelMode": "single",
      "tokenMode": "mixed"
    },
    "normalization": {
      "hiddenLocals": ["q"]
    }
  },
  "output": {
    "model": {
      "kind": "array",
      "element": { "kind": "scalar", "type": "int" }
    },
    "presentation": {
      "style": "one_per_line"
    }
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
              {
                "tagValue": "pop",
                "name": "Pop",
                "fields": []
              },
              {
                "tagValue": "top",
                "name": "Top",
                "fields": []
              },
              {
                "tagValue": "size",
                "name": "Size",
                "fields": []
              },
              {
                "tagValue": "empty",
                "name": "Empty",
                "fields": []
              }
            ]
          }
        }
      }
    ],
    "returnStyle": "direct_model"
  }
}
```

---

## Few-shot 6. Multiple testcases

### Statement excerpt
- The first line contains T.
- For each testcase:
  - first line contains N
  - second line contains N integers
- Print one answer per testcase.

### Expected interpretation
- repeated testcase unit
- internal count-only N hidden
- output is one result per testcase

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X005",
    "title": "Repeated Sequence Problem"
  },
  "input": {
    "locals": [
      { "name": "t", "type": "int" }
    ],
    "model": {
      "kind": "array",
      "lengthFrom": "t",
      "readAs": "tokens",
      "element": {
        "kind": "record",
        "name": "TestCase",
        "fields": [
          {
            "name": "nums",
            "type": {
              "kind": "array",
              "element": { "kind": "scalar", "type": "int" },
              "lengthFrom": "n",
              "readAs": "tokens"
            }
          }
        ]
      }
    },
    "stream": {
      "topLevelMode": "testcases",
      "tokenMode": "token",
      "testcaseCountLocal": "t"
    },
    "normalization": {
      "hiddenLocals": ["t", "n"]
    }
  },
  "output": {
    "model": {
      "kind": "array",
      "element": { "kind": "scalar", "type": "long" }
    },
    "presentation": {
      "style": "one_per_line"
    }
  },
  "userApi": {
    "methodName": "solve",
    "inputStyle": "flatten",
    "flattenedParameters": [
      {
        "name": "cases",
        "type": {
          "kind": "array",
          "lengthFrom": "t",
          "readAs": "tokens",
          "element": {
            "kind": "record",
            "name": "TestCase",
            "fields": [
              {
                "name": "nums",
                "type": {
                  "kind": "array",
                  "element": { "kind": "scalar", "type": "int" },
                  "lengthFrom": "n",
                  "readAs": "tokens"
                }
              }
            ]
          }
        }
      }
    ],
    "returnStyle": "direct_model"
  },
  "notes": [
    "Each testcase hides its internal count-only n."
  ]
}
```

---

## Few-shot 7. Multi-section output

### Statement excerpt
- Print the minimum distance on the first line.
- Print the path on the second line.

### Expected interpretation
- output has multiple semantic fields
- output record
- multi-section presentation

### Spec
```json
{
  "schemaVersion": "1.0",
  "source": {
    "platform": "boj",
    "problemId": "X006",
    "title": "Shortest Path With Route"
  },
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
    },
    "normalization": {
      "hiddenLocals": ["m"],
      "indexBase": 1
    }
  },
  "output": {
    "model": {
      "kind": "record",
      "name": "Output",
      "fields": [
        { "name": "distance", "type": { "kind": "scalar", "type": "long" } },
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
        {
          "field": "distance",
          "style": "single_line_scalar"
        },
        {
          "field": "path",
          "style": "space_separated_single_line",
          "separator": " "
        }
      ]
    }
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
    "returnStyle": "output_record"
  }
}
```
