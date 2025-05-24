**Other Settings:**
- Response format: `text`
- Temperature: `1.00`
- Top P: `1.00`


**Functions:**


```json
{
  "name": "csv_operations",
  "description": "Universal CSV dispatcher. Perform any CRUD or query operation on a CSV by supplying `operation` plus only the parameters needed for that operation.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": [
          "create",
          "delete",
          "read",
          "read_row",
          "read_column",
          "summary",
          "append_row",
          "append_rows",
          "update_cell",
          "delete_row",
          "filter_rows",
          "validate"
        ],
        "description": "Which CSV operation to invoke. One of: create, delete, read, read_row, read_column, summary, append_row, append_rows, update_cell, delete_row, filter_rows, validate."
      },
      "path": {
        "type": "string",
        "description": "Directory path where the CSV files reside (all operations)."
      },
      "file_name": {
        "type": "string",
        "description": "Name of the CSV file to operate on (all operations). Supported files: `identify_subscriber.csv`, `manage_services.csv`, `retrieve_billing_details.csv`."
      },
      "index": {
        "type": "integer",
        "description": "Zero‑based row index, used by `read_row`, `update_cell`, and `delete_row`."
      },
      "column": {
        "oneOf": [
          {
            "type": "string"
          },
          {
            "type": "integer"
          }
        ],
        "description": "Column name or zero‑based index, used by `read_column`, `filter_rows`, and `update_cell`."
      },
      "row": {
        "type": "object",
        "description": "Mapping of column→value for a single row; used by `append_row`."
      },
      "rows": {
        "type": "array",
        "items": {
          "type": "object"
        },
        "description": "List of row mappings; used by `append_rows`."
      },
      "value": {
        "type": [
          "string",
          "number",
          "boolean",
          "null"
        ],
        "description": "New cell value; required by `update_cell`."
      },
      "condition_type": {
        "type": "string",
        "enum": [
          "equals",
          "greater_than",
          "less_than",
          "contains",
          "startswith",
          "endswith"
        ],
        "description": "Filter condition type; used by `filter_rows`."
      },
      "condition_value": {
        "type": [
          "string",
          "number"
        ],
        "description": "Value to compare against; used by `filter_rows`."
      },
      "headers": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of column names for a new CSV; used by `create`."
      },
      "required_columns": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of columns to validate existence; used by `validate`."
      }
    },
    "required": [
      "operation",
      "file_name"
    ]
  }
}
```

---
