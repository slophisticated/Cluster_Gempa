import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
HEADER = "latitude,longitude,depth,mag\n"


class CsvUploadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_cwd = Path.cwd()
        os.chdir(ROOT)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.original_cwd)

    def run_upload(self, csv):
        with patch("streamlit.file_uploader", return_value=io.BytesIO(csv)):
            return AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()

    def test_invalid_uploads_show_actionable_error(self):
        cases = {
            "empty": b"",
            "header_only": HEADER.encode(),
            "missing_values_only": (HEADER + ",100,25,5\n").encode(),
            "text_in_features": (HEADER + "south,100,25,5\n").encode(),
            "infinity": (HEADER + "-3,100,inf,5\n").encode(),
            "broken_csv": (HEADER + '-3,100,25,"5\n').encode(),
            "outside_input_range": (HEADER + "-90,100,25,5\n").encode(),
        }
        for name, csv in cases.items():
            with self.subTest(name=name):
                app = self.run_upload(csv)
                self.assertFalse(app.exception, [e.message for e in app.exception])
                self.assertEqual(len(app.error), 1)
                self.assertNotIn("Traceback", app.error[0].value)

    def test_valid_upload_keeps_predictions(self):
        app = self.run_upload((ROOT / "examples/gempa-sintetis.csv").read_bytes())
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertFalse(app.error)
        self.assertEqual(app.dataframe[0].value["Cluster"].tolist(), [3, 3])

    def test_skipped_missing_rows_are_reported(self):
        app = self.run_upload((HEADER + "-3.5,100.5,25,5\n,100,25,5\n").encode())
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertFalse(app.error)
        self.assertEqual(len(app.dataframe[0].value), 1)
        self.assertEqual(len(app.warning), 1)

    def test_manual_prediction_still_works(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
        app.button[0].click().run()
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertIn("Cluster 3", app.success[0].value)


if __name__ == "__main__":
    unittest.main()
