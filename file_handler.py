import pandas as pd
import streamlit as st

def load_file(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return {"Sheet1": pd.read_csv(uploaded_file)}
    xl = pd.ExcelFile(uploaded_file)
    return {name: xl.parse(name) for name in xl.sheet_names}

def get_sheet_names(sheets):
    return list(sheets.keys())

def preview_sheets(sheets, names):
    for name in names:
        st.write(f"**{name}**")
        st.dataframe(sheets[name].head(5))