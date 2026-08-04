# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability within the Twitter Clone Backend REST API, please report it privately by emailing `security@example.com`. Do not disclose security issues publicly until they have been addressed.

## Security Controls Implemented

- Password hashing using Flask-Bcrypt (Blowfish cipher).
- JWT Access and Refresh token authorization with server-side revocation blocklist.
- Rate limiting on sensitive endpoints via Flask-Limiter.
- Input sanitization and path traversal prevention (`secure_filename` & UUID v4 renaming).
- HTTP Security Headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`).
