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

## Making your own

1. Pick your fragments
2. Create a repo with a `profile.toml`
3. Apply it: `nex profile apply your-user/your-profile`

Or use the builder: `nex profile init` walks you through the decision tree and generates a `profile.toml` from fragments.

See [nex.styrene.io](https://nex.styrene.io) for docs.
