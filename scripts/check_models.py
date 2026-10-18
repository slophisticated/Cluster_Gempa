"""Periksa konsistensi artefak tepercaya dengan label historis repository."""

from collections import Counter
import json
from pathlib import Path
import warnings

import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning


ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["latitude", "longitude", "depth", "mag"]


def main():
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        try:
            scaler = joblib.load(ROOT / "scaler_gempa.joblib")
            model = joblib.load(ROOT / "kmeans_gempa.joblib")
        except InconsistentVersionWarning as error:
            raise SystemExit(
                "Versi scikit-learn tidak cocok dengan artefak. "
                "Pasang dependensi dari requirements.txt sebelum memeriksa model."
            ) from error

    history = pd.read_csv(ROOT / "data_cluster.csv")
    if history.empty:
        raise SystemExit("Data historis kosong; tidak ada label yang dapat diperiksa.")
    scaled = pd.DataFrame(scaler.transform(history[FEATURES]), columns=FEATURES)
    predicted = model.predict(scaled)
    mismatches = int((predicted != history["KMeans_Cluster"].to_numpy()).sum())
    if mismatches:
        raise SystemExit(f"Label model berbeda pada {mismatches} baris historis.")

    with (ROOT / "cluster_info.json").open(encoding="utf-8") as source:
        metadata = json.load(source)
    expected_counts = {int(key): value["jumlah_gempa"] for key, value in metadata.items()}
    if dict(Counter(int(label) for label in predicted)) != expected_counts:
        raise SystemExit("Jumlah baris per cluster tidak cocok dengan cluster_info.json.")

    sample = pd.read_csv(ROOT / "examples" / "gempa-sintetis.csv")
    sample_scaled = pd.DataFrame(scaler.transform(sample[FEATURES]), columns=FEATURES)
    sample_labels = model.predict(sample_scaled)
    if sample_labels.tolist() != [3, 3]:
        raise SystemExit("Label contoh sintetis berbeda dari hasil acuan [3, 3].")

    print(f"OK: {len(history)} label historis dan jumlah {len(metadata)} cluster cocok.")
    print(f"OK: contoh sintetis menghasilkan label {sample_labels.tolist()}.")
    print("Pemeriksaan ini memverifikasi konsistensi artefak, bukan akurasi atau bahaya gempa.")


if __name__ == "__main__":
    main()
