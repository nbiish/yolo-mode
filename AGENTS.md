# AGENTS.md

```xml
<agent>
Approach: Security-first, Zero Trust, Standardized  
Output: Production-ready, tested, encrypted, PQC-compliant  
</agent>

Use `tts-cli --text "<text>"` to generate audio for the user to concisely summarize your actions and decisions, or `local-tts-mcp` if `tts-cli` is not available.

<coding>
Universal Standards:
Match existing codebase style
SOLID, DRY, KISS, YAGNI
Small, focused changes over rewrites
Never create dummy code
Websearch the facts

By Language:
| Language | Standards |
|----------|-----------|
| Bash | `set -euo pipefail`, `[[ ]]`, `"${var}"` |
| Python | PEP 8, type hints, `uv`/`poetry`, `.venv` |
| TypeScript | strict mode, ESLint, Prettier |
| Rust | `cargo fmt`, `cargo clippy`, `Result` over panic |
| Go | `gofmt`, `go vet`, Effective Go |
| C++ | `clang-format`, `clang-tidy`, C++20, RAII |
</coding>

<security>
Core Principles:
Zero Trust: Verify every tool call; sanitize all inputs.
Least Privilege: Minimal permissions; scoped credentials per session.
No hardcoded secrets: Environment variables only, accessed via secure vault.
Sandboxing: Code execution via WASM/Firecracker only.
Tool Misuse: Strict schema validation (Zod/Pydantic) for all inputs.
Identity Abuse: Independent Permission Broker; short-lived tokens.
Information Disclosure: PII Redaction; Env var only secrets.
Repudiation: Structured immutable ledgers; remote logging.

Data Protection & Encryption:
In Transit:
TLS 1.3+ with mTLS for inter-agent communication.
Hybrid PQC Key Exchange: X25519 + ML-KEM-768 (FIPS 203).
At Rest:
AES-256-GCM for databases and file storage.
Tenant-specific keys for Vector DB embeddings.
Encrypted logs with strict retention and PII redaction.


Post-Quantum Crytography (NIST FIPS Standards)
| Purpose | Standard | Algorithm | Status (2026) |
|---------|----------|-----------|---------------|
| Key Encapsulation | FIPS 203 | ML-KEM-768/1024 | Standard |
| Digital Signatures | FIPS 204 | ML-DSA-65/87 | Standard |
| Hash-Based Sig | FIPS 205 | SLH-DSA | Standard |
</security>

Git Commits: `<type>(<scope>): <description>` — feat|fix|docs|refactor|test|chore|perf|ci

**Important**:  Follow the critical security, best-practices, and coding standards rules while informing the user of your actions and decisions via tts-cli or local-tts-mcp upon completion of the task.

```
