**Other Settings:**
- Response format: `text`
- Temperature: `1.00`
- Top P: `1.00`


**Functions:**

```json
{
  "name": "search_on_youtube",
  "description": "Search YouTube for the given query and return an embeddable search URL plus HTML snippets for the top N videos.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search terms to use on YouTube",
        "minLength": 1
      },
      "links_nr": {
        "type": "integer",
        "description": "Number of top video results to fetch",
        "default": 1
      }
    },
    "required": [
      "query"
    ]
  }
}
```
