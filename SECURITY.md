# Security Policy

## Security Model

FlexiAI Toolsmith includes tools that can inspect and modify system configurations, network settings, and running processes. This document outlines security considerations, safe usage practices, and responsible disclosure procedures.

---

## Security Warnings

### ⚠️ Dangerous Tools

The following tools require **explicit opt-in** and should be used only in controlled environments:

- **`security_audit.defense_actions`** – Can modify firewall rules, kill processes, or block network connections
- **`security_audit.update_system`** – Can trigger system updates requiring elevated privileges
- **`security_audit.port_scan`** – Can probe network hosts (may be detected as scanning activity)
- **`security_audit.network_scan`** – Can perform network discovery (may trigger security alerts)

### Safe Defaults

> **⚠️ IMPORTANT:** Currently, there is **no automatic gating** for dangerous operations in the codebase. These tools will execute if called by an assistant. 

**Recommended Implementation:**
- Add `ENABLE_DANGEROUS_TOOLS` environment variable check before executing `defense_actions` and `update_system`
- Default to `false` (disabled)
- Require explicit opt-in: `ENABLE_DANGEROUS_TOOLS=true`

**Current Behavior:**
- `defense_actions` and `update_system` will execute if called
- They require appropriate system permissions (root/admin) to succeed
- All operations are logged to `logs/security_audit.log`

**Important:** These tools should only be used by authorized operators who understand the implications. Consider implementing the opt-in flag before production use.

---

## Security Best Practices

### 1. Environment Isolation

- Run FlexiAI Toolsmith in isolated environments (containers, VMs, or dedicated systems)
- Use separate API keys for development and production
- Never commit `.env` files or API keys to version control

### 2. Access Control

- Restrict access to the web interface (use authentication if exposing publicly)
- Use strong `SECRET_KEY` values for Quart sessions
- Implement network-level restrictions (firewalls, VPNs) for production deployments

### 3. Audit Logging

All `defense_actions` operations are logged with:
- Operator identity (user_id)
- Timestamp
- Operation type and parameters
- Result status

Logs are stored in `logs/app.log` by default. For production, consider:
- Centralized logging (e.g., ELK stack, CloudWatch)
- Log retention policies
- Alerting on suspicious operations

### 4. Tool Allowlisting

Consider implementing allowlists/denylists for:
- External network targets (for port/network scans)
- Process names (for process management)
- IP addresses (for firewall rules)

---

## Data Handling & Privacy

### PII (Personally Identifiable Information)

Some tools may process PII:
- **Subscriber Management** tools access customer data from CSV files
- **Security Audit** tools may log system information that could identify users

**Recommendations:**
- Store PII data in encrypted storage
- Implement data retention policies
- Comply with applicable privacy regulations (GDPR, CCPA, etc.)
- Use environment-specific data sources (separate dev/prod)

### Data Retention

- Application logs: Configure retention based on operational needs
- Tool outputs: Consider automatic cleanup of temporary files
- CSV/Spreadsheet data: Follow your organization's data retention policies

---

## Network Security

### Inbound Connections

- Web interface (Quart): Default port 8000
  - Use reverse proxy (nginx, Traefik) for production
  - Enable HTTPS/TLS
  - Restrict access to trusted networks

### Outbound Connections

- OpenAI/Azure API calls: Ensure network access to provider endpoints
- YouTube API: Requires internet access
- Security audit tools: May make network connections for scanning

**Firewall Recommendations:**
- Allow only necessary outbound connections
- Block inbound connections except from trusted sources
- Monitor for unexpected network activity

---

## Responsible Disclosure

### Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email security concerns to: [your-security-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Resolution: Depends on severity and complexity

### Security Updates

Security updates will be:
- Released as patch versions (e.g., 1.0.1 → 1.0.2)
- Documented in CHANGELOG.md
- Tagged with security labels in releases

---

## Configuration Security

### Environment Variables

**Never commit these to version control:**
- `OPENAI_API_KEY` / `AZURE_OPENAI_API_KEY`
- `YOUTUBE_API_KEY`
- `GITHUB_TOKEN`
- `SECRET_KEY`
- Any other API keys or credentials

**Use `.env` files** (git-ignored) or secure secret management:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Environment variables in CI/CD

### Assistant IDs

- Assistant IDs are not sensitive but should not be exposed unnecessarily
- Use different assistants for dev/staging/production
- Rotate assistants if credentials are compromised

---

## Operational Security

### Production Deployment

1. **Use HTTPS** – Never expose the web interface over HTTP in production
2. **Authentication** – Implement user authentication for web access
3. **Rate Limiting** – Consider rate limiting for API endpoints
4. **Monitoring** – Set up monitoring and alerting for:
   - Failed authentication attempts
   - Unusual tool usage patterns
   - System resource exhaustion
   - Network anomalies

### Container Security

If using Docker:
- Use non-root user in containers
- Scan images for vulnerabilities
- Keep base images updated
- Use minimal base images (Alpine, distroless)

---

## Tool-Specific Security Notes

### Security Audit Tools

**Reconnaissance Operations:**
- `reconnaissance` – Read-only, safe for general use
- `detect_processes` – Read-only, safe for general use

**Network Operations:**
- `port_scan` – May trigger IDS/IPS alerts
- `network_scan` – May trigger network security alerts
- Use only on networks you own or have explicit permission to scan

**Defense Operations:**
- `defense_actions` – **Requires root/admin privileges**
- Can modify system state (firewall, processes, ports)
- Always test in non-production environments first
- Have rollback procedures ready

**System Updates:**
- `update_system` – **Requires root/admin privileges**
- May install security patches automatically
- Test in staging before production
- Have backup/rollback procedures

### CSV/Spreadsheet Tools

- Validate input data to prevent injection attacks
- Limit file sizes to prevent DoS
- Sanitize file paths to prevent directory traversal
- Use read-only operations when possible

---

## Security Checklist

Before deploying to production:

- [ ] Review security audit tool usage and consider implementing `ENABLE_DANGEROUS_TOOLS` opt-in flag
- [ ] Strong `SECRET_KEY` is configured
- [ ] Web interface is behind authentication/authorization
- [ ] HTTPS/TLS is enabled
- [ ] API keys are stored securely (not in code)
- [ ] Logging is configured and monitored
- [ ] Network access is restricted appropriately
- [ ] Backup and recovery procedures are in place
- [ ] Security updates are applied regularly
- [ ] Access controls are implemented

---

## Additional Resources

- [docs/TOOLING.md](docs/TOOLING.md) – Tool documentation with security notes
- [docs/ENV_SETUP.md](docs/ENV_SETUP.md) – Secure configuration practices
- [CONTRIBUTING.md](CONTRIBUTING.md) – Development security practices

---

**Last Updated:** 2026-01-21
