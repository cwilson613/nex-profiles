# nex-profiles

> Archived: this personal fork has moved to [`styrene-lab/nex-profiles`](https://github.com/styrene-lab/nex-profiles).

This repository is retained only as a compatibility pointer for old links. Do not use it as the canonical base for new Nex profiles.

Use the Styrene-owned profile library instead:

```sh
nex profile apply styrene-lab/nex-profiles
```

Private overlays should extend the Styrene base:

```toml
[meta]
extends = "styrene-lab/nex-profiles"
```

Current known overlays have already moved to the Styrene base, including:

- `cwilson613/nex-personal`
- `cwilson613/nex-gamingpc`
- `recro/nex-coe`
- `styrene-lab/nex-jamkit`

Historical content remains available in git history.
