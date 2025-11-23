# Security Policy

## Overview

This repository contains personal dotfiles and configurations. It's important to keep sensitive data secure and separate from version control.

## What NOT to Commit

### Credentials and Secrets
- ❌ API keys (OpenAI, GitHub, cloud providers, etc.)
- ❌ OAuth tokens
- ❌ Passwords or password hashes
- ❌ Private keys and certificates
- ❌ SSH keys
- ❌ Webhook secrets
- ❌ Database credentials

### Personal Data
- ❌ Personal notes and documents
- ❌ Email or message databases
- ❌ Browser cookies and session data
- ❌ Application caches
- ❌ Personal UUIDs and anonymous IDs
- ❌ Local file paths that expose your username

### Application Data
- ❌ Database files (*.sqlite, *.db)
- ❌ Password manager vaults
- ❌ Encrypted messaging app data
- ❌ Browser profiles and extensions data
- ❌ Application logs with sensitive information

## Current Protection

The repository is protected with a comprehensive `.gitignore` file that excludes:

1. **Sensitive Applications**: 1Password, Signal, Obsidian, Electron apps
2. **Database Files**: All SQLite and database files
3. **API Keys**: Config files that typically contain secrets
4. **Browser Data**: Cookies, cache, session storage
5. **System-specific Data**: Application caches and telemetry

## Best Practices

### For Repository Maintainers

1. **Review before commit**: Always check what you're about to commit
   ```bash
   git status
   git diff --cached
   ```

2. **Use example/template files**: Instead of committing actual configs with secrets, create `.example` versions:
   ```bash
   # Instead of: config.json
   # Use: config.json.example
   ```

3. **Environment variables**: Use environment variables for sensitive data
   ```bash
   export API_KEY="your-key-here"
   ```

4. **Scan for secrets**: Use tools to detect accidentally committed secrets
   ```bash
   # Example tools:
   # - git-secrets
   # - trufflehog
   # - gitleaks
   ```

### For Users

1. **After cloning**: Never commit your personal modifications back to a public fork
2. **Local configuration**: Keep sensitive configs in a separate, private location
3. **Regular audits**: Periodically review what's being tracked
4. **Use private repos**: For truly personal configs, use private repositories

## If You Find a Leaked Secret

If you discover that a secret was accidentally committed:

1. **Revoke the secret immediately** (regenerate API keys, change passwords)
2. **Remove from history**: Use `git filter-branch` or `BFG Repo-Cleaner` to remove from history
3. **Force push**: Update the remote repository
4. **Notify**: If it's a shared repository, notify all contributors

### Removing Secrets from History

```bash
# Using BFG Repo-Cleaner (recommended)
bfg --delete-files secret-file.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Or using git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH-TO-FILE" \
  --prune-empty --tag-name-filter cat -- --all
```

## Reporting Security Issues

If you discover a security vulnerability or accidentally committed secret in this repository:

1. **DO NOT** create a public issue
2. Contact the repository owner directly
3. Provide details about the exposed secret
4. Allow time for the issue to be addressed before public disclosure

## References

- [GitHub's guide to removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git filter-branch documentation](https://git-scm.com/docs/git-filter-branch)
