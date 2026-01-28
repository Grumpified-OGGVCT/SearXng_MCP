# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of SearXNG MCP Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (preferred): 
   - Go to https://github.com/Grumpified-OGGVCT/SearXng_MCP/security/advisories
   - Click "Report a vulnerability"

2. **Email** (if GitHub Security Advisories is not available):
   - Send details to the repository maintainer via GitHub
   - Include "SECURITY" in the subject line

### What to Include

Please include the following information in your report:

- Type of vulnerability
- Full paths of affected source files
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Remote code execution, authentication bypass | 1-7 days |
| **High** | Data exposure, privilege escalation | 7-14 days |
| **Medium** | Limited information disclosure | 14-30 days |
| **Low** | Minor issues with limited impact | 30-90 days |

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**: Regularly update to the latest version
   ```bash
   pip install --upgrade searxng-mcp
   ```

2. **Use Environment Variables**: Store sensitive configuration in environment variables, not in code
   ```bash
   export SEARXNG_INSTANCES="https://your-instance.com"
   ```

3. **Monitor Logs**: Regularly check logs for suspicious activity

4. **Use HTTPS Instances**: Always use HTTPS SearXNG instances, not HTTP

5. **Cookie Security**: Cookie files are stored in `~/.searxng_mcp/cookies/` with appropriate permissions

### For Developers

1. **Input Validation**: All user inputs are validated before processing

2. **Secure Defaults**: 
   - Timeouts are set to prevent hanging requests
   - Safe search is available as an option
   - HTTPS is enforced for instances

3. **Dependency Management**: 
   - Regular automated dependency updates
   - Security scanning with pip-audit
   - Vulnerability monitoring in CI/CD

4. **No Secrets in Code**: Never commit API keys, tokens, or credentials

## Known Security Considerations

### Cookie Storage

- Cookies are stored locally in `~/.searxng_mcp/cookies/`
- Files are created with user-only permissions
- Cookies persist user preferences, not authentication credentials

### Network Requests

- All requests use httpx with timeout protection
- HTTPS is preferred for all instances
- No user data is transmitted beyond search queries

### Data Privacy

- No user data is logged or stored beyond cookies
- Search queries are sent directly to SearXNG instances
- No telemetry or analytics are collected

## Automated Security Measures

### GitHub Actions

Our CI/CD pipeline includes:

1. **Dependency Scanning**: Weekly automated checks for outdated dependencies
2. **Vulnerability Detection**: pip-audit scans for known vulnerabilities
3. **Code Quality**: Linting and type checking to prevent common issues
4. **Automated Updates**: Weekly checks for security patches

### Security Tools

- **Bandit**: Python security linter
- **pip-audit**: Dependency vulnerability scanner
- **Ruff**: Fast Python linter with security rules
- **MyPy**: Type checking to prevent type-related vulnerabilities

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible
5. Credit the reporter (unless they wish to remain anonymous)

## Security Updates

Security updates will be released as:

- **Patch versions** for backwards-compatible fixes (0.1.x)
- **Minor versions** if changes affect compatibility (0.x.0)

All security updates will be documented in:
- [CHANGELOG.md](CHANGELOG.md)
- GitHub Security Advisories
- Release notes

## Compliance

### MCP 2.0 Security Principles

This project adheres to MCP 2.0 security principles:

1. **User Consent**: Users control what data is shared
2. **Data Privacy**: Minimal data collection and storage
3. **Tool Safety**: Safe execution of search operations
4. **Transparency**: Clear documentation of capabilities and limitations

### Dependencies

We follow security best practices for dependencies:

- Regular updates via automated workflows
- Vulnerability scanning in CI/CD
- Pinned versions in requirements.txt
- Security advisory monitoring

## Credits

We thank the security researchers and contributors who help keep SearXNG MCP Server secure.

### Hall of Fame

*No security vulnerabilities reported yet. Be the first!*

## Questions?

For questions about this security policy, please create a GitHub Discussion or contact the maintainers.

---

**Last Updated**: 2026-01-28
