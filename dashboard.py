import streamlit as st
import pandas as pd
import numpy as np
import math

# Konfigurasi halaman
st.set_page_config(layout="wide", page_title="Kel 6 - Dashboard", page_icon="📄")

# Sidebar menu
st.sidebar.title("📂 Menu")
menu_pilihan = st.sidebar.radio(
    "Pilih Halaman:",
    ("Data Train", "Frekuensi dan Interval")
)

# Path file Excel
excel_path = "Tubes_Mosi.xlsx"

@st.cache_data
def load_excel_data(path):
    try:
        # Pakai engine openpyxl secara eksplisit
        df = pd.read_excel(path, sheet_name="DataTrain", engine="openpyxl")
        return df
    except FileNotFoundError:
        st.error(f"❌ File tidak ditemukan di: {path}")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"❌ Gagal membaca sheet: {e}")
        return pd.DataFrame()
    except ImportError as e:
        st.error(f"❌ Modul 'openpyxl' belum terinstal. Jalankan: pip install openpyxl")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Terjadi error saat membaca file: {e}")
        return pd.DataFrame()

# Load data
df = load_excel_data(excel_path)

# ========================
# 🟦 HALAMAN: DATA TRAIN
# ========================
if menu_pilihan == "Data Train":
    st.title("📊 Data Train Pengunjung")

    if not df.empty:
        df_display = df.reset_index(drop=True)
        df_display.index = [''] * len(df_display)
        if "Tahun" in df_display.columns:
            df_display["Tahun"] = df_display["Tahun"].astype(str)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Tidak ada data yang bisa ditampilkan.")

# =============================================
# 🟩 HALAMAN: FREKUENSI DAN INTERVAL PER DAERAH
# =============================================
elif menu_pilihan == "Frekuensi dan Interval":
    st.title("📈 Frekuensi dan Interval per Daerah")

    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()
        exclude_cols = ["id", "bulan", "tahun"]
        daerah_cols = [col for col in df.columns if col not in exclude_cols]

        daerah_options = ["pilih daerah"] + daerah_cols
        st.markdown("_Silakan pilih salah satu daerah dari daftar untuk melihat distribusi frekuensi._")
        selected_daerah = st.selectbox("📍 Daftar Daerah:", daerah_options)

        if selected_daerah == "pilih daerah":
            st.info("Pilih daerah terlebih dahulu untuk menampilkan distribusi frekuensi.")
        else:
            st.subheader(f"📊 Distribusi Frekuensi: {selected_daerah.capitalize()}")

            data = df[selected_daerah].dropna()
            n = len(data)
            x_min, x_max = data.min(), data.max()
            R = x_max - x_min
            k = math.ceil(1 + 3.3 * math.log10(n))
            h = math.ceil(R / k)

            lower = math.floor(x_min)
            bins = []
            for _ in range(k):
                upper = lower + h
                bins.append((lower, upper))
                lower = upper + 1

            labels = [f"{low} - {high}" for low, high in bins]
            cut_bins = [b[0] for b in bins] + [bins[-1][1]]

            kelas = pd.cut(data, bins=cut_bins, labels=labels, include_lowest=True, right=True)
            freq_table = kelas.value_counts().sort_index().reset_index()
            freq_table.columns = ["Interval Jumlah", "Frekuensi"]
            freq_table = freq_table[freq_table["Frekuensi"] > 0].reset_index(drop=True)

            freq_table["No"] = range(1, len(freq_table) + 1)
            total = freq_table["Frekuensi"].sum()
            prob_raw = freq_table["Frekuensi"] / total
            prob_rounded = prob_raw.round(2)
            selisih = 1.00 - prob_rounded.sum()
            if abs(selisih) > 0:
                idx_max = prob_rounded.idxmax()
                prob_rounded.iloc[idx_max] += selisih
                prob_rounded = prob_rounded.round(2)

            freq_table["Probabilitas"] = prob_rounded
            freq_table["Prob. Kumulatif"] = freq_table["Probabilitas"].cumsum().round(2)

            upper_bounds = (freq_table["Prob. Kumulatif"] * 100).astype(int)
            lower_bounds = [1] + [ub + 1 for ub in upper_bounds[:-1]]
            freq_table["Interval Angka Acak"] = [
                f"{lb} - {ub}" for lb, ub in zip(lower_bounds, upper_bounds)
            ]

            freq_table = freq_table[[
                "No", "Interval Jumlah", "Frekuensi", "Probabilitas", "Prob. Kumulatif", "Interval Angka Acak"
            ]]
            st.dataframe(freq_table, use_container_width=True)

            st.markdown("---")
            st.markdown("### ℹ️ Informasi Tambahan")
            st.markdown(f"Jumlah Data (n): {n}")
            st.markdown(f"x_min: {x_min}")
            st.markdown(f"x_max: {x_max}")
            st.markdown(f"Jangkauan (R): {R}")
            st.markdown(f"Jumlah Kelas (k): {k}")
            st.markdown(f"Panjang Kelas (h): {h}")
    else:
        st.warning("Data tidak tersedia.")
