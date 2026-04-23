# nex-profiles

Composable profile fragments for [nex](https://nex.styrene.io). Mix and match to build your system config.

## Fragments

Fragments are the atoms of a nex profile. Each one handles a single concern. Compose them in your `profile.toml` and nex merges everything together.

| Category | Fragments | Description |
|----------|-----------|-------------|
| **core** | `essentials` | CLI tools, GNU userland, git defaults — the stuff every machine needs |
| **platform** | `macos`, `linux` | OS-level defaults (system prefs, networking, nix settings) |
| **desktop** | `cosmic`, `gnome`, `kde`, `hyprland` | Desktop environment config (Linux only) |
| **gpu** | `amd`, `nvidia`, `intel` | GPU drivers, Vulkan, hardware acceleration (Linux only) |
| **audio** | `pipewire`, `pulseaudio` | Audio backend config (Linux only) |
| **shell** | `bash`, `zsh`, `fish` | Default shell, completions, history |
| **role** | `dev`, `gaming`, `server`, `edge` | Use-case packages and services |

## Compose order

Fragments are merged in the order listed. Later fragments win on scalar values; arrays (like package lists) are concatenated and deduped.

```toml
# Last writer wins: if core/essentials sets dark_mode = false
# and platform/macos sets dark_mode = true, you get true.
compose = [
  "core/essentials",
  "platform/macos",
  "shell/bash",
  "role/dev",
]
```

## Dependencies

Fragments declare what they require:

```toml
[fragment]
name     = "cosmic"
requires = ["platform/linux"]
```

Nex validates the dependency graph before applying. If you compose `desktop/cosmic` without `platform/linux`, it errors.

## Examples

**Mac developer workstation:**

```toml
[meta]
name = "my-mac"
compose = [
  "core/essentials",
  "platform/macos",
  "shell/bash",
  "role/dev",
]
```

**AMD gaming desktop (what nex-gamingpc becomes):**

```toml
[meta]
name = "gaming-pc"
compose = [
  "core/essentials",
  "platform/linux",
  "desktop/cosmic",
  "gpu/amd",
  "audio/pipewire",
  "shell/bash",
  "role/gaming",
]
```

**Headless server:**

```toml
[meta]
name = "homelab-node"
compose = [
  "core/essentials",
  "platform/linux",
  "shell/bash",
  "role/server",
]
```

**Edge device:**

```toml
[meta]
name = "sensor-node"
compose = [
  "platform/linux",
  "shell/bash",
  "role/edge",
]
```

(Note: edge skips `core/essentials` to keep the footprint minimal.)

## Inheritance

Assembled profiles live in their own repos and can be extended further:

```
nex-profiles (fragments)
    │
    │  compose
    ▼
styrene-lab/nex-mac              (assembled: essentials + macos + bash + dev)
    │
    │  extends
    ▼
cwilson613/nex-personal          (private: SSH keys, kubeconfig, aliases)
```

```
nex-profiles (fragments)
    │
    │  compose
    ▼
styrene-lab/nex-linux-desktop    (assembled: essentials + linux + cosmic + pipewire)
    │
    │  extends
    ▼
cwilson613/nex-gamingpc          (machine-specific: AMD GPU, Steam, COSMIC favorites)
```

## Shell config pipeline

The `[shell]` section in a profile TOML generates a home-manager nix module that manages your bash (or future: zsh/fish) dotfiles declaratively. Here's how data flows:

```
profile.toml [shell] section
        │
        │  nex profile apply
        ▼
~/macos-nix/nix/modules/home/shell.nix    (generated nix module)
        │
        │  nex switch (darwin-rebuild)
        ▼
~/.profile      ← sessionVariables + profileExtra
~/.bash_profile ← sources ~/.profile, then ~/.bashrc
~/.bashrc       ← aliases, historySize, initExtra, bash-completion
```

### TOML fields

| Field | Maps to | Purpose |
|-------|---------|---------|
| `[shell.aliases]` | `programs.bash.shellAliases` | Shell aliases (merged across overlays) |
| `[shell.env]` | `home.sessionVariables` | Env vars exported at login |
| `profileExtra` | `programs.bash.profileExtra` | Login shell init (Homebrew PATH, Cargo, etc.) |
| `initExtra` | `programs.bash.initExtra` | Interactive shell init (pipefail, tool PATH, etc.) |

### History settings

`HISTSIZE`, `HISTFILESIZE`, and `HISTCONTROL` are intercepted from `[shell.env]` and mapped to native home-manager options (`programs.bash.historySize`, etc.) instead of `home.sessionVariables`. This is because home-manager's `programs.bash` sets its own history defaults in `.bashrc`, which would override values set via `.profile` session variables.

### Overlay merging

When a profile uses `extends`, the base profile is applied first and the overlay merges on top:

- **Aliases and env vars**: overlay wins on key conflicts, base values are preserved
- **profileExtra / initExtra**: overlay content is appended after base content
- **History settings**: overlay values override base values

### Git identity inheritance

**Important:** The `[git]` section in a base profile sets `git config --global user.name` and `user.email`. If you extend someone else's profile, their git identity is applied first. You **must** override `[git]` in your own overlay, or you'll unknowingly commit as the base profile's author.

```toml
# Your overlay — always include this
[git]
name = "Your Name"
email = "your-email@example.com"
```

### Keeping secrets out

Public profiles should only contain non-sensitive config. Machine-specific or private config (SSH keys, kubeconfig paths, work-specific aliases) goes in a private overlay:

```toml
# Private overlay (e.g. cwilson613/nex-personal)
extends = "cwilson613/nex-profiles"

[shell.aliases]
clod = "claude --dangerously-skip-permissions"

[shell.env]
KUBECONFIG = "$HOME/.kube/work.kubeconfig"
```

## Fresh Mac setup

For a colleague setting up a new MacBook:

```sh
# 1. Install nex (requires curl — available on stock macOS)
curl -fsSL https://nex.styrene.io/install.sh | sh

# 2. Bootstrap the system (installs Nix, Homebrew, Xcode CLT, scaffolds config)
nex init

# 3. Apply your profile (or extend someone else's)
nex profile apply your-user/your-profile

# 4. Activate
nex switch
```

`nex init` handles the full dependency chain: Nix installer, Homebrew installer (which triggers Xcode Command Line Tools / git), config scaffolding, and first build. If git is somehow missing after Homebrew, nex will fail with a clear message pointing to `xcode-select --install`.

## Making your own

1. Pick your fragments
2. Create a repo with a `profile.toml`
3. Apply it: `nex profile apply your-user/your-profile`

Or use the builder: `nex profile init` walks you through the decision tree and generates a `profile.toml` from fragments.

See [nex.styrene.io](https://nex.styrene.io) for docs.
