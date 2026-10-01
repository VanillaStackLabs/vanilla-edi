### Description
A clear and concise description of what this PR does. If it introduces a new EDI transaction set (e.g., 810, 856), briefly explain the schema design.

### Related Issue
Closes #[Issue Number]

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

### Testing & CI
VanillaEDI maintains a strict 100% test coverage requirement. 
- [ ] I have run `pytest` locally and all tests pass.
- [ ] I have run `pytest --cov` and maintained 100% line/branch coverage.
- [ ] I have tested this against valid, sanitized X12 payloads.

### Data Privacy Checklist
**WARNING: EDI payloads often contain PHI or PII. Review your test data carefully.**
- [ ] I confirm that any X12 test files or JSON fixtures included in this PR are completely mocked/sanitized/redacted.

### Additional Context
Add any other context, screenshots, or API design notes about the pull request here.