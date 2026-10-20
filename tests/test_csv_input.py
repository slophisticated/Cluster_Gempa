import io
import unittest

from csv_input import FEATURES, read_prediction_csv


HEADER = ",".join(FEATURES) + "\n"


class CsvInputTests(unittest.TestCase):
    def test_exact_limits_are_accepted(self):
        data, skipped = read_prediction_csv(io.StringIO(
            HEADER + "-11,95,0,4.5\n6,141,700,9.5\n"
        ))
        self.assertEqual(skipped, 0)
        self.assertEqual(data.shape, (2, 4))

    def test_each_feature_rejects_both_sides_of_its_limits(self):
        limits = {"latitude": (-11, 6), "longitude": (95, 141),
                  "depth": (0, 700), "mag": (4.5, 9.5)}
        for feature, (low, high) in limits.items():
            for value in [low - 0.001, high + 0.001]:
                with self.subTest(feature=feature, value=value):
                    row = dict(zip(FEATURES, [-3.5, 100.5, 25, 5]))
                    row[feature] = value
                    with self.assertRaisesRegex(ValueError, feature):
                        read_prediction_csv(io.StringIO(HEADER + ",".join(map(str, row.values()))))

    def test_extra_columns_and_original_row_order_are_preserved(self):
        csv = "event,mag,depth,longitude,latitude\nA,5,25,100.5,-3.5\nB,5,25,100,\nC,4.8,80,110,-7\n"
        data, skipped = read_prediction_csv(io.StringIO(csv))
        self.assertEqual(skipped, 1)
        self.assertEqual(data["event"].tolist(), ["A", "C"])
        self.assertEqual(data["latitude"].tolist(), [-3.5, -7])

    def test_missing_column_is_named(self):
        with self.assertRaisesRegex(ValueError, "Kolom berikut tidak ditemukan: mag"):
            read_prediction_csv(io.StringIO("latitude,longitude,depth\n-3,100,25\n"))

    def test_extra_fields_are_not_silently_shifted_or_truncated(self):
        with self.assertRaisesRegex(ValueError, "jumlah kolom"):
            read_prediction_csv(io.StringIO(HEADER + "ignored,-3,100,25,5\n"))

    def test_invalid_utf8_has_recovery_message(self):
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            read_prediction_csv(io.BytesIO(HEADER.encode() + b"-3,100,25,\xff\n"))

    def test_non_finite_and_text_values_name_the_column(self):
        for value in ["inf", "-inf", "1e999", "south"]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "latitude"):
                    read_prediction_csv(io.StringIO(HEADER + f"{value},100,25,5\n"))


if __name__ == "__main__":
    unittest.main()
