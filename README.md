# nex-profiles

Community base profiles for [nex](https://nex.styrene.io). Opinionated, platform-specific starter configs that you extend with your own personal or machine-specific profile.

## Profiles

| Profile | Platform | Description |
|---------|----------|-------------|
| [mac](mac/profile.toml) | macOS | Developer Mac with sane defaults — kitty, Firefox, dark mode, clean dock, fast keyboard, TouchID, bash |

More coming: `linux-desktop`, `linux-server`, `linux-edge`.

## How it works

Each profile is a `profile.toml` that nex can apply to configure a machine from scratch. Profiles use the `extends` field for inheritance — your personal profile extends a base, and nex merges them:

```
nex-profiles/mac                 (community base)
    ^
cwilson613/nex-personal          (your SSH keys, kubeconfig, aliases)
```

```
nex-profiles/linux-desktop       (community base)
    ^
cwilson613/nex-gamingpc          (AMD GPU, Steam, COSMIC specifics)
```

Packages, aliases, and settings are merged — not replaced — so the base gives you a solid foundation and your personal profile layers on private config.

## Usage

```sh
# Apply directly
nex profile apply cwilson613/nex-profiles/mac

# Or extend in your own profile.toml
[meta]
extends = "cwilson613/nex-profiles/mac"
```

## What the mac profile configures

**Packages**: bash, kitty, firefox, ripgrep, fd, eza, bat, jq, yq, curl, wget, htop, git, vim, GNU coreutils/sed/awk/findutils

**Shell**: bash default, eza/bat aliases

**Dock**: stripped to Finder, Firefox, kitty, System Settings. Auto-hide, no recents.

**Keyboard**: fast repeat, no auto-correct, no smart quotes/dashes/capitalize, full keyboard access

**Trackpad**: tap to click, natural scrolling

**Finder**: show extensions + hidden files, list view, path/status bars, search current folder

**Screenshots & Recordings**: save to `~/Screenshots`, no shadow

**Security**: TouchID for sudo, immediate lock (TouchID makes unlock instant)

**Power**: 45 min display sleep, never system sleep/hibernate

**Other**: dark mode, expanded save/print dialogs, save to disk not iCloud, no .DS_Store on network/USB, no quarantine dialog, Bluetooth on, no hot corners
