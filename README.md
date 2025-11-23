# Omarchy Dotfiles

My Omarchy OS config setup files with all the important files and dotfiles for future configs.

## Security Notice

⚠️ **Important**: This repository contains configuration files for personal use. Sensitive data such as passwords, API keys, and personal information have been excluded.

### Excluded Sensitive Directories

The following directories are **NOT** included in this repository for security reasons:

- **1Password/** - Password manager database and configuration
- **Signal/** - Encrypted messaging app data including encryption keys
- **obsidian/** - Personal notes, cookies, and session data
- **Electron/** - Application cache and preferences
- **obs-studio/plugin_config/** - OBS WebSocket passwords and configurations
- **Ultralytics/** - ML framework settings with personal paths and UUIDs
- **configstore/** - Application configuration stores with telemetry data
- **nextjs-nodejs/** - Next.js telemetry and anonymous IDs
- **turborepo/** - Turborepo telemetry configuration

### What to Configure Locally

After cloning this repository, you'll need to:

1. **Set up your own application configurations** for:
   - 1Password
   - Signal Desktop
   - Obsidian
   - OBS Studio
   
2. **Configure API keys and secrets** in your local environment (never commit these!)

3. **Review and customize** the dotfiles to match your system and preferences

## Installation

1. Clone this repository
2. Review the configuration files
3. Symlink or copy the configurations you need to your `~/.config/` directory
4. Set up sensitive applications separately with your own credentials

## Best Practices

- ✅ **DO** keep configuration templates and examples
- ✅ **DO** document what needs to be configured
- ❌ **DON'T** commit passwords, API keys, or personal data
- ❌ **DON'T** commit database files or session cookies
- ❌ **DON'T** commit application cache directories

## License

Personal configuration files - use at your own risk.
