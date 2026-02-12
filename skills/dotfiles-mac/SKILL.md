---
name: dotfiles-mac
description: Create, update, or apply a macOS dotfiles repo. Use when the user wants to back up their system configuration, set up a new Mac from dotfiles, capture current configs into an existing dotfiles repo, or manage dotfiles with GNU Stow. Covers Homebrew, shell, git, SSH, GPG, app configs, and macOS defaults.
---

# Dotfiles Mac

Help users create, update, or apply a macOS dotfiles repo using GNU Stow and plain git.

## Repo Conventions

- **Location**: `~/.dotfiles/` (or user's existing dotfiles repo)
- **Symlink manager**: GNU Stow with `--no-folding` (always file-level symlinks, never directory-level)
- **Structure**: Each top-level directory is a stow package mirroring `$HOME`
- **OS-specific**: Directories prefixed `os-` (e.g., `os-macos/`) contain OS-specific files
- **Machine-specific**: `.local` file pattern — gitignored files sourced/included by tracked configs

### Repo Layout

```
~/.dotfiles/
├── setup.sh                    # Entry point: detects OS, delegates
├── .gitignore
├── .stow-local-ignore
├── README.md
│
├── # Cross-platform stow packages (each mirrors $HOME)
├── shell/                      # → ~/.zshrc, ~/.zprofile, etc.
├── git/                        # → ~/.gitconfig, ~/.gitignore_global
├── ssh/                        # → ~/.ssh/config (NOT keys)
├── gpg/                        # → ~/.gnupg/gpg.conf, gpg-agent.conf
├── tmux/                       # → ~/.tmux.conf or ~/.config/tmux/
├── nvim/                       # → ~/.config/nvim/
├── ghostty/                    # → ~/.config/ghostty/
├── claude/                     # → ~/.claude/settings.json, skills, etc.
├── <tool>/                     # Additional stow packages as needed
│
├── os-macos/                   # macOS-specific (NOT auto-stowed)
│   ├── Brewfile                # Homebrew packages/casks/taps/mas
│   ├── setup.sh                # brew, Xcode CLT, stow, defaults
│   ├── defaults.sh             # macOS defaults write commands
│   └── gpg/                    # OS-specific override (e.g., pinentry-mac)
│
└── os-linux/                   # Future: Linux-specific
    ├── setup.sh
    └── gpg/                    # Linux-specific override
```

The `os-` prefix keeps OS directories sorted together, visually distinct from stow packages.

### OS-Specific Overrides

For each stow package, check if `os-{current_os}/` has a directory with the same name. If so, stow the OS-specific version **instead of** the common one — the OS version wins entirely.

Example: `gpg/` has base config. `os-macos/gpg/` has macOS-specific config (e.g., `pinentry-program` set to `pinentry-mac`). On macOS, only `os-macos/gpg/` is stowed.

If OS-specific package directories contain files that should be ignored by stow (e.g., README.md), place a `.stow-local-ignore` in the `os-macos/` directory — stow only reads this file from its `-d` directory.

### Machine-Specific Overrides

Use the `.local` file pattern — tracked configs source/include an untracked `.local` counterpart:

- `.zshrc` → sources `~/.zshrc.local` at end (if it exists)
- `.gitconfig` → `[include] path = ~/.gitconfig.local`
- `.ssh/config` → `Include ~/.ssh/config.local` at top

All `.local` files are gitignored. This avoids templating engines entirely.

---

## Instructions for Claude

You are helping a user manage their macOS dotfiles. Determine which workflow applies:

- **Create**: User has no dotfiles repo — audit their system, generate the repo
- **Update/Capture**: User has a dotfiles repo — capture current system state into it
- **Apply**: User has a dotfiles repo — apply it to a new or existing machine

If unclear, ask the user which workflow they want.

---

### Workflow A: Create a New Dotfiles Repo

#### Step 1: Audit the System

Scan the user's machine to discover what's worth tracking. Run these in parallel where possible:

**Homebrew:**
```bash
brew bundle dump --force --describe --file=/tmp/dotfiles-audit-Brewfile
```

**Shell configs:**
- Check for `~/.zshrc`, `~/.zsh/`, `~/.zprofile`, `~/.zshenv`, `~/.bashrc`, `~/.bash_profile`
- Fish: `~/.config/fish/config.fish`, `~/.config/fish/conf.d/`, `~/.config/fish/functions/`
- Detect framework: Oh My Zsh (`~/.oh-my-zsh/`), Prezto, Starship, plain zsh
- If Oh My Zsh: note custom themes in `~/.oh-my-zsh/custom/themes/` and custom plugins in `~/.oh-my-zsh/custom/plugins/` — these are user content worth tracking. Do NOT track OMZ core (it's managed by its own installer).

**Git:**
- Read `~/.gitconfig` (note: may contain `[user]` with name/email — fine to track)
- Check for conditional includes (`[includeIf]` sections) — these reference paths that may need adjustment on other machines. Suggest moving `[includeIf]` blocks to `~/.gitconfig.local` since they reference machine-specific paths
- Check for `~/.gitignore_global` or equivalent

**SSH:**
- Read `~/.ssh/config` (track this)
- Note: NEVER track `~/.ssh/id_*`, `~/.ssh/*.pub`, `~/.ssh/known_hosts`, `~/.ssh/authorized_keys`

**GPG:**
- Read `~/.gnupg/gpg.conf`, `~/.gnupg/gpg-agent.conf` (track these)
- NEVER track: `~/.gnupg/private-keys-v1.d/`, `~/.gnupg/*.kbx`, `~/.gnupg/trustdb.gpg`, `~/.gnupg/openpgp-revocs.d/`, `~/.gnupg/S.gpg-agent*`

**Claude/AI configs:**
- Check for `~/CLAUDE.local.md`, `~/.claude/settings.json`, non-symlinked skills in `~/.claude/skills/`
- NEVER track: `~/.claude/auth/`, `~/.claude/sessions/`, `~/.claude/cache/`, `~/.claude/telemetry/`, `~/.claude/*.local.json`

**Terminal emulator:**
- Ghostty: `~/.config/ghostty/config`
- iTerm2: check for plist or JSON profile exports
- Alacritty: `~/.config/alacritty/alacritty.toml` (current, since v0.13) or `~/.config/alacritty/alacritty.yml` (legacy)
- Kitty: `~/.config/kitty/kitty.conf`

**Editor configs:**
- Neovim: `~/.config/nvim/`
- Vim: `~/.vimrc`
- VS Code: `~/Library/Application Support/Code/User/settings.json`, `keybindings.json`
- Note: VS Code/Cursor settings live in `~/Library/Application Support/` (path with spaces). These can't be managed cleanly with stow — handle with direct symlinks in setup.sh instead.

**Other common configs:**
- tmux: `~/.tmux.conf` or `~/.config/tmux/tmux.conf`
- Starship: `~/.config/starship.toml`
- ripgrep: `~/.ripgreprc`
- bat: `~/.config/bat/config`
- Any `~/.config/` subdirectories for tools installed via Homebrew
- Check `$XDG_CONFIG_HOME` (default: `~/.config/`). Adjust stow targets if user has a non-standard XDG location.

**macOS defaults:**
- Ask the user if they want to capture macOS system preferences
- If yes, identify commonly customized domains: `NSGlobalDomain`, `com.apple.dock`, `com.apple.finder`, `com.apple.Safari`, `com.apple.screencapture`, etc.

#### Step 2: Security Scan

Before proposing anything to track, scan discovered files for secrets:

- **Auth tokens**: Look for patterns like `token`, `api_key`, `secret`, `password`, `credential` in config files
- **Specific files to exclude**:
  - `~/.npmrc` (may contain auth tokens) — detect and either exclude or template with placeholder
  - `~/.config/graphite/user_config` (contains auth) — exclude
  - `~/.netrc` — exclude
  - `~/.aws/credentials` — exclude (but `~/.aws/config` is safe)
  - `~/.docker/config.json` (Docker registry auth) — exclude
  - `~/.kube/config` (Kubernetes tokens/certs) — exclude
  - `~/.config/gh/hosts.yml` (GitHub CLI OAuth tokens) — exclude
  - `~/.config/gcloud/` (Google Cloud credentials) — exclude
  - `~/.boto`, `~/.s3cfg` (S3 credentials) — exclude
  - Any file containing what looks like a base64-encoded token or prefixed strings: `ghp_`, `gho_`, `ghs_`, `github_pat_`, `sk-`, `npm_`, `xoxb-`, `xoxp-`, `xoxe-`, `AKIA`, `AIza`, `glpat-`, `pypi-`, `sk_live_`, `pk_live_`, `rk_live_`, `SG.`, `dop_v1_`
- Scan file contents for `-----BEGIN.*PRIVATE KEY-----` headers — this catches embedded private keys regardless of filename
- In shell configs, scan for `export` statements where the variable name contains KEY, SECRET, TOKEN, PASSWORD, or CREDENTIAL — these often contain inline secrets
- If a file contains both safe config and embedded secrets, note it for the user and suggest the `.local` file pattern to split them

#### Step 3: Present Findings

Show the user what was discovered, grouped by category:

```
## Discovered Configuration

### Homebrew (N formulae, N casks, N taps)
[summary of what's in the Brewfile]

### Shell (zsh + Oh My Zsh)
- .zshrc, .zprofile, .zshenv
- OMZ custom themes: [list]
- OMZ custom plugins: [list]

### Git
- .gitconfig (user: name <email>)
- .gitignore_global

### SSH
- config (N hosts configured)
- ⚠ Keys will NOT be tracked

### GPG
- gpg.conf, gpg-agent.conf
- ⚠ Secret keys will NOT be tracked

### [other categories...]

### ⚠ Excluded (secrets detected)
- ~/.npmrc (contains auth token)
- [other excluded files]
```

Ask the user:
1. Which categories to include (all are opt-in by default)
2. Whether to capture macOS defaults
3. Where to create the repo (default: `~/.dotfiles/`)
4. Whether to create a GitHub repo

#### Step 4: Generate the Repo

1. Create the directory structure with stow packages for each selected category
2. Copy config files into the appropriate stow package directories, mirroring home directory structure
3. Place the `Brewfile` from the audit dump into `os-macos/`
4. Generate `setup.sh` (see Setup Script section below)
5. Generate `.gitignore` covering:
   - Secret key patterns (`id_*`, `*.key`, `*.pem`, `private-keys-v1.d/`)
   - Auth files (`.npmrc`, `.netrc`, auth tokens)
   - `.local` override files (`*.local`, `.local/`)
   - Backup directory (`.dotfiles-backup/`)
   - OS artifacts (`.DS_Store`)
6. Generate `.stow-local-ignore` (skip `README.md`, `setup.sh`, `os-*`, `.git`, `.gitignore`)
7. Generate `README.md` with repo overview and usage instructions
8. If macOS defaults selected, generate `os-macos/defaults.sh`
9. Ensure tracked shell configs include the `.local` sourcing pattern at the end
10. Ensure `.gitconfig` includes `[include] path = ~/.gitconfig.local`
11. Ensure `.ssh/config` includes `Include ~/.ssh/config.local` at top
12. `git init`, create initial commit
13. If user wants GitHub: create remote repo and push

#### Step 5: Apply (Optional)

After generating, ask if the user wants to apply the dotfiles now (stow them). If yes, run setup.sh with the stow subcommand.

---

### Workflow B: Update/Capture Existing Repo

The user has a dotfiles repo and wants to sync their current system state into it.

#### Step 1: Locate and Understand the Repo

1. Find the dotfiles repo (check `~/.dotfiles/`, or ask)
2. Read the repo structure to understand what's already tracked
3. Identify which stow packages exist

#### Step 2: Diff Current State vs Tracked

For each tracked category, compare current system files with repo contents:

**Brewfile:**
```bash
brew bundle dump --force --describe --file=/tmp/dotfiles-capture-Brewfile
```
Then diff against the tracked `os-macos/Brewfile`. Show added/removed packages.

**Config files:**
For each stow package, diff the target file against the repo copy. Show meaningful changes (ignore whitespace, comments-only changes are low priority).

**New configs:**
Scan for config files that exist on the system but aren't tracked in any stow package. Suggest new packages.

#### Step 3: Present Changes

Show the user a summary of what changed:

```
## Changes Since Last Capture

### Brewfile
- Added: package-a, package-b, cask-c
- Removed: old-package

### shell/.zshrc
- [diff summary or key changes]

### New (untracked)
- ~/.config/ghostty/config (suggest: ghostty/ stow package)

### Unchanged
- git/, ssh/, gpg/
```

Ask the user which changes to apply to the repo.

#### Step 4: Apply Updates

1. Update selected files in the repo (copy current system files into stow packages)
2. Update Brewfile if selected
3. Run the security scan on any new/changed files before staging
4. Stage and commit with a descriptive message (e.g., `chore: capture updated shell config and new packages`)

---

### Workflow C: Apply Repo to a Machine

The user has a dotfiles repo and wants to apply it to a new or existing machine.

#### Step 1: Validate

1. Read the repo to understand what will be applied
2. Check for conflicts: existing files at target locations that aren't symlinks to the repo
3. Present a summary of what will happen

#### Step 2: Run Setup

Execute `setup.sh` or walk through it step by step if the user prefers. See Setup Script section for the execution order.

#### Step 3: Post-Apply Checklist

After setup completes, present a next-steps checklist:

```
## Next Steps (manual)

- [ ] Import GPG secret keys: `gpg --import /path/to/private-key.asc`
      Then set trust: `gpg --edit-key <KEY_ID>` → `trust` → `5` → `quit`
- [ ] Copy SSH keys to ~/.ssh/ and `chmod 600 ~/.ssh/id_*`
      (or generate new: `ssh-keygen -t ed25519`)
      (if using encrypted secrets with transcrypt, keys are already in place after unlock)
- [ ] Sign into Mac App Store (for `mas` packages in Brewfile)
- [ ] Authenticate services:
  - [ ] `gh auth login` (GitHub CLI)
  - [ ] `npm login` (npm registry)
  - [ ] `gt auth` (Graphite)
- [ ] Create machine-specific overrides in ~/.zshrc.local, ~/.gitconfig.local, etc.
- [ ] Review and run macOS defaults: cd ~/.dotfiles && ./os-macos/defaults.sh

Ask me to help with any of these!
```

---

### Workflow D: Unstow / Restore

If the user wants to revert to their pre-stow state:

1. Un-stow all packages: `stow -D -d $DOTFILES_DIR -t $HOME <package>` for each
2. If `~/.dotfiles-backup/` exists, offer to restore backed-up files
3. List any files that were in the backup and confirm before restoring
4. Print what was restored vs what was removed

---

## Setup Script Design

### Root `setup.sh`

The root setup.sh detects the OS and delegates:

```bash
#!/usr/bin/env bash
set -euo pipefail
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname -s)" in
  Darwin) source "$DOTFILES_DIR/os-macos/setup.sh" ;;
  Linux)  source "$DOTFILES_DIR/os-linux/setup.sh" ;;
  *)      echo "Unsupported OS"; exit 1 ;;
esac
```

### `os-macos/setup.sh`

Supports subcommands:

```bash
./setup.sh              # Full install (all phases)
./setup.sh brew         # Homebrew + brew bundle only
./setup.sh stow         # Stow all packages only
./setup.sh macos        # macOS defaults only
./setup.sh capture      # Capture current state back to repo
./setup.sh restore      # Un-stow all packages and restore backups
```

### Execution Order (Full Install)

```
Phase 1: Foundation
  1. Xcode Command Line Tools
     - xcode-select -p &>/dev/null || xcode-select --install
  2. Homebrew
     - Detect arch: /opt/homebrew (ARM) vs /usr/local (Intel)
     - Install if missing, eval brew shellenv

Phase 2: Packages
  3. brew bundle install --file=os-macos/Brewfile --no-lock
     - Non-fatal: individual failures warn but continue

Phase 3: Frameworks
  4. Oh My Zsh (if shell/ stow package uses it)
     - Install if ~/.oh-my-zsh/ doesn't exist
     - Stow custom themes/plugins into place

Phase 4: Configuration
  5. Stow all packages
     - For each directory that isn't os-*, .git, or special files:
       - Check for os-macos/ override → stow that instead if present
       - Backup conflicting real files to ~/.dotfiles-backup/<timestamp>/
       - stow --no-folding -d $DOTFILES_DIR -t $HOME <package>
     - Skip packages the user has excluded (via env var or config)

Phase 5: System Preferences (opt-in)
  6. macOS defaults (only if explicitly requested or --with-defaults flag)
     - Source os-macos/defaults.sh
     - killall affected apps at the end (Dock, Finder, SystemUIServer)

Phase 6: Post-install
  7. Change default shell to brew zsh (if not already)
     - Ensure brew's zsh is in /etc/shells: sudo sh -c 'echo $(brew --prefix)/bin/zsh >> /etc/shells'
     - Then: chsh -s $(brew --prefix)/bin/zsh
  8. Print next-steps checklist
```

### Backup Strategy

Before stowing, handle existing non-symlink files:

```bash
backup_if_needed() {
  local target="$1"
  if [ -L "$target" ]; then
    # Existing symlink (possibly from another dotfiles manager)
    local link_target="$(readlink "$target")"
    echo "  Replacing symlink: $target → $link_target"
    rm "$target"
  elif [ -e "$target" ]; then
    local rel_path="${target#$HOME/}"
    local backup_path="$BACKUP_DIR/$rel_path"
    mkdir -p "$(dirname "$backup_path")"
    mv "$target" "$backup_path"
    echo "  Backed up: $target → $backup_path"
  fi
}
```

### Idempotency

Every operation is safe to re-run:
- Xcode CLT: checks before installing
- Homebrew: checks before installing
- brew bundle: only installs missing packages
- Stow: re-stowing already-linked files is a no-op
- Defaults: `defaults write` is idempotent

### Error Handling

```bash
# Critical (stop): Can't install Homebrew, stow has unresolvable conflicts
# Non-critical (warn + continue): Individual brew packages, missing optional tools

# Since setup.sh uses set -euo pipefail, non-fatal sections must trap errors:
# brew bundle install ... || echo "⚠ Some packages failed (continuing)"
# stow ... || echo "⚠ Stow failed for $package (continuing)"
```

---

## Security Rules

**NEVER track or commit** (unless encrypted with transcrypt — see Encrypted Secrets section):
- Private keys (SSH, GPG, TLS)
- Auth tokens, API keys, credentials
- `.env` files, environment secrets
- Session data, cookies, browser profiles
- Keyrings and trust databases
- Files matching: `id_*`, `*.key`, `*.pem`, `*.p12`, `private-keys-v1.d/`, `*.kbx`, `trustdb.gpg`, `.env*`
- Files containing token prefixes: `ghp_`, `gho_`, `ghs_`, `github_pat_`, `sk-`, `npm_`, `xoxb-`, `xoxp-`, `xoxe-`, `AKIA`, `AIza`, `glpat-`, `pypi-`, `sk_live_`, `pk_live_`, `rk_live_`, `SG.`, `dop_v1_`
- Files containing: `token`, `secret`, `password` values
- Files containing `-----BEGIN.*PRIVATE KEY-----` headers

**For files with mixed content** (safe config + embedded secrets):
- Suggest splitting into tracked config + gitignored `.local` override
- Or template with placeholders and a warning comment: `token = <YOUR_TOKEN_HERE>  # REPLACE with actual token`

**Always run a secret scan** before `git add` — grep for token-like patterns in staged files.

---

## Encrypted Secrets (Optional)

This section is entirely optional. Users who don't want encryption skip it — the skill works exactly as before. Present this as a choice during Workflow A (Step 3).

### Tool: transcrypt

[transcrypt](https://github.com/elasticdog/transcrypt) provides transparent, password-based encryption in git via clean/smudge filters. Files are decrypted in the working tree (so stow sees plaintext) and encrypted in git objects (safe to push).

**Install:** `brew install transcrypt`
**Deps:** bash + OpenSSL (pre-installed on macOS/Linux)

### Initialization (one-time per repo)

```bash
cd ~/.dotfiles
transcrypt -c aes-256-cbc -p 'master-password'
```

### Marking Files as Encrypted

Add patterns to `.gitattributes` in the repo root:

```
# Encrypted secrets
ssh/.ssh/id_ed25519 filter=crypt diff=crypt merge=crypt
ssh/.ssh/id_ed25519.pub filter=crypt diff=crypt merge=crypt
gpg/.gnupg/private-keys-v1.d/** filter=crypt diff=crypt merge=crypt
*.npmrc filter=crypt diff=crypt merge=crypt
```

**Critical:** Ensure a file's `.gitattributes` pattern exists BEFORE running `git add` — otherwise it commits in plaintext.

### What This Enables

- SSH private keys CAN be tracked (encrypted)
- GPG secret keys CAN be tracked (encrypted)
- `.npmrc` with auth tokens CAN be tracked (encrypted)
- Any file matched in `.gitattributes` is auto-encrypted on commit

If using encrypted secrets, remove the corresponding patterns from `.gitignore` (e.g., `id_*`, `*.kbx`, `private-keys-v1.d/`).

### Workflow Integration

- **Create/Capture:** After `git add`, transcrypt auto-encrypts on commit. No manual step needed.
- **Apply (fresh machine):** After `git clone`, run `transcrypt -c aes-256-cbc -p 'password'` to unlock. Then stow as normal — files are decrypted in the working tree.
- **setup.sh:** Add a transcrypt unlock step between clone and stow. Prompt for the password if encrypted files are detected (check for `.gitattributes` with `filter=crypt` patterns).

### Caveats

- **Password strength matters** — recommend a strong passphrase, store it in a password manager
- **Unrecoverable if lost** — if the password is lost, encrypted files cannot be recovered
- **Lock operation:** `transcrypt --flush-credentials` encrypts files in the working tree — symlinks would then point to ciphertext. Document this as an intentional "lock" for when the machine is untrusted.
- **Validate before adding:** When adding a new secret file, always confirm its `.gitattributes` pattern exists before `git add`

---

## `.gitignore` Template

If using transcrypt for encrypted secrets, remove patterns for files that are encrypted instead.

```gitignore
# Secrets & keys (remove entries for files encrypted with transcrypt)
id_*
*.key
*.pem
*.p12
*.pfx
private-keys-v1.d/
*.kbx
trustdb.gpg
openpgp-revocs.d/
secring.gpg
S.gpg-agent*
.npmrc
.netrc
.env*
known_hosts*
authorized_keys
random_seed
credentials

# Machine-specific overrides (e.g., .zshrc.local, .gitconfig.local)
*.local
.local/

# Backups
.dotfiles-backup/

# OS artifacts
.DS_Store
```

## `.stow-local-ignore` Template

```
\.git
\.gitignore
\.stow-local-ignore
^README\.md
^setup\.sh
^os-.*
^LICENSE
```

## `.gitattributes` Template (for transcrypt)

```
# Uncomment patterns for files you want encrypted with transcrypt
# ssh/.ssh/id_* filter=crypt diff=crypt merge=crypt
# gpg/.gnupg/private-keys-v1.d/** filter=crypt diff=crypt merge=crypt
# *.npmrc filter=crypt diff=crypt merge=crypt
```
