#!/usr/bin/env python3
from __future__ import annotations

import configparser
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RenderTest(unittest.TestCase):
    def test_example_renders_expected_contract(self) -> None:
        interpreter = "/opt/homebrew/bin/python3.14"
        if not Path(interpreter).exists():
            interpreter = "python3"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            subprocess.run([
                interpreter, str(ROOT / "recording/scripts/render.py"),
                str(ROOT / "recording/rig.example.toml"), str(output),
            ], check=True)

            collection_path = next((output / "obs/scenes").glob("*.json"))
            collection = json.loads(collection_path.read_text())
            sources = {source["name"]: source for source in collection["sources"]}
            self.assertEqual(collection["scene_order"], [
                {"name": "VOCALS"}, {"name": "DRUMS"}, {"name": "SAFE"}])
            self.assertEqual(
                [item["name"] for item in sources["VOCALS"]["settings"]["items"]],
                ["Main Camera", "PROGRAM - DAW Mix"],
            )
            drum_items = sources["DRUMS"]["settings"]["items"]
            self.assertEqual([item["name"] for item in drum_items], [
                "Main Camera", "Detail Camera", "PROGRAM - DAW Mix"])
            detail = drum_items[1]
            self.assertEqual(detail["bounds"], {"x": 576.0, "y": 324.0})
            self.assertEqual(detail["pos"], {"x": 1296.0, "y": 708.0})
            self.assertEqual(sources["PROGRAM - DAW Mix"]["mixers"], 1)

            profile_path = next((output / "obs/profiles").glob("*/basic.ini"))
            profile = configparser.ConfigParser()
            profile.read(profile_path)
            self.assertEqual(profile["Audio"]["SampleRate"], "48000")
            self.assertEqual(profile["SimpleOutput"]["RecFormat2"], "mkv")

            vocals = (output / "ardour/scripts/vocals_arm_only.lua").read_text()
            drums = (output / "ardour/scripts/drums_arm_only.lua").read_text()
            safe = (output / "ardour/scripts/recording_mode_safe_stop.lua").read_text()
            self.assertIn('name == "Vocal"', vocals)
            self.assertIn('name == "Drums Audio"', drums)
            self.assertIn('name == "Drums MIDI"', drums)
            self.assertIn("request_stop", safe)

            rendered = "\n".join(path.read_text() for path in output.rglob("*") if path.is_file())
            for forbidden in ("server_password", "stream_key", "oauth_token"):
                self.assertNotIn(forbidden, rendered.lower())


if __name__ == "__main__":
    unittest.main()
