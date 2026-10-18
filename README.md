# Clustering Gempa Bumi Indonesia

Aplikasi Streamlit untuk mengeksplorasi kelompok gempa historis di wilayah
Indonesia berdasarkan **lintang, bujur, kedalaman, dan magnitudo**. Model
K-Means menempatkan input ke salah satu dari lima cluster; hasilnya ditampilkan
bersama ringkasan dan peta data historis.

**Ini adalah studi clustering, bukan prediksi kapan gempa akan terjadi,
peringatan dini, atau penilaian keselamatan suatu lokasi.** Nomor cluster adalah
label kelompok, bukan urutan tingkat bahaya.

## Yang bisa dicoba

- **Prediksi Satu Gempa:** masukkan empat fitur untuk melihat cluster dan
  titik historis dalam kelompok yang sama.
- **Prediksi dari File CSV:** unggah beberapa baris sekaligus, lihat jumlah
  per cluster, lalu unduh hasil beserta nama cluster.
- **Tentang Cluster:** lihat deskripsi, statistik, dan persebaran data yang
  sudah dikelompokkan.

## Menjalankan aplikasi

Siapkan Python dan pip, lalu jalankan dari direktori repository:

```sh
git clone https://github.com/slophisticated/Cluster_Gempa.git
cd Cluster_Gempa
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
source .venv/bin/activate
```

Pasang dependensi dan buka aplikasi:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit. Pertahankan direktori kerja di
root repository: aplikasi membaca model, metadata, dan CSV melalui path relatif.
Artefak model sudah tersedia, sehingga menjalankan aplikasi tidak memerlukan
pelatihan ulang.

Versi dependensi belum dikunci di `requirements.txt`, dan versi lingkungan
pelatihan belum tercatat di notebook. Kompatibilitas model `.joblib` dengan
semua versi scikit-learn belum dijamin. Jika muncul peringatan versi model,
gunakan lingkungan pelatihan yang sesuai atau latih dan ekspor ulang seluruh
artefak dengan versi yang sama; lihat
[panduan persistensi model scikit-learn](https://scikit-learn.org/stable/model_persistence.html).
Muat hanya file Joblib dari sumber yang dipercaya.

## Contoh CSV

Unggah [contoh input sintetis](examples/gempa-sintetis.csv) pada tab
**Prediksi dari File CSV**. Barisnya merupakan contoh format, bukan laporan
kejadian gempa nyata:

```csv
latitude,longitude,depth,mag
-3.5,100.5,25.0,5.0
-7.0,110.0,80.0,4.8
```

| Kolom | Makna dan satuan |
| --- | --- |
| `latitude` | Lintang desimal; negatif berarti selatan |
| `longitude` | Bujur desimal; positif berarti timur |
| `depth` | Kedalaman dalam kilometer |
| `mag` | Magnitudo, bukan intensitas guncangan di suatu lokasi |

Gunakan header persis seperti contoh dan titik sebagai pemisah desimal.
Keempat fitur harus numerik. Aplikasi membuang baris dengan fitur kosong,
tetapi belum menyediakan penanganan khusus untuk CSV rusak, teks pada fitur
numerik, atau file tanpa baris valid.

Input manual dibatasi pada lintang -11 hingga 6, bujur 95 hingga 141,
kedalaman 0 hingga 700 km, dan magnitudo 4.5 hingga 9.5. Batas ini belum
diterapkan pada unggahan CSV; siapkan data dengan cakupan yang sesuai sebelum
mengunggah. Hasil unduhan berisi kolom input, `Cluster`, dan `Nama Cluster`.

## Data dan metode

Notebook menggunakan [USGS Earthquake Catalog](https://earthquake.usgs.gov/earthquakes/search/)
dengan filter wilayah Indonesia, periode yang dinyatakan 2015–2024, dan
magnitudo minimum 4.5. Salinan data tersedia di repository. Notebook membaca
CSV lokal terlebih dahulu dan hanya meminta data USGS jika file itu tidak ada.

Empat fitur distandardisasi dengan `StandardScaler`. Notebook membandingkan
K-Means, Hierarchical Clustering, dan DBSCAN; aplikasi memakai K-Means dengan
lima cluster. Nama serta deskripsi cluster merupakan interpretasi studi dan
tersimpan terpisah dari model.

## Isi repository

| File | Kegunaan |
| --- | --- |
| [app.py](app.py) | Antarmuka Streamlit dan penempatan input ke cluster |
| [Notebook analisis](Clustering_Gempa_Indonesia_USGS.ipynb) | Persiapan data, perbandingan model, evaluasi, dan ekspor artefak |
| [requirements.txt](requirements.txt) | Dependensi aplikasi, belum dikunci versinya |
| [gempa_indonesia_usgs.csv](gempa_indonesia_usgs.csv) | Salinan katalog yang digunakan notebook |
| [data_cluster.csv](data_cluster.csv) | Empat fitur dan label historis untuk peta |
| [cluster_info.json](cluster_info.json) | Nama, deskripsi, dan statistik lima cluster |
| [scaler_gempa.joblib](scaler_gempa.joblib) | Scaler yang sudah dilatih |
| [kmeans_gempa.joblib](kmeans_gempa.joblib) | Model K-Means yang sudah dilatih |

Notebook memerlukan lingkungan analisis terpisah dengan paket tambahan untuk
plotting dan notebook; `requirements.txt` saat ini ditujukan untuk aplikasi.
Mengulang notebook dapat menulis ulang artefak dan `requirements.txt`, jadi
gunakan salinan kerja saat bereksperimen.
