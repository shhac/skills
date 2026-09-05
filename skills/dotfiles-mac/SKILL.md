---
name: dotfiles-mac
description: 'Create, update, or apply a macOS dotfiles repo with GNU Stow. Use to back up system configuration, capture current configs, or set up a new Mac.'
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
├── shell/                      # → ~/.zshrc.shared, ~/.zprofile, etc.
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

- Local `~/.zshrc` bootstrap (not stowed) → sources `~/.zshrc.shared` then `~/.zshrc.local`
- `.zshrc.shared` is tracked and stowed from `shell/.zshrc.shared`
- `.gitconfig` → `[include] path = ~/.gitconfig.local`
- `.ssh/config` → `Include ~/.ssh/config.local` at top

All `.local` files are gitignored. This avoids templating engines entirely.

---

## Instructions

You are helping a user manage their macOS dotfiles. Determine which workflow applies:

- **Create**: User has no dotfiles repo — audit their system, generate the repo
- **Update/Capture**: User has a dotfiles repo — capture current system state into it
- **Apply**: User has a dotfiles repo — apply it to a new or existing machine

If unclear, ask the user which workflow they want.

---

### Workflow A: Create a New Dotfiles Repo

#### Step 1: Audit the System

Scan the user's machine to discover what's worth tracking. Run these in parallel where possible:

**Existing dotfiles managers:**
- Check for chezmoi (`~/.local/share/chezmoi/`), yadm (`~/.local/share/yadm/`), or bare git repos in `$HOME` (`~/.cfg/`, `~/.dotfiles.git/`)
- If detected, warn the user before proceeding — creating a competing dotfiles system can cause conflicts

**Homebrew:**
```bash
brew bundle dump --force --describe --file="$(mktemp /tmp/dotfiles-audit-Brewfile.XXXXXX)"
```

**Shell configs:**
- Check for `~/.zshrc`, `~/.zsh/`, `~/.zprofile`, `~/.zshenv`, `~/.bashrc`, `~/.bash_profile`
- Fish: `~/.config/fish/config.fish`, `~/.config/fish/conf.d/`, `~/.config/fish/functions/`
- Detect framework: Oh My Zsh (`~/.oh-my-zsh/`), Prezto, Starship, plain zsh
- For fish or bash users, skip zsh-specific sections (Oh My Zsh, zsh plugins) and adapt shell configuration steps accordingly
- If Oh My Zsh: note custom themes in `~/.oh-my-zsh/custom/themes/` and custom plugins in `~/.oh-my-zsh/custom/plugins/` — these are user content worth tracking. Do NOT track OMZ core (it's managed by its own installer).

**Git:**
- Read `~/.gitconfig` (may contain `[user]` with name/email — fine to track)
- Check for conditional includes (`[includeIf]` sections) — these reference paths that may need adjustment on other machines. Suggest moving `[includeIf]` blocks to `~/.gitconfig.local` since they reference machine-specific paths
- Check for `~/.gitignore_global` or equivalent

**SSH:**
- Read `~/.ssh/config` (track this)
- NEVER track `~/.ssh/id_*`, `~/.ssh/*.pub`, `~/.ssh/known_hosts`, `~/.ssh/authorized_keys`

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
- VS Code/Cursor settings live in `~/Library/Application Support/` (path with spaces). These can't be managed cleanly with stow — handle with direct symlinks in setup.sh instead:
  ```bash
  ln -sf "$DOTFILES_DIR/vscode/.config/Code/User/settings.json" \
    "$HOME/Library/Application Support/Code/User/settings.json"
  ```

**Other common configs:**
- tmux: `~/.tmux.conf` or `~/.config/tmux/tmux.conf`
- Starship: `~/.config/starship.toml`
- ripgrep: `~/.ripgreprc`
- bat: `~/.config/bat/config`
- Any `~/.config/` subdirectories for tools installed via Homebrew
- Check `$XDG_CONFIG_HOME` (default: `~/.config/`). If set to a non-default path, use it as the stow target (`-t $XDG_CONFIG_HOME`) for packages that install into `~/.config/`.

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
  - Any file containing token prefixes listed in the Security Rules section below
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
9. Ensure shell setup uses local bootstrap + shared tracked config pattern:
   - `~/.zshrc` is local bootstrap (not stowed)
   - tracked `shell/.zshrc.shared` is stowed to `~/.zshrc.shared`
   - local bootstrap sources `~/.zshrc.shared` and `~/.zshrc.local`
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
brew bundle dump --force --describe --file="$(mktemp /tmp/dotfiles-capture-Brewfile.XXXXXX)"
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

### shell/.zshrc.shared
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
4. Ask the user: "Proceed with applying these changes?" — never run setup.sh without explicit confirmation

#### Step 2: Run Setup

Execute `setup.sh` or walk through it step by step if the user prefers. See Setup Script section for the execution order.

If setup.sh fails partway through: the script uses `set -euo pipefail` so it stops on error. Some steps may have already completed (packages installed, some stow links created). Since each phase is idempotent, it's safe to fix the issue and re-run the script. Watch for stow conflicts or partial symlinks that may need manual cleanup before re-running.

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
     - Use unattended mode and preserve local bootstrap: `CHSH=no RUNZSH=no KEEP_ZSHRC=yes ... --unattended --keep-zshrc`
  6. NVM (if selected)
     - Install with profile mutation disabled: `... | PROFILE=/dev/null bash`

Phase 5: Configuration
  7. Ensure local ~/.zshrc bootstrap exists (not stowed)
     - Local ~/.zshrc sources ~/.zshrc.shared and ~/.zshrc.local
     - If an unmanaged ~/.zshrc exists, migrate it to ~/.zshrc.local before writing bootstrap
  8. Stow all packages
     - For each directory that isn't os-*, .git, or special files:
       - Check for os-macos/ override → stow that instead if present
       - Backup conflicting real files to ~/.dotfiles-backup/<timestamp>/
       - stow --no-folding -d $DOTFILES_DIR -t $HOME <package>
     - Exclude shell/.zshrc from stow (local bootstrap is intentionally unmanaged)
     - Skip packages the user has excluded (via env var or config)

Phase 6: System Preferences (opt-in)
  9. macOS defaults (only if explicitly requested or --with-defaults flag)
     - Source os-macos/defaults.sh
     - killall affected apps at the end (Dock, Finder, SystemUIServer)

Phase 7: Post-install
  10. Change default shell to brew zsh (if not already)
      - Ensure brew's zsh is in /etc/shells: sudo sh -c 'echo $(brew --prefix)/bin/zsh >> /etc/shells'
      - Then: chsh -s $(brew --prefix)/bin/zsh
  11. Print next-steps checklist
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
- Files containing `-----BEGIN.*PRIVATE KEY-----` headers
- Files whose secret-named fields hold a **real value**

**Judge the value, not the key name.** A field called `token` or `password` does
not by itself make a file unsafe. Many modern CLIs (commonly Go and Rust ones)
keep the real secret in the OS keychain and leave a placeholder in the config —
literal sentinels like `__KEYCHAIN__`, `keychain:`, `<stored>`, or a sibling
`keychain_managed: true` flag. Such files are portable configuration and are
usually the *most* valuable thing to track, because they carry profile names,
hostnames, and account IDs that are tedious to rebuild by hand.

Before excluding a config file, check what the secret-named fields actually
contain:

```bash
# Show secret-named fields and whether they hold a value or a placeholder
python3 - "$FILE" <<'PY'
import json, sys
KEYS = ("password","token","secret","key","cookie","passphrase","credential")
def walk(n, t=()):
    if isinstance(n, dict):
        for k, v in n.items(): walk(v, t + (k,))
    elif isinstance(n, list):
        for i, v in enumerate(n): walk(v, t + (str(i),))
    elif isinstance(n, str) and t and any(x in t[-1].lower() for x in KEYS):
        print(f"{'.'.join(t)} = {'PLACEHOLDER' if not n or n.isupper() or n.startswith('__') else f'VALUE ({len(n)} chars)'}")
walk(json.load(open(sys.argv[1])))
PY
```

Read the output, don't gate on it — it flags names, and some secret-sounding
fields hold references rather than secrets. `connections.<name>.credential`
naming a credential *alias* to look up is a common shape, as are `key` fields
holding a config key name. Judge each hit.

If every hit is a placeholder or a reference, the file is safe to track in
plaintext. If any holds a real value, exclude it, encrypt it, or split it per
the mixed-content rule below.

Be aware that a file safe today is not guaranteed safe tomorrow — a future
version of the tool could start storing a token inline. If you track such files,
re-run the check on every capture rather than trusting a one-off audit.

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

This works for files nothing rewrites — SSH keys, GPG keys, static rc files. It
does **not** work for config a running tool writes back to. See *Tool-managed
config cannot be stowed* under Gotchas before stowing anything an application
owns.

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

- **Password strength matters** — recommend a strong passphrase, store it in a password manager. If the repo is public this is a hard requirement, not advice: see *Publishing encrypted files* under Gotchas.
- **Unrecoverable if lost** — if the password is lost, encrypted files cannot be recovered. Have the user prove they can decrypt before they depend on it.
- **Non-deterministic encryption** — each encryption produces different ciphertext. This is normal (age uses a random salt). Only re-encrypt when content actually changes, otherwise git sees a diff on every encryption even if the plaintext is identical. See *Archiving and encrypting reproducibly* under Gotchas for how to detect "actually changed" correctly.
- **Always use `-j batchpass`** — `age -p` prompts interactively on TTY and cannot be scripted. The batchpass plugin reads `AGE_PASSPHRASE` from the environment.
- **Unset passphrase after use** — always `unset AGE_PASSPHRASE` when done to avoid leaking the passphrase to child processes

---

---

## Gotchas

Hard-won failures. Each is silent — the command succeeds and the damage shows up
later — so check for them rather than waiting for a report.

### Tool-managed config cannot be stowed

Any application that writes its config **atomically** — temp file in the same
directory, then `rename()` over the target — destroys a stow symlink the first
time it saves. `rename()` replaces the symlink; it does not follow it. This is
the normal safe-write pattern, so assume it for anything a running program owns:
CLI tools that store profiles or credentials, editors, browsers, most Go and
Rust tools.

The second-order effect is worse than the broken link. Once the symlink is a
regular file, the next stow run sees a conflict, backs up the *live* file, and
relinks to the now-stale repo copy — silently reverting every change the user
made since. They lose real configuration and nothing reports it.

Verify before stowing anything an application writes:

```bash
# after stowing, make the app save its config, then:
[ -L ~/.config/<tool>/config.json ] && echo "symlink survived" || echo "REPLACED — do not stow this"
```

For these files use **copy-in/copy-out** instead of stow: an explicit command
that copies repo → `$HOME` on apply, and `$HOME` → repo on capture. State this
plainly in the repo's README, because it is the one place the usual "edit the
symlink, edit the repo" rule does not hold.

Static configs the user edits by hand (`.zshrc`, `.gitconfig`, `.tmux.conf`) are
unaffected — stow them normally.

### Silent fallbacks that look like success

A setup script that defaults to a safe-sounding value when a required setting is
missing will report success having done nothing. On a new machine that is the
difference between a restored config and an empty one, reported identically.

Prefer: ask when interactive, fail with the valid options when not, and warn
when a step completes having changed nothing.

### A check that always fails gets ignored

Any drift or health check that cannot reach a clean state trains the user to
skip its output — which defeats every other check it prints alongside. If a
warning cannot be resolved, fix the underlying declaration or silence it
explicitly with a recorded reason. Two common causes on macOS:

- **`mas` vs `cask` vs manual installs.** A `mas` entry for an app installed
  from the web (or a `cask` entry for one installed by hand) can never be
  satisfied, because `brew bundle` only sees what it installed. Either adopt the
  existing install (`brew install --cask <name> --adopt`) or drop the entry.
- **Re-encrypting unchanged content.** See below.

### Archiving and encrypting reproducibly

If the repo bundles or encrypts files, every default in the chain is
non-deterministic, so a no-op capture produces a diff:

- **age emits different ciphertext every run.** Gate re-encryption on the
  *plaintext* changing — commit a hash beside the blob and compare.
- **Hash file contents, not the archive.** Tar embeds mtimes, modes and uid/gid,
  and bsdtar (macOS) differs from GNU tar (Linux), so an archive hash reports
  drift when nothing changed. Restoring files and `chmod`-ing them is enough to
  break it. Hash a sorted list of `(content hash, relative path)` instead.
- **`COPYFILE_DISABLE=1` is required on macOS.** Otherwise bsdtar silently
  embeds AppleDouble (`._*`) members for extended attributes — invisible to
  `tar tf`, and they change the bytes.
- **`tar czf` is non-deterministic**; gzip stamps its own mtime. Use
  `tar cf - | gzip -n`.

### Publishing encrypted files

If the dotfiles repo is public, encrypted blobs are archived permanently by
forks, clones, and third-party mirrors. A later passphrase compromise
retroactively decrypts every historical blob, and re-encrypting does not
unpublish the old ones — there is no rotation path.

Confirm the repo's visibility before proposing encrypted secrets, and if it is
public, say this plainly rather than implying encryption makes it safe. Prefer a
private repo for anything sensitive. Where a public repo is the deliberate
choice, require a generated passphrase and check the user can actually unlock
the bootstrap file *before* they rely on it — discovering a wrong passphrase on
a new machine is discovering it too late.

Note also that per-file `.age` publishes its filenames. If the file *names*
disclose something (which services an organisation uses, say), bundle before
encrypting so only the archive name is visible.

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
