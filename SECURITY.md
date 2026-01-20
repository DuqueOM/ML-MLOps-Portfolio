# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅        |
| Previous | ❌        |

## Reporting a Vulnerability

If you discover a security vulnerability in this ML-MLOps Portfolio project, please report it privately before disclosing it publicly.

### How to Report

**Preferred Method:**
- Send an email to: DuqueOrtegaMutis@gmail.com
- Use the subject line: `Security Vulnerability Report - ML-MLOps-Portfolio`

**Alternative Methods:**
- GitHub's private vulnerability reporting: [Report Vulnerability](https://github.com/DuqueOM/ML-MLOps-Portfolio/security/advisories/new)
- Direct message on LinkedIn: [Duque Ortega Mutis](https://linkedin.com/in/duqueom)

### What to Include

Please include the following information in your report:

1. **Vulnerability Type** (e.g., XSS, SQL injection, dependency issue)
2. **Affected Components** (specific files, APIs, or dependencies)
3. **Impact Assessment** (potential damage or risk)
4. **Reproduction Steps** (detailed steps to reproduce the issue)
5. **Proof of Concept** (if available)
6. **Suggested Mitigation** (optional but helpful)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 business days
- **Resolution Timeline**: Depends on severity (see below)

## Severity Levels

| Severity | Response Time | Description |
|----------|---------------|-------------|
| Critical | 48 hours | Remote code execution, data breach, system compromise |
| High | 7 days | Privilege escalation, data exposure, authentication bypass |
| Medium | 14 days | Information disclosure, DoS vulnerabilities |
| Low | 30 days | Minor security issues, best practice violations |

## Security Scope

The following security aspects are within scope:

### ✅ In Scope
- Application code in all three projects (BankChurn, CarVision, TelecomAI)
- API endpoints and authentication mechanisms
- Docker container configurations
- CI/CD pipeline security
- Dependency vulnerabilities
- Data handling and storage
- Infrastructure as code (Terraform, K8s manifests)

### ❌ Out of Scope
- Vulnerabilities in third-party dependencies (report to upstream)
- Issues requiring physical access to infrastructure
- Social engineering attacks
- Denial of service attacks against production infrastructure
- Vulnerabilities in outdated versions no longer supported

## Security Best Practices in This Project

### Implemented Measures
- **Container Security**: Multi-stage Docker builds, minimal base images
- **Dependency Scanning**: Automated security scans in CI/CD (`pip-audit`, `safety`)
- **Secret Management**: No hardcoded secrets, environment-based configuration
- **Code Quality**: Static analysis with `bandit`, `flake8`, `mypy`
- **Access Control**: Principle of least privilege in deployment configurations
- **Monitoring**: Prometheus metrics and Grafana dashboards for security monitoring

### Configuration Security
- **Pydantic Validation**: Input sanitization and type checking
- **FastAPI Security**: CORS configuration, request validation
- **MLflow Security**: Authentication and authorization for experiment tracking
- **Kubernetes Security**: Network policies, resource limits, security contexts

## Disclosure Policy

### Coordinated Disclosure
We follow coordinated disclosure principles:

1. **Private Report**: Vulnerabilities are reported privately
2. **Assessment**: Security team evaluates and validates the report
3. **Remediation**: Fix is developed and tested
4. **Disclosure**: Public disclosure after fix is deployed (typically 90 days)

### Credit
Security researchers will be acknowledged in our security advisories unless they prefer to remain anonymous.

### Security Advisories
- Published advisories: [GitHub Security Advisories](https://github.com/DuqueOM/ML-MLOps-Portfolio/security/advisories)
- CVE assignments when applicable

## Security Contacts

### Security Team
- **Lead**: Duque Ortega Mutis
- **Email**: DuqueOrtegaMutis@gmail.com
- **GitHub**: @DuqueOM

### Emergency Contact
For critical security issues requiring immediate attention:
- **Emergency Email**: DuqueOrtegaMutis@gmail.com
- **Response Time**: Within 24 hours

## Security Updates

- **Low Priority**: Included in regular releases
- **Medium Priority**: Patch releases within 14 days
- **High Priority**: Security patches within 7 days
- **Critical Priority**: Emergency patches within 48 hours

## Security Testing

### Automated Testing
- **SAST**: Static Application Security Testing with `bandit`
- **SCA**: Software Composition Analysis with `pip-audit`
- **Container Scanning**: `trivy` for Docker images
- **Infrastructure Scanning**: `tfsec` for Terraform configurations

### Manual Testing
- **Penetration Testing**: Quarterly security assessments
- **Code Reviews**: Security-focused code reviews for critical changes
- **Architecture Reviews**: Security architecture assessments

## Legal Disclaimer

This security policy is provided "as is" without warranty of any kind. We reserve the right to modify this policy at any time.

---

**Last Updated**: January 2026  