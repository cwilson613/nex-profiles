#!/usr/bin/env python3
"""Render portable Ardour action scripts and an OBS seed collection from a rig manifest."""

from __future__ import annotations

import argparse
import configparser
import json
from pathlib import Path
import uuid

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.9-3.10
    import tomli as tomllib


def q(value: str) -> str:
    return json.dumps(value)


def action_script(name: str, description: str, tracks: list[str]) -> str:
    conditions = " or ".join(f"name == {q(track)}" for track in tracks)
    expected = ", ".join(tracks)
    return f'''ardour {{
  ["type"] = "EditorAction",
  name = {q(name)},
  author = "recording-rig renderer",
  description = {q(description)}
}}

function factory () return function ()
  if Session:actively_recording() then return end
  local found = 0
  for track in Session:get_tracks():iter() do
    local name = track:name()
    local arm = {conditions}
    track:rec_enable_control():set_value(arm and 1 or 0, PBD.GroupControlDisposition.NoGroup)
    if arm then found = found + 1 end
  end
  Session:save_state("")
  if found ~= {len(tracks)} then
    LuaDialog.Message(
      {q(name)},
      {q('Expected tracks: ' + expected)},
      LuaDialog.MessageType.Warning,
      LuaDialog.ButtonType.Close
    ):run()
  end
end end
'''


def safe_script() -> str:
    return '''ardour {
  ["type"] = "EditorAction",
  name = "Recording Mode: Safe Stop",
  author = "recording-rig renderer",
  description = [[Stop transport, disarm every track, and save the session.]]
}

function factory () return function ()
  Session:request_stop(false, false, ARDOUR.TransportRequestSource.TRS_UI)
  for track in Session:get_tracks():iter() do
    track:rec_enable_control():set_value(0, PBD.GroupControlDisposition.NoGroup)
  end
  Session:save_state("")
end end
'''


def source(name: str, kind: str, settings: dict, mixers: int = 0) -> dict:
    return {
        "prev_ver": 536936450,
        "name": name,
        "uuid": str(uuid.uuid4()),
        "id": kind,
        "versioned_id": kind,
        "settings": settings,
        "mixers": mixers,
        "sync": 0,
        "flags": 0,
        "volume": 1.0,
        "balance": 0.5,
        "enabled": True,
        "muted": False,
        "hotkeys": {},
        "deinterlace_mode": 0,
        "deinterlace_field_order": 0,
        "monitoring_type": 0,
        "private_settings": {},
    }


def item(src: dict, item_id: int, *, x: int = 0, y: int = 0,
         width: int = 0, height: int = 0) -> dict:
    return {
        "name": src["name"], "source_uuid": src["uuid"], "visible": True,
        "locked": True, "rot": 0.0, "pos": {"x": float(x), "y": float(y)},
        "scale": {"x": 1.0, "y": 1.0}, "align": 5,
        "bounds_type": 2 if width and height else 0, "bounds_align": 0,
        "bounds": {"x": float(width), "y": float(height)},
        "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0,
        "crop_to_bounds": False, "id": item_id, "group_item_backup": False,
    }


def scene(name: str, items: list[dict]) -> dict:
    result = source(name, "scene", {
        "id_counter": max((entry["id"] for entry in items), default=0),
        "custom_size": False, "items": items,
    })
    result["hotkeys"] = {"OBSBasic.SelectScene": []}
    result["canvas_uuid"] = "6c69626f-6273-4c00-9d88-c5136d61696e"
    return result


def render(manifest: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    ardour = output / "ardour" / "scripts"
    obs_profiles = output / "obs" / "profiles"
    obs_scenes = output / "obs" / "scenes"
    ardour.mkdir(parents=True, exist_ok=True)
    obs_profiles.mkdir(parents=True, exist_ok=True)
    obs_scenes.mkdir(parents=True, exist_ok=True)

    tracks = manifest["tracks"]
    vocals = [tracks["vocals"]["name"]]
    drums = [tracks["drums"]["name"]]
    if tracks["drums"].get("record_midi"):
        drums.append(tracks["drums"]["midi_track"])
    (ardour / "vocals_arm_only.lua").write_text(action_script(
        "Vocals: Arm Only", "Arm the vocal recording mode only.", vocals))
    (ardour / "drums_arm_only.lua").write_text(action_script(
        "Drums: Arm Audio + MIDI Only", "Arm the drum recording mode only.", drums))
    (ardour / "recording_mode_safe_stop.lua").write_text(safe_script())

    width, height = manifest["canvas_width"], manifest["canvas_height"]
    video, obs, names = manifest["video"], manifest["obs"], manifest["scenes"]
    backend = manifest["audio"]["backend"]
    camera_kind = "macos-avcapture" if backend == "coreaudio" else "v4l2_input"
    camera_key = "device" if backend == "coreaudio" else "device_id"
    audio_kind = "coreaudio_input_capture" if backend == "coreaudio" else "pulse_input_capture"
    audio_key = "device_id"
    program = source(obs["program_audio_name"], audio_kind,
                     {audio_key: manifest["audio"]["bridge_uid"]}, 1)
    main = source(video["main"]["name"], camera_kind,
                  {camera_key: video["main"]["device_id"],
                   "device_name": video["main"]["device_name"]})
    detail = source(video["detail"]["name"], camera_kind,
                    {camera_key: video["detail"]["device_id"],
                     "device_name": video["detail"]["device_name"]})
    pip = video["pip"]
    detail_x = width - pip["width"] - pip["right_margin"]
    detail_y = height - pip["height"] - pip["bottom_margin"]
    vocals_scene = scene(names["vocals"], [
        item(main, 1, width=width, height=height), item(program, 2)])
    drums_scene = scene(names["drums"], [
        item(main, 1, width=width, height=height),
        item(detail, 2, x=detail_x, y=detail_y,
             width=pip["width"], height=pip["height"]), item(program, 3)])
    safe_scene = scene(names["safe"], [])
    collection = {
        "name": obs["collection_name"],
        "sources": [program, main, detail, vocals_scene, drums_scene, safe_scene],
        "groups": [], "scene_order": [{"name": n} for n in
            (names["vocals"], names["drums"], names["safe"])],
        "current_scene": names["safe"], "current_program_scene": names["safe"],
        "canvases": [], "current_transition": "Fade", "transition_duration": 300,
        "transitions": [], "quick_transitions": [], "saved_projectors": [],
        "preview_locked": False, "scaling_enabled": False, "scaling_level": 0,
        "scaling_off_x": 0.0, "scaling_off_y": 0.0, "modules": {}, "version": 2,
    }
    (obs_scenes / f'{obs["collection_name"].replace(" ", "-")}.json').write_text(
        json.dumps(collection, indent=2) + "\n")

    profile_dir = obs_profiles / obs["profile_name"].replace(" ", "-")
    profile_dir.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser(); config.optionxform = str
    config["General"] = {"Name": obs["profile_name"]}
    config["SimpleOutput"] = {
        "FilePath": str(Path(obs["recording_path"]).expanduser()),
        "RecFormat2": obs["recording_format"], "RecEncoder": obs["encoder"],
        "RecQuality": "Small", "ABitrate": "320", "RecTracks": "1",
    }
    config["Video"] = {
        "BaseCX": str(width), "BaseCY": str(height), "OutputCX": str(width),
        "OutputCY": str(height), "FPSCommon": str(manifest["fps"]),
        "ColorSpace": "709", "ColorRange": "Partial",
    }
    config["Audio"] = {"SampleRate": str(manifest["sample_rate"]),
                       "ChannelSetup": "Stereo"}
    with (profile_dir / "basic.ini").open("w") as handle:
        config.write(handle, space_around_delimiters=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = tomllib.loads(args.manifest.read_text())
    if manifest.get("schema") != "io.styrene.recording-rig.v1":
        raise SystemExit("unsupported recording-rig schema")
    render(manifest, args.output)


if __name__ == "__main__":
    main()
