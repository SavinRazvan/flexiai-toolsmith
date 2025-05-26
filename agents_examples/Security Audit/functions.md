**Other Settings:**
- Response format: `text`
- Temperature: `1.00`
- Top P: `1.00`


**Functions:**

```json
{
  "name": "security_audit",
  "description": "Run a structured security audit operation and return JSON-formatted findings.\n\nSupported operations:\n  • reconnaissance — no additional parameters\n  • detect_processes — no additional parameters\n  • port_scan — requires `target`; optional `start_port`, `end_port`\n  • network_scan — requires `network` in CIDR notation\n  • defense_actions — optional `bad_ips`, `bad_pids`, `bad_ports`\n  • update_system — no additional parameters",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "description": "The audit operation to perform (one of: 'reconnaissance', 'detect_processes', 'port_scan', 'network_scan', 'defense_actions', 'update_system').",
        "enum": [
          "reconnaissance",
          "detect_processes",
          "port_scan",
          "network_scan",
          "defense_actions",
          "update_system"
        ],
        "optional": false
      },
      "target": {
        "type": "string",
        "description": "Hostname or IP to scan (required when 'operation' is 'port_scan').",
        "optional": true
      },
      "start_port": {
        "type": "integer",
        "description": "Lower bound of port range (inclusive, default=1; only used for 'port_scan').",
        "optional": true
      },
      "end_port": {
        "type": "integer",
        "description": "Upper bound of port range (inclusive, default=1024; only used for 'port_scan').",
        "optional": true
      },
      "network": {
        "type": "string",
        "description": "Network CIDR to scan (e.g., '192.168.1.0/24'; required when 'operation' is 'network_scan').",
        "optional": true
      },
      "bad_ips": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of IP addresses to block (only used for 'defense_actions').",
        "optional": true
      },
      "bad_pids": {
        "type": "array",
        "items": {
          "type": "integer"
        },
        "description": "List of process IDs to terminate (only used for 'defense_actions').",
        "optional": true
      },
      "bad_ports": {
        "type": "array",
        "items": {
          "type": "integer"
        },
        "description": "List of TCP ports to block (only used for 'defense_actions').",
        "optional": true
      }
    },
    "required": [
      "operation"
    ]
  }
}
```
