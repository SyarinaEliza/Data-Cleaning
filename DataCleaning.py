import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title=" Data Cleaning App", layout="wide")

st.title("🧹Data Cleaning App")
st.write("Upload CSV or Excel files, explore data issues, and clean only what you need.")

uploaded_file = st.file_uploader(
    "📤 Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_type = "csv"
    else:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("📄 Select Excel Sheet", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        file_type = "excel"

    st.success("File loaded successfully!")

    st.subheader("📊 Data Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Cells", int(df.isnull().sum().sum()))

    st.subheader("🔍 Data Types")

    dtypes_df = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": df.dtypes.astype(str)
    })
    st.dataframe(dtypes_df, use_container_width=True)

    st.subheader("❗ Missing Values by Column")

    missing_df = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Missing Count": df.isnull().sum().values,
        "Missing %": (df.isnull().mean().values * 100).round(2)
    })
    st.dataframe(missing_df, use_container_width=True)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    st.subheader("🛠 Data Cleaning Options")

    df_cleaned = df.copy()

    # Remove duplicates
    if st.checkbox("Remove duplicate rows"):
        df_cleaned = df_cleaned.drop_duplicates()

    # Column selection
    columns_to_clean = st.multiselect(
        "Select columns to clean missing values",
        df_cleaned.columns.tolist()
    )

    cleaning_method = st.selectbox(
        "Select cleaning method",
        ["None", "Drop rows", "Fill with mean", "Fill with median", "Fill with mode"]
    )

    if cleaning_method != "None" and columns_to_clean:

        if cleaning_method == "Drop rows":
            df_cleaned = df_cleaned.dropna(subset=columns_to_clean)

        elif cleaning_method in ["Fill with mean", "Fill with median"]:
            numeric_cols = df_cleaned[columns_to_clean].select_dtypes(include=np.number).columns

            if len(numeric_cols) == 0:
                st.warning("⚠ No numeric columns selected for this method.")
            else:
                if cleaning_method == "Fill with mean":
                    df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(
                        df_cleaned[numeric_cols].mean()
                    )
                else:
                    df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(
                        df_cleaned[numeric_cols].median()
                    )

        elif cleaning_method == "Fill with mode":
            for col in columns_to_clean:
                if not df_cleaned[col].mode().empty:
                    df_cleaned[col] = df_cleaned[col].fillna(
                        df_cleaned[col].mode()[0]
                    )

    st.subheader("✅ Cleaned Data Preview")

    col1, col2 = st.columns(2)
    col1.metric("Rows Before", df.shape[0])
    col2.metric("Rows After", df_cleaned.shape[0])

    st.dataframe(df_cleaned.head(), use_container_width=True)

    st.subheader("⬇ Download Cleaned Dataset")

    col1, col2 = st.columns(2)

    # CSV download
    with col1:
        csv_data = df_cleaned.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download as CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    # Excel download
    with col2:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name="Cleaned Data")

        st.download_button(
            label="⬇ Download as Excel",
            data=excel_buffer.getvalue(),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
