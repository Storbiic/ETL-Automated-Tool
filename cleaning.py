import pandas as pd
import re

def clean_master_yazaki(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Standardize column name
    if any(col.strip().upper().replace(' ', '_') == 'YAZAKI_PN' for col in df.columns):
        df.rename(columns={col: 'YAZAKI PN' for col in df.columns if col.strip().upper().replace(' ', '_') == 'YAZAKI_PN'}, inplace=True)
    # Clean ONLY YAZAKI PN column: ensure string type, remove non-alphanumeric
    if 'YAZAKI PN' in df.columns:
        # Force conversion to string, handling all data types
        df['YAZAKI PN'] = df['YAZAKI PN'].apply(lambda x: str(x) if pd.notna(x) else '').str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    return df


def clean_generic_sheet(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Standardize all column names
    df.columns = [col.strip().upper().replace(' ', '_') for col in df.columns]
    # Swap first two cols
    cols = list(df.columns)
    if len(cols) >= 2:
        cols[0], cols[1] = cols[1], cols[0]
        df = df[cols]
    # Clean string values and ensure consistent types
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else '').apply(lambda x: re.sub(r"['\"+ ]+", "", x).strip())
    return df
