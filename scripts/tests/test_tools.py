from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL_ROOT / "scripts"
INSPECT_3MF = SCRIPTS / "inspect_3mf.py"
VALIDATE_STL = SCRIPTS / "validate_stl_blender.py"
BLENDER = Path(r"D:\blender.exe")


TWO_TETRAHEDRA_STL = """solid main
facet normal 0 0 -1
 outer loop
  vertex 0 0 0
  vertex 12 0 0
  vertex 0 12 0
 endloop
endfacet
facet normal 0 -1 0
 outer loop
  vertex 0 0 0
  vertex 0 0 12
  vertex 12 0 0
 endloop
endfacet
facet normal 1 1 1
 outer loop
  vertex 12 0 0
  vertex 0 0 12
  vertex 0 12 0
 endloop
endfacet
facet normal -1 0 0
 outer loop
  vertex 0 0 0
  vertex 0 12 0
  vertex 0 0 12
 endloop
endfacet
endsolid main
solid stray
facet normal 0 0 -1
 outer loop
  vertex 30 0 0
  vertex 32 0 0
  vertex 30 2 0
 endloop
endfacet
facet normal 0 -1 0
 outer loop
  vertex 30 0 0
  vertex 30 0 2
  vertex 32 0 0
 endloop
endfacet
facet normal 1 1 1
 outer loop
  vertex 32 0 0
  vertex 30 0 2
  vertex 30 2 0
 endloop
endfacet
facet normal -1 0 0
 outer loop
  vertex 30 0 0
  vertex 30 2 0
  vertex 30 0 2
 endloop
endfacet
endsolid stray
"""


class Inspect3mfTests(unittest.TestCase):
    def test_writes_manifest_with_stl_hash_and_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stl = root / "dripper_v2_body.stl"
            stl.write_bytes(b"test stl payload")
            archive = root / "slice.3mf"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("3D/3dmodel.model", '<model><item path="dripper_v2_body.stl" /></model>')
                zf.writestr(
                    "Metadata/model_settings.config",
                    '<config><part source_file="dripper_v2_body.stl" /></config>',
                )
            output = root / "3mf_manifest.json"

            result = subprocess.run(
                [sys.executable, str(INSPECT_3MF), str(archive), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["stl_files"][0]["file_name"], stl.name)
            self.assertEqual(manifest["stl_files"][0]["version"], "v2")
            self.assertEqual(manifest["stl_files"][0]["sha256"], hashlib.sha256(stl.read_bytes()).hexdigest())
            self.assertIn("Metadata/model_settings.config", manifest["config_references"])


@unittest.skipUnless(BLENDER.exists(), "Blender is required for STL validation integration test")
class ValidateStlTests(unittest.TestCase):
    def test_reports_each_component_and_applies_fluid_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stl = Path(directory) / "two_components.stl"
            stl.write_text(TWO_TETRAHEDRA_STL, encoding="utf-8")
            result = subprocess.run(
                [
                    str(BLENDER),
                    "-b",
                    "--python",
                    str(VALIDATE_STL),
                    "--",
                    "--product-rules",
                    "fluid-container",
                    str(stl),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            json_start = result.stdout.find("{")
            json_end = result.stdout.rfind("}") + 1
            report = json.loads(result.stdout[json_start:json_end])
            file_report = report["files"][0]
            self.assertEqual(file_report["component_count"], 2)
            self.assertEqual(file_report["components"][0]["role"], "main")
            self.assertEqual(file_report["components"][1]["role"], "stray_shell")
            self.assertIn("euler_chi", file_report["components"][0])
            self.assertIn("genus_if_closed_orientable", file_report["components"][0])
            self.assertTrue(file_report["basic_pass"])
            self.assertFalse(file_report["product_rule_results"]["passes"])
            self.assertEqual(report["evidence_level"], "cad_mesh_passed")


if __name__ == "__main__":
    unittest.main()
