import importlib.util
import math
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "src" / "python" / "psfascii_metrics.py"
SPEC = importlib.util.spec_from_file_location("psfascii_metrics", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PsfAsciiMetricsTests(unittest.TestCase):
    def test_unwrap_degrees(self):
        values = [
            complex(math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            for angle in (-170, 170, 150)
        ]
        self.assertEqual(MODULE.unwrap_degrees(values), [-170.0, -190.0, -210.0])

    def test_calculate_interpolates_unity_crossing(self):
        ac_text = '''VALUE
"freq" 1.0e+00
"out" (1.0e+01 0.0e+00)
"ym" (0.0e+00 0.0e+00)
"freq" 1.0e+01
"out" (7.0710678119e-01 -7.0710678119e-01)
"ym" (0.0e+00 0.0e+00)
"freq" 1.0e+02
"out" (0.0e+00 -1.0e-01)
"ym" (0.0e+00 0.0e+00)
'''
        dc_text = '''VALUE
"out" "V" 5.5e-01
"VDD:p" "I" -6.6e-05
END
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ac_path = root / "ac.ac"
            dc_path = root / "dcOp.dc"
            ac_path.write_text(ac_text, encoding="utf-8")
            dc_path.write_text(dc_text, encoding="utf-8")
            metrics = MODULE.calculate(ac_path, dc_path, "out", "ym")

        self.assertAlmostEqual(metrics["gain_db"], 20.0, places=6)
        self.assertAlmostEqual(metrics["ugf_hz"], 10.0, places=6)
        self.assertAlmostEqual(metrics["phase_margin_deg"], 135.0, places=6)
        self.assertAlmostEqual(metrics["out_dc_v"], 0.55, places=6)
        self.assertAlmostEqual(metrics["supply_current_a"], 66e-6, places=9)


if __name__ == "__main__":
    unittest.main()
