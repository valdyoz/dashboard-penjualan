import streamlit as st
import pandas as pd

# =============================================
# KONFIGURASI HALAMAN
# =============================================
st.set_page_config(page_title="Dashboard Penjualan", layout="wide")

# =============================================
# BACA DATA DARI FILE EXCEL
# =============================================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    # Bersihkan nama kolom
    new_columns = []
    for col in df.columns:
        try:
            new_columns.append(str(col).strip())
        except:
            new_columns.append(col)
    df.columns = new_columns

    # Konversi kolom tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], dayfirst=True)

    # Hitung kolom Total
    df["Total"] = df["Qty"] * df["Harga"]

    return df

df = load_data()

# =============================================
# SIDEBAR - FILTER
# =============================================
st.sidebar.header("🔍 Filter Data")

list_wilayah = ["Semua"] + list(df["Wilayah"].unique())
pilihan_wilayah = st.sidebar.selectbox("Pilih Wilayah", list_wilayah)

min_date = df["Tanggal"].min().date()
max_date = df["Tanggal"].max().date()
pilihan_tanggal = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

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
st.title("📊 Dashboard Penjualan")
st.markdown("---")

# =============================================
# METRIC CARDS
# =============================================
col1, col2, col3 = st.columns(3)

total_penjualan = df_filtered["Total"].sum()
total_qty = df_filtered["Qty"].sum()
rata_transaksi = df_filtered["Total"].mean()

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
# VISUALISASI (STREAMLIT NATIVE - TANPA PLOTLY)
# =============================================
if not df_filtered.empty:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Tren Penjualan Harian")
        df_harian = df_filtered.groupby("Tanggal")["Total"].sum().reset_index()
        df_harian = df_harian.set_index("Tanggal")
        st.line_chart(df_harian, use_container_width=True)

    with col_right:
        st.subheader("📊 Penjualan per Produk")
        df_produk = df_filtered.groupby("Produk")["Total"].sum().reset_index()
        df_produk = df_produk.set_index("Produk")
        st.bar_chart(df_produk, use_container_width=True)

    col_left2, col_right2 = st.columns([1, 1])

    with col_left2:
        st.subheader("🗺️ Kontribusi per Wilayah")
        df_wilayah = df_filtered.groupby("Wilayah")["Total"].sum().reset_index()
        # Pie chart pakai bar chart horizontal sebagai gantinya
        st.bar_chart(df_wilayah.set_index("Wilayah"), use_container_width=True, horizontal=True)

    with col_right2:
        st.subheader("📦 Transaksi Terbesar")
        top_10 = df_filtered.nlargest(10, "Total")[["Tanggal", "Produk", "Wilayah", "Total"]]
        top_10["Tanggal"] = top_10["Tanggal"].dt.strftime("%d %b %Y")
        st.dataframe(top_10, use_container_width=True, hide_index=True)

    st.markdown("---")

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
