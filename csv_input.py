"""Membaca fitur CSV sesuai batas input aplikasi."""

import warnings

import numpy as np
import pandas as pd


FEATURE_LIMITS = {
    "latitude": (-11.0, 6.0),
    "longitude": (95.0, 141.0),
    "depth": (0.0, 700.0),
    "mag": (4.5, 9.5),
}
FEATURES = list(FEATURE_LIMITS)


def read_prediction_csv(file):
    """Kembalikan data valid dan jumlah baris dengan fitur kosong yang dilewati."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", pd.errors.ParserWarning)
            df = pd.read_csv(file, index_col=False)
    except pd.errors.EmptyDataError as error:
        raise ValueError("File CSV kosong. Tambahkan header dan setidaknya satu baris data.") from error
    except (pd.errors.ParserError, pd.errors.ParserWarning) as error:
        raise ValueError("CSV tidak dapat dibaca. Periksa jumlah kolom dan tanda kutip, lalu unggah ulang.") from error
    except UnicodeDecodeError as error:
        raise ValueError("File tidak dapat dibaca sebagai UTF-8. Simpan ulang CSV dengan encoding UTF-8.") from error

    missing = [column for column in FEATURES if column not in df.columns]
    if missing:
        raise ValueError(f"Kolom berikut tidak ditemukan: {', '.join(missing)}")

    valid = df.dropna(subset=FEATURES).copy()
    skipped = len(df) - len(valid)
    if valid.empty:
        raise ValueError("Tidak ada baris dengan empat fitur lengkap. Isi latitude, longitude, depth, dan mag.")

    numbers = valid[FEATURES].apply(pd.to_numeric, errors="coerce")
    invalid = numbers.columns[(~np.isfinite(numbers)).any()].tolist()
    if invalid:
        raise ValueError(f"Gunakan angka berhingga pada kolom: {', '.join(invalid)}. Gunakan titik untuk desimal.")

    outside = [
        f"{column} ({low:g} s.d. {high:g})"
        for column, (low, high) in FEATURE_LIMITS.items()
        if (~numbers[column].between(low, high)).any()
    ]
    if outside:
        raise ValueError(f"Nilai di luar batas input aplikasi: {', '.join(outside)}. Perbaiki data lalu unggah ulang.")

    valid[FEATURES] = numbers
    return valid, skipped
