# Security Policy

## Supported Versions

### Package versions

Only the latest release (currently **v0.2.0**) receives security patches.
Older releases are not supported — if you discover a vulnerability in an
earlier version, please upgrade to the latest release first and verify the
issue still reproduces.

| Version | Supported          |
|---------|--------------------|
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

### Python versions

`robotsix-modules` requires **Python 3.12 or later**. Older Python versions
are not supported.

| Python  | Supported          |
|---------|--------------------|
| 3.12+   | :white_check_mark: |
| < 3.12  | :x:                |

## Reporting a Vulnerability

If you believe you have found a security vulnerability in
`robotsix-modules`, please report it privately rather than opening a public
issue. We take every report seriously and will work with you to understand
and address the issue.

**Do not open a public GitHub issue.** Public disclosure of a vulnerability
puts users at risk before a fix can be prepared and released.

Instead, use one of these channels:

- **Preferred:** Open a [GitHub Security Advisory](https://github.com/damien-robotsix/robotsix-modules/security/advisories/new) on this repository. GitHub's private reporting form allows you to describe the vulnerability and collaborate with maintainers in a secure environment.
- **Alternative:** Send an email to [damien.robotsix@gmail.com](mailto:damien.robotsix@gmail.com) with a description of the vulnerability. Please include enough detail for us to reproduce and triage the issue — a proof of concept, affected versions, and any mitigations you are aware of are all helpful.

## Expected Response Timeline

- We will acknowledge your report within **72 hours** and confirm we are
  investigating.
- We will provide a preliminary assessment (including whether the report is
  accepted as a security issue and, if so, an estimated severity) within
  **5 business days**.
- After the initial assessment, we will keep you informed of progress and
  coordinate a disclosure timeline with you before any public announcement.

We ask that you refrain from disclosing the vulnerability publicly during
this window so that we can prepare and release a fix safely.

## Security Model

This section describes the security boundaries of `robotsix-modules` so that
reporters and consumers understand what the library does — and does not —
protect against.

- **YAML parsing:** All YAML input is parsed with `yaml.safe_load`, which
  does not deserialize arbitrary Python objects. There is no invocation of
  `yaml.load` with an unsafe loader anywhere in the codebase.
- **Network surface:** `robotsix-modules` is a pure CLI and library
  validator with **no network surface**. It does not make outbound
  connections, open listening sockets, or fetch remote resources.
- **No HTML rendering or authentication:** The library performs no HTML
  rendering, maintains no authentication state, and does not execute
  user-supplied code or shell commands.
- **Consumer responsibility:** The `validate()` and `validate_file()`
  functions, as well as the CLI entry point, accept untrusted input (YAML
  file paths, YAML strings). The library treats all input as potentially
  malicious and focuses on schema conformance — it does **not** sanitize or
  normalize input beyond parsing and validation. Consumers are responsible
  for ensuring that any data they pass to this library comes from trusted
  sources, or for applying their own sanitization before passing it on to
  other systems.

This security model is a factual description of the library's current
design. It is not a substitute for a full security audit.
