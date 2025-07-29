from difflib import SequenceMatcher
import pandas as pd
import streamlit as st

def suggest_column(input_name: str, columns: list) -> str:
    if not input_name.strip():
        return columns[0] if columns else ""
    
    # Extract prefix and suffix from input (e.g., J74_V710_B2_PP_YOTK -> J74_V710_B2, YOTK)
    parts = input_name.split('_')
    if len(parts) >= 4:
        prefix = '_'.join(parts[:3])  # First 3 parts
        suffix = parts[-1]  # Last part
    else:
        # Fallback to original logic if format doesn't match
        best, best_score = input_name, 0
        for col in columns:
            score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
            if score > best_score:
                best, best_score = col, score
        return best
    
    best, best_score = input_name, 0
    for col in columns:
        # Check if column starts with prefix and ends with suffix
        if col.upper().startswith(prefix.upper()) and col.upper().endswith(suffix.upper()):
            score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
            if score >= 0.9 and score > best_score:  # 90% threshold
                best, best_score = col, score
    
    return best


def add_activation_status(master_df: pd.DataFrame, target_df: pd.DataFrame, key_col: str, lookup_col: str) -> pd.DataFrame:
    import streamlit as st

    # Remove duplicates from master
    master_clean = master_df.drop_duplicates(subset=[key_col], keep='first')

    # Prepare lookup dictionary with nulls as "0" if needed
    lookup_series = master_clean[lookup_col]
    lookup_dict = pd.Series(lookup_series.values, index=master_clean[key_col]).to_dict()

    st.write(f"**Lookup Info:** {len(lookup_dict)} unique master records available for lookup")

    df = target_df.copy()

    def get_status(key):
        if pd.isna(key):
            return "MISSING_KEY"  # Key is missing/null in target
        elif key in lookup_dict:
            val = lookup_dict[key]
            return val if pd.notna(val) else "0"  # Found key, but value is null
        else:
            return "NOT_FOUND"  # Key not found in master

    # Apply custom mapping logic
    df.insert(1, 'ACTIVATION_STATUS', df[key_col].apply(get_status))

    # Show mapping results
    st.write(f"**Mapping Summary:**")
    st.write(df['ACTIVATION_STATUS'].value_counts())

    return df


