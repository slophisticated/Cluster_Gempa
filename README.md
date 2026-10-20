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

Gunakan **Python 3.12** dan pip, lalu jalankan dari direktori repository:

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

Dependensi aplikasi dikunci di `requirements.txt`. Kedua artefak `.joblib`
menyimpan versi **scikit-learn 1.6.1**; versi ini dipakai agar tidak memuat model
dengan versi scikit-learn berbeda. Kombinasi dependensi yang dicantumkan telah
diuji pada Windows dengan Python 3.12.14: halaman aplikasi dan prediksi manual
berjalan, dua input sintetis menghasilkan label `[3, 3]`, dan seluruh **8.731**
label historis cocok dengan hasil model. macOS, Linux, dan deployment cloud
belum diuji untuk kombinasi ini.

Ini adalah lingkungan aplikasi yang diuji, bukan rekonstruksi lengkap
lingkungan pelatihan: versi NumPy/SciPy saat pelatihan belum tercatat.
Dependensi transitif juga belum dikunci seluruhnya. Jika melatih ulang,
simpan versi lingkungan bersama seluruh artefak baru; lihat
[panduan persistensi model scikit-learn](https://scikit-learn.org/stable/model_persistence.html).
Muat hanya file Joblib dari sumber yang dipercaya.

Untuk memeriksa artefak dan data historis setelah instalasi:

```sh
python scripts/check_models.py
```

Pemeriksaan menolak versi scikit-learn yang berbeda, membandingkan label
historis dan jumlah tiap cluster dengan metadata, serta menjalankan contoh
sintetis. Ini memeriksa konsistensi file, bukan akurasi ilmiah model.

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
Keempat fitur harus berupa angka berhingga. Aplikasi melewati baris dengan fitur
kosong dan menampilkan jumlahnya; jika tidak ada baris lengkap, prediksi tidak
dijalankan. CSV kosong, format rusak, encoding selain UTF-8, teks pada fitur
numerik, serta nilai tak hingga ditolak dengan pesan untuk memperbaiki file.

Input manual dibatasi pada lintang -11 hingga 6, bujur 95 hingga 141,
kedalaman 0 hingga 700 km, dan magnitudo 4.5 hingga 9.5. Unggahan CSV memakai
batas yang sama: file dengan nilai di luar batas ditolak, bukan
dipotong ke nilai batas. Hasil unduhan berisi kolom input, `Cluster`, dan `Nama Cluster`.

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
| [csv_input.py](csv_input.py) | Validasi fitur CSV dan batas input yang dipakai aplikasi |
| [Notebook analisis](Clustering_Gempa_Indonesia_USGS.ipynb) | Persiapan data, perbandingan model, evaluasi, dan ekspor artefak |
| [requirements.txt](requirements.txt) | Versi dependensi aplikasi yang sudah diuji |
| [scripts/check_models.py](scripts/check_models.py) | Pemeriksaan konsistensi artefak dan label historis |
| [gempa_indonesia_usgs.csv](gempa_indonesia_usgs.csv) | Salinan katalog yang digunakan notebook |
| [data_cluster.csv](data_cluster.csv) | Empat fitur dan label historis untuk peta |
| [cluster_info.json](cluster_info.json) | Nama, deskripsi, dan statistik lima cluster |
| [scaler_gempa.joblib](scaler_gempa.joblib) | Scaler yang sudah dilatih |
| [kmeans_gempa.joblib](kmeans_gempa.joblib) | Model K-Means yang sudah dilatih |

Notebook memerlukan lingkungan analisis terpisah dengan paket tambahan untuk
plotting dan notebook; `requirements.txt` saat ini ditujukan untuk aplikasi.
Mengulang notebook dapat menulis ulang artefak dan `requirements.txt`, jadi
gunakan salinan kerja saat bereksperimen.

## Memeriksa unggahan CSV

Jalankan pengujian validasi dan alur aplikasi dari root repository setelah
dependensi aplikasi terpasang:

```sh
python -m unittest discover -s tests -v
```

Pengujian memakai CSV sintetis serta artefak model yang tersedia; tidak meminta
data USGS atau melatih ulang model.
