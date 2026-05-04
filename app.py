import streamlit as st
import pandas as pd
import plotly.express as px

# =============================================
# KONFIGURASI HALAMAN
# =============================================
st.set_page_config(page_title="Dashboard Penjualan", layout="wide")

# =============================================
# BACA DATA DARI FILE EXCEL
# =============================================
@st.cache_data
def load_data():
    # Baca file Excel
    df = pd.read_excel("Book1.xlsx")

    # BERSIHKAN NAMA KOLOM DARI SPASI TERSEMBUNYI
    df.columns = df.columns.str.strip()

    # Konversi kolom tanggal (format Indonesia: dd/mm/yyyy)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], dayfirst=True)

    # Hitung kolom Total
    df["Total"] = df["Qty"] * df["Harga"]

    return df

df = load_data()

# =============================================
# SIDEBAR - FILTER
# =============================================
st.sidebar.header("🔍 Filter Data")

# Filter Wilayah
list_wilayah = ["Semua"] + list(df["Wilayah"].unique())
pilihan_wilayah = st.sidebar.selectbox("Pilih Wilayah", list_wilayah)

# Filter Tanggal
min_date = df["Tanggal"].min().date()
max_date = df["Tanggal"].max().date()
pilihan_tanggal = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Terapkan Filter
df_filtered = df.copy()
if pilihan_wilayah != "Semua":
    df_filtered = df_filtered[df_filtered["Wilayah"] == pilihan_wilayah]

if len(pilihan_tanggal) == 2:
    start_date, end_date = pilihan_tanggal
    df_filtered = df_filtered[
        (df_filtered["Tanggal"].dt.date >= start_date) &
        (df_filtered["Tanggal"].dt.date <= end_date)
    ]

# =============================================
# JUDUL
# =============================================
st.title("📊 Dashboard Penjualan - Book1")
st.markdown("---")

# =============================================
# METRIC CARDS (KPI)
# =============================================
col1, col2, col3 = st.columns(3)

total_penjualan = df_filtered["Total"].sum()
total_qty = df_filtered["Qty"].sum()
rata_transaksi = df_filtered["Total"].mean()

# Cegah error kalau data kosong
if pd.isna(rata_transaksi):
    rata_transaksi = 0

with col1:
    st.metric(label="💰 Total Penjualan", value=f"Rp {total_penjualan:,.0f}")

with col2:
    st.metric(label="📦 Total Qty Terjual", value=f"{total_qty:,}")

with col3:
    st.metric(label="📈 Rata-rata Transaksi", value=f"Rp {rata_transaksi:,.0f}")

st.markdown("---")

# =============================================
# VISUALISASI
# =============================================
# Hanya tampilkan grafik kalau data ada
if not df_filtered.empty:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Tren Penjualan Harian")
        df_harian = df_filtered.groupby("Tanggal")["Total"].sum().reset_index()
        fig_line = px.line(
            df_harian, x="Tanggal", y="Total",
            labels={"Total": "Total Penjualan (Rp)"},
            template="plotly_white"
        )
        fig_line.update_traces(line_color="#2E86C1")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        st.subheader("📊 Penjualan per Produk")
        df_produk = df_filtered.groupby("Produk")["Total"].sum().reset_index().sort_values("Total", ascending=False)
        fig_bar = px.bar(
            df_produk, x="Produk", y="Total", color="Produk",
            labels={"Total": "Total Penjualan (Rp)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    col_left2, col_right2 = st.columns([1, 1])

    with col_left2:
        st.subheader("🗺️ Kontribusi per Wilayah")
        df_wilayah = df_filtered.groupby("Wilayah")["Total"].sum().reset_index()
        fig_pie = px.pie(
            df_wilayah, values="Total", names="Wilayah",
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right2:
        st.subheader("📦 Transaksi Terbesar")
        top_10 = df_filtered.nlargest(10, "Total")[["Tanggal", "Produk", "Wilayah", "Total"]]
        top_10["Tanggal"] = top_10["Tanggal"].dt.strftime("%d %b %Y")
        st.dataframe(top_10, use_container_width=True, hide_index=True)

    st.markdown("---")

    # =============================================
    # TABEL DETAIL (TOGGLE)
    # =============================================
    st.subheader("📋 Data Detail")
    if st.checkbox("Tampilkan Semua Data"):
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        st.download_button(
            label="⬇️ Download Data sebagai CSV",
            data=df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="data_penjualan.csv",
            mime="text/csv"
        )
else:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter yang dipilih.")