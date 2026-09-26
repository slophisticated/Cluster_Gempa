import json

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Clustering Gempa Indonesia", page_icon="🌋", layout="wide")

FEATURES = ["latitude", "longitude", "depth", "mag"]
# Warna tiap cluster (hex) untuk peta
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


# 1. Memuat artefak model (disimpan di cache agar tidak dimuat ulang setiap interaksi)
@st.cache_resource
def load_model():
    scaler = joblib.load("scaler_gempa.joblib")
    model = joblib.load("kmeans_gempa.joblib")
    with open("cluster_info.json") as f:
        info = {int(k): v for k, v in json.load(f).items()}
    return scaler, model, info


@st.cache_data
def load_data():
    try:
        return pd.read_csv("data_cluster.csv")
    except FileNotFoundError:
        return None


scaler, model, cluster_info = load_model()
data = load_data()


# 2. Fungsi prediksi cluster
def prediksi_cluster(df_input):
    X = df_input[FEATURES]
    X_scaled = pd.DataFrame(scaler.transform(X), columns=FEATURES)
    return model.predict(X_scaled)


# 3. Tampilan aplikasi
st.title("🌋 Clustering Gempa Bumi Indonesia")
st.write(
    "Aplikasi ini mengelompokkan gempa bumi ke dalam salah satu dari "
    f"**{len(cluster_info)} zona gempa** hasil model K-Means yang dilatih pada katalog "
    "gempa USGS wilayah Indonesia 2015–2024 (M ≥ 4,5)."
)

tab1, tab2, tab3 = st.tabs(["🔍 Prediksi Satu Gempa", "📄 Prediksi dari File CSV", "ℹ️ Tentang Cluster"])

# ---------- Tab 1: input manual ----------
with tab1:
    col_input, col_hasil = st.columns([1, 2])

    with col_input:
        st.subheader("Data Gempa")
        lat = st.number_input("Latitude (−11 s.d. 6)", min_value=-11.0, max_value=6.0,
                              value=-3.5, step=0.1, format="%.4f")
        lon = st.number_input("Longitude (95 s.d. 141)", min_value=95.0, max_value=141.0,
                              value=100.5, step=0.1, format="%.4f")
        depth = st.number_input("Kedalaman (km)", min_value=0.0, max_value=700.0,
                                value=25.0, step=1.0)
        mag = st.number_input("Magnitudo", min_value=4.5, max_value=9.5,
                              value=5.0, step=0.1)
        tombol = st.button("Prediksi Cluster", type="primary")

    with col_hasil:
        if tombol:
            input_df = pd.DataFrame([[lat, lon, depth, mag]], columns=FEATURES)
            cluster = int(prediksi_cluster(input_df)[0])
            info = cluster_info[cluster]

            st.success(f"Gempa ini masuk ke **Cluster {cluster}: {info['nama']}**")
            st.write(info["deskripsi"])

            if "jumlah_gempa" in info:
                m1, m2, m3 = st.columns(3)
                m1.metric("Jumlah gempa historis", f"{info['jumlah_gempa']:,}".replace(",", "."))
                m2.metric("Kedalaman rata-rata", f"{info['depth_rata2']:.0f} km")
                m3.metric("Magnitudo rata-rata", f"{info['mag_rata2']:.2f}")

            if data is not None:
                st.caption("Titik merah besar = gempa yang diinput. Titik lain = gempa historis pada cluster yang sama.")
                peta = data[data["KMeans_Cluster"] == cluster][["latitude", "longitude"]].copy()
                peta["color"] = COLORS[cluster % len(COLORS)] + "80"
                peta["size"] = 6000
                titik = pd.DataFrame({"latitude": [lat], "longitude": [lon],
                                      "color": ["#ff0000"], "size": [40000]})
                st.map(pd.concat([peta, titik]), latitude="latitude", longitude="longitude",
                       color="color", size="size")
        else:
            st.info("Masukkan data gempa di sebelah kiri, lalu klik **Prediksi Cluster**.")

# ---------- Tab 2: upload CSV ----------
with tab2:
    st.write("Upload file CSV yang memiliki kolom `latitude`, `longitude`, `depth`, dan `mag` "
             "(misalnya hasil download dari USGS).")
    file = st.file_uploader("Pilih file CSV", type="csv")

    if file is not None:
        df_upload = pd.read_csv(file)
        kurang = [c for c in FEATURES if c not in df_upload.columns]

        if kurang:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(kurang)}")
        else:
            df_upload = df_upload.dropna(subset=FEATURES).copy()
            df_upload["Cluster"] = prediksi_cluster(df_upload)
            df_upload["Nama Cluster"] = df_upload["Cluster"].map(lambda c: cluster_info[int(c)]["nama"])

            st.write(f"**{len(df_upload)}** gempa berhasil diprediksi.")
            st.dataframe(df_upload[FEATURES + ["Cluster", "Nama Cluster"]])

            st.subheader("Jumlah gempa per cluster")
            st.bar_chart(df_upload["Nama Cluster"].value_counts())

            df_upload["color"] = df_upload["Cluster"].map(lambda c: COLORS[int(c) % len(COLORS)])
            st.map(df_upload, latitude="latitude", longitude="longitude", color="color", size=8000)

            st.download_button("Download hasil (CSV)", df_upload.drop(columns="color").to_csv(index=False),
                               file_name="hasil_prediksi_cluster.csv", mime="text/csv")

# ---------- Tab 3: penjelasan cluster ----------
with tab3:
    tabel = pd.DataFrame([
        {"Cluster": c, "Nama": v["nama"], "Deskripsi": v["deskripsi"],
         "Jumlah Gempa": v.get("jumlah_gempa"), "Kedalaman Rata-rata (km)": v.get("depth_rata2"),
         "Magnitudo Rata-rata": v.get("mag_rata2")}
        for c, v in sorted(cluster_info.items())
    ])
    st.dataframe(tabel, hide_index=True)

    if data is not None:
        st.subheader("Peta seluruh gempa per cluster")
        semua = data.copy()
        semua["color"] = semua["KMeans_Cluster"].map(lambda c: COLORS[int(c) % len(COLORS)])
        st.map(semua, latitude="latitude", longitude="longitude", color="color", size=5000)
        st.caption("  ·  ".join(f"Cluster {c}: {COLORS[c % len(COLORS)]}" for c in sorted(cluster_info)))

st.divider()
st.caption("Sumber data: USGS Earthquake Catalog (earthquake.usgs.gov) · Model: K-Means (scikit-learn)")
