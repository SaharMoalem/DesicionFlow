# Golden Decision Test Cases

This directory contains golden decision test cases for regression testing.

Each test case is organized in its own directory with:
- `input.json`: The decision request input
- `expected_output.json`: The expected decision response
- `metadata.yaml`: Test case metadata (description, tags, etc.)

## Structure

```
golden/
├── decision_build_vs_buy_001/
│   ├── input.json
│   ├── expected_output.json
│   └── metadata.yaml
└── decision_vendor_selection_001/
    ├── input.json
    ├── expected_output.json
    └── metadata.yaml
```

## Usage

Golden tests are run as part of the evaluation harness (Story 5.5).


