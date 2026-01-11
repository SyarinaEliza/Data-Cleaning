import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Data Cleaning App", layout="wide")
st.title("🧹 Data Cleaning App")
st.markdown("Upload a CSV or Excel file to inspect and clean your data")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)

data = None

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "csv":
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

if data is not None:
    st.subheader("📋 Raw Dataset")
    st.dataframe(data.head())

    st.subheader("ℹ️ Dataset Info")
    st.write("Shape:", data.shape)

    # Missing values
    st.subheader("❓ Missing Values")
    missing = data.isnull().sum()
    st.dataframe(missing[missing > 0] if missing.sum() > 0 else "No missing values found")

    # Duplicate rows
    st.subheader("📝 Duplicate Records")
    duplicates = data.duplicated()
    st.write(f"Number of duplicate rows: {duplicates.sum()}")

    st.subheader("🧰 Data Cleaning Operations")

    # Remove duplicates
    if st.button("Remove Duplicate Rows"):
        data = data.drop_duplicates()
        st.success("Duplicate rows removed!")

    # Remove missing values
    if st.button("Remove Missing Values (Drop rows with NaN)"):
        data = data.dropna()
        st.success("Rows with missing values removed!")

    # Handle missing values
    st.markdown("**Fill Missing Values**")
    method = st.selectbox("Choose method to fill missing values", ["None", "Fill with 0", "Fill with Mean", "Fill with Median", "Fill with Mode"])
    if st.button("Handle Missing Values"):
        if method == "Fill with 0":
            data = data.fillna(0)
        elif method == "Fill with Mean":
            for col in data.select_dtypes(include="number").columns:
                data[col].fillna(data[col].mean(), inplace=True)
        elif method == "Fill with Median":
            for col in data.select_dtypes(include="number").columns:
                data[col].fillna(data[col].median(), inplace=True)
        elif method == "Fill with Mode":
            for col in data.columns:
                data[col].fillna(data[col].mode()[0], inplace=True)
        st.success(f"Missing values handled with method: {method}")

    st.subheader("✅ Cleaned Dataset")
    st.dataframe(data.head())
    st.write("Shape after cleaning:", data.shape)

    def convert_df(df):
        """Convert dataframe to bytes for download"""
        output = BytesIO()
        if file_extension == "csv":
            df.to_csv(output, index=False)
        else:
            df.to_excel(output, index=False)
        return output.getvalue()

    st.download_button(
        label="📥 Download Cleaned File",
        data=convert_df(data),
        file_name=f"cleaned_data.{file_extension}",
        mime="text/csv" if file_extension=="csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload a CSV or Excel file to start cleaning your data.")
