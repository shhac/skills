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
      (if using encrypted secrets with age, keys are already in place after decryption)
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

Phase 3: Decrypt Secrets (if age-encrypted files exist)
  4. Find all .age files in stow packages
     - If none found, skip this phase
     - Prompt for master passphrase once
     - Decrypt each .age file to its non-.age counterpart
     - Unset passphrase from environment after decryption

Phase 4: Frameworks
  5. Oh My Zsh (if shell/ stow package uses it)
     - Install if ~/.oh-my-zsh/ doesn't exist
     - Stow custom themes/plugins into place

Phase 5: Configuration
  6. Stow all packages
     - For each directory that isn't os-*, .git, or special files:
       - Check for os-macos/ override → stow that instead if present
       - Backup conflicting real files to ~/.dotfiles-backup/<timestamp>/
       - stow --no-folding -d $DOTFILES_DIR -t $HOME <package>
     - Skip packages the user has excluded (via env var or config)

Phase 6: System Preferences (opt-in)
  7. macOS defaults (only if explicitly requested or --with-defaults flag)
     - Source os-macos/defaults.sh
     - killall affected apps at the end (Dock, Finder, SystemUIServer)

Phase 7: Post-install
  8. Change default shell to brew zsh (if not already)
     - Ensure brew's zsh is in /etc/shells: sudo sh -c 'echo $(brew --prefix)/bin/zsh >> /etc/shells'
     - Then: chsh -s $(brew --prefix)/bin/zsh
  9. Print next-steps checklist
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

**NEVER track or commit** (unless encrypted with age — see Encrypted Secrets section):
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

### Tool: age

[age](https://age-encryption.org/) provides simple, modern file encryption using scrypt KDF and ChaCha20-Poly1305 (AEAD). Designed by Filippo Valsorda (Go security lead).

**Install:** `brew install age`
**Security:** scrypt KDF (adjustable work factor) → ChaCha20-Poly1305 authenticated encryption

### How It Works with Stow

Unlike transparent git encryption, age uses an explicit encrypt/decrypt model:

- Encrypted files have `.age` extension and ARE committed to git
- Decrypted counterparts are gitignored
- `setup.sh` finds `.age` files, prompts for password, decrypts them (strips `.age` extension), then stows

```
ssh/
  .ssh/
    config              # plaintext (stowed normally)
    id_ed25519.age      # encrypted (committed to git)
    id_ed25519          # decrypted (gitignored, created by setup.sh)
```

### Commands

```bash
# Encrypt a file
AGE_PASSPHRASE="pw" age -e -j batchpass -o file.age file

# Decrypt a file
AGE_PASSPHRASE="pw" age -d -j batchpass -o file file.age
```

Always use `-j batchpass` with the `AGE_PASSPHRASE` env var — never `age -p` (which is interactive/TTY only and unsuitable for scripting). The batchpass plugin ships with `brew install age`.

### What This Enables

- SSH private keys CAN be tracked (as `.age` files)
- GPG secret keys CAN be tracked (as `.age` files)
- `.npmrc` with auth tokens CAN be tracked (as `.age` files)
- Any sensitive file can be encrypted and committed alongside its plaintext config

If using encrypted secrets, add the decrypted filenames to `.gitignore` (e.g., `id_ed25519`, `private-keys-v1.d/`). The `.age` versions stay tracked.

### Workflow Integration

- **Create (Workflow A):** Ask user if they want to encrypt secrets. If yes, encrypt selected files with `age -e -j batchpass`, add `.age` extension. Add decrypted filenames to `.gitignore`. Commit `.age` files.
- **Capture (Workflow B):** For files that have `.age` counterparts in the repo, prompt for password, re-encrypt current versions: `AGE_PASSPHRASE="pw" age -e -j batchpass -o file.age file`. Commit updated `.age` files.
- **Apply (Workflow C / setup.sh):** After `brew bundle` (so `age` is installed), find all `.age` files, prompt for password once, decrypt each to its non-`.age` counterpart (see setup.sh integration below). Then stow as normal — stow sees the decrypted files.

### setup.sh Integration

Add an age decrypt phase between brew bundle (Phase 2) and stow (Phase 4). Only runs if `.age` files exist in the repo:

```bash
# Phase 3: Decrypt secrets (if any)
age_files=$(find "$DOTFILES_DIR" -name '*.age' -not -path '*/.git/*')
if [ -n "$age_files" ]; then
  echo "Encrypted secrets found. Enter master passphrase to decrypt."
  read -sp "Passphrase: " AGE_PASSPHRASE; echo
  export AGE_PASSPHRASE
  for f in $age_files; do
    age -d -j batchpass -o "${f%.age}" "$f"
    echo "  Decrypted: ${f%.age}"
  done
  unset AGE_PASSPHRASE
fi
```

### Caveats

- **Password strength matters** — recommend a strong passphrase, store it in a password manager
- **Unrecoverable if lost** — if the password is lost, encrypted files cannot be recovered
- **Non-deterministic encryption** — each encryption produces different ciphertext. This is normal (age uses a random salt). Only re-encrypt when content actually changes, otherwise git sees a diff on every encryption even if the plaintext is identical.
- **Always use `-j batchpass`** — `age -p` prompts interactively on TTY and cannot be scripted. The batchpass plugin reads `AGE_PASSPHRASE` from the environment.
- **Unset passphrase after use** — always `unset AGE_PASSPHRASE` when done to avoid leaking the passphrase to child processes

---

## `.gitignore` Template

```gitignore
# Secrets & keys
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

# Decrypted secrets (age)
# When using age encryption, the .age files are committed and
# decrypted counterparts are gitignored. Add specific filenames here:
# id_ed25519
# id_ed25519.pub
# private-keys-v1.d/*

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
