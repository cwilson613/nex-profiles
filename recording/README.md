# Portable recording-rig template

This package describes a common two-mode performance-recording rig without
owning any one host's device identities or framing:

```text
sources -> audio interface -> DAW final mix -> bridge -> OBS
                       +-----> hardware monitor
```

It supports:

- a vocal mode with one main camera and one armed audio track;
- a drum mode with a main camera, detail/foot-camera PiP, stereo audio, and
  optional MIDI capture;
- a safe mode that stops and disarms recording;
- one stereo program-audio source in OBS, avoiding duplicate raw inputs;
- 48 kHz end-to-end operation by default.

## Ownership model

- `nex-profiles/recording`: portable schema, renderer, examples, and tests.
- A machine repository: concrete device UIDs, camera IDs, track names, generated
  assets, and host installation/recovery tooling.
- A session directory: performances, playlists, snapshots, and recorded media.

Do not commit credentials, OBS WebSocket passwords, streaming services, or
recorded media into this package.

## Customize

Copy the example manifest into the consuming machine repository:

```sh
cp recording/rig.example.toml rig.toml
```

Edit these classes of values:

1. Audio backend: `coreaudio` or `pipewire`.
2. Interface and bridge names/UIDs.
3. Interface channel count and monitor/bridge channel numbers.
4. Exact Ardour track names and input channels.
5. Camera names and stable IDs.
6. PiP geometry, canvas, frame rate, profile/collection names, and recording path.

Render assets:

```sh
python3.11 recording/scripts/render.py rig.toml generated/recording-rig
```

Requires Python 3.11 or newer from Homebrew, Nix, or the host package manager.

Generated output contains:

```text
generated/recording-rig/
├── ardour/scripts/*.lua
└── obs/
    ├── profiles/<profile>/basic.ini
    └── scenes/<collection>.json
```

The output is a safe seed, not a complete substitute for host validation. OBS
may normalize source settings after first load. Re-export intentionally chosen
camera transforms into the machine repository after visual framing.

## Platform adapters

### macOS/CoreAudio

Use an aggregate with the physical interface first and a two-channel virtual
bridge second. Keep the physical interface as clock master and enable drift
correction only for the bridge. Ardour uses the aggregate; macOS defaults remain
on the physical interface.

If the interface has `N` outputs, bridge channels are usually `N+1` and `N+2`.
Do not assume this: inspect the aggregate channel order.

### Linux/PipeWire

Do not reproduce a CoreAudio aggregate. PipeWire already provides graph fan-out.
Connect the Ardour program outputs to both the hardware sink and a stable virtual
or direct OBS capture node. Keep hardware/direct monitoring outside the software
round trip. Use WirePlumber rules for stable node names rather than embedding
volatile numeric IDs.

The renderer emits a Pulse/PipeWire-compatible OBS audio source for a
`pipewire` manifest, but the consuming host remains responsible for creating and
routing the named node.

## Required host validation

Before recording:

1. All program-audio devices report the manifest sample rate.
2. Hardware input meters and matching Ardour track meters both move.
3. Ardour Master reaches hardware monitoring and the OBS bridge.
4. OBS receives exactly one program mix and no webcam microphones.
5. Vocal mode arms only the vocal track.
6. Drum mode arms only drum audio and configured MIDI.
7. Safe mode stops and disarms all tracks.
8. A 20-30 second MKV contains stereo audio, stable video, and plausible sync.

## Testing

```sh
python3.11 recording/tests/test_render.py
```

The test renders an example into a temporary directory and checks mode actions,
scene membership, PiP geometry, profile sample rate, and secret hygiene.
