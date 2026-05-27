# Nex profile matrix

The catalog is organized by a prescriptive matrix:

```text
hardware class + purpose = starter profile pattern
```

Names are descriptive; the matrix is normative. A personal repository such as
`nex-gamingpc` maps to a reusable matrix row such as
`starter/amd64-amd-gaming`.

## First starter rows

| Hardware class | Purpose | Starter ID | Nix system | Notes |
|---|---|---|---|---|
| `amd64-generic` | `cli` | `starter/amd64-cli` | `x86_64-linux` | Minimal command-line baseline. |
| `amd64-generic` | `server` | `starter/amd64-server` | `x86_64-linux` | Headless server baseline. |
| `amd64-amd-desktop` | `gaming` | `starter/amd64-amd-gaming` | `x86_64-linux` | Public pattern derived from `nex-gamingpc`. |
| `amd64-generic` | `low-latency-audio` | `starter/amd64-low-latency-audio` | `x86_64-linux` | Public pattern derived from `nex-jamkit`. |
| `amd64-generic` | `vm-base` | `starter/amd64-vm-base` | `x86_64-linux` | VM guest base for deterministic image builds. |
| `amd64-generic` | `cloud-base` | `starter/amd64-cloud-base` | `x86_64-linux` | Cloud guest base for external image factories. |
| `arm64-rpi4` | `edge-node` | `starter/arm64-rpi4-edge-node` | `aarch64-linux` | Raspberry Pi 4 field node. |
| `arm64-rpi4` | `kiosk` | `starter/arm64-rpi4-kiosk` | `aarch64-linux` | Raspberry Pi 4 kiosk/display appliance. |
| `arm64-rpi4` | `mesh-node` | `starter/arm64-rpi4-mesh-node` | `aarch64-linux` | Raspberry Pi 4 mesh/MANET node. |

## Future rows

Future rows are tracked in the Nex design node `hardware-purpose-profile-matrix`.
Do not infer taxonomy from repo names; add rows here when a starter becomes
concrete.
