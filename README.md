# nex profile

Personal macOS workstation profile for [nex](https://nex.styrene.io).

## Quick start

On a fresh Mac:

```sh
curl -fsSL https://nex.styrene.io/install.sh | sh
nex init
nex profile apply cwilson613/nex-profiles
```

This installs all packages, shell config, git settings, and macOS preferences
defined in `profile.toml`.

## What's in here

| Section | What it configures |
|---|---|
| `[packages]` | nix packages, brew formulae, brew casks, taps |
| `[shell]` | Default shell, aliases, environment variables |
| `[git]` | Name, email, default branch, pull/push behavior |
| `[macos]` | Finder, Dock, trackpad, fonts |
| `[security]` | TouchID for sudo |

## Making your own

Fork this repo, edit `profile.toml`, push. Then:

```sh
nex profile apply <your-github-user>/nex-profiles
```

See [nex.styrene.io](https://nex.styrene.io) for docs.
