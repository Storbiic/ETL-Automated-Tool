"""
Enhanced data cleaning functionality with better error handling
"""
import pandas as pd
import re
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Handles data cleaning operations"""
    
    @staticmethod
    def clean_master_yazaki(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean master YAZAKI data with detailed logging
        Returns: (cleaned_dataframe, cleaning_stats)
        """
        df = df.copy()
        stats = {
            "original_shape": df.shape,
            "columns_renamed": [],
            "rows_with_null_yazaki_pn": 0,
            "rows_cleaned": 0
        }
        
        # Standardize column name
        yazaki_cols = [col for col in df.columns if col.strip().upper().replace(' ', '_') == 'YAZAKI_PN']
        if yazaki_cols:
            old_name = yazaki_cols[0]
            df.rename(columns={old_name: 'YAZAKI PN'}, inplace=True)
            stats["columns_renamed"].append(f"{old_name} -> YAZAKI PN")
        
        # Clean ONLY YAZAKI PN column
        if 'YAZAKI PN' in df.columns:
            # Count nulls before cleaning
            stats["rows_with_null_yazaki_pn"] = df['YAZAKI PN'].isna().sum()
            
            # Force conversion to string, handling all data types
            original_count = len(df)
            df['YAZAKI PN'] = df['YAZAKI PN'].apply(
                lambda x: str(x) if pd.notna(x) else ''
            ).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
            
            # Remove rows with empty YAZAKI PN after cleaning
            df = df[df['YAZAKI PN'].str.len() > 0]
            stats["rows_cleaned"] = original_count - len(df)
        
        stats["final_shape"] = df.shape
        logger.info(f"Master cleaning completed: {stats}")

        # Fix data types for Arrow compatibility
        df = DataCleaner.fix_arrow_compatibility(df)

        return df, stats
    
    @staticmethod
    def clean_generic_sheet(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean generic sheet with detailed logging
        Returns: (cleaned_dataframe, cleaning_stats)
        """
        df = df.copy()
        stats = {
            "original_shape": df.shape,
            "columns_standardized": [],
            "columns_swapped": False,
            "string_columns_cleaned": 0
        }
        
        # Store original column names for comparison
        original_columns = list(df.columns)
        
        # Standardize all column names
        df.columns = [col.strip().upper().replace(' ', '_') for col in df.columns]
        stats["columns_standardized"] = list(zip(original_columns, df.columns))
        
        # Swap first two columns if we have at least 2
        cols = list(df.columns)
        if len(cols) >= 2:
            cols[0], cols[1] = cols[1], cols[0]
            df = df[cols]
            stats["columns_swapped"] = True
        
        # Clean string values and ensure consistent types
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].apply(
                lambda x: str(x) if pd.notna(x) else ''
            ).apply(
                lambda x: re.sub(r"['\"+ ]+", "", x).strip()
            )
            stats["string_columns_cleaned"] += 1
        
        stats["final_shape"] = df.shape
        logger.info(f"Generic cleaning completed: {stats}")

        # Fix data types for Arrow compatibility
        df = DataCleaner.fix_arrow_compatibility(df)

        return df, stats
    
    @staticmethod
    def prepare_target_sheet(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare target sheet by ensuring YAZAKI PN is first column"""
        df = df.copy()
        cols = list(df.columns)
        
        # Rename YAZAKI_PN to YAZAKI PN if needed
        if "YAZAKI_PN" in cols:
            df.rename(columns={"YAZAKI_PN": "YAZAKI PN"}, inplace=True)
            cols = list(df.columns)
        
        # Move YAZAKI PN to first position
        if "YAZAKI PN" in cols:
            cols.insert(0, cols.pop(cols.index("YAZAKI PN")))
            df = df[cols]
        
        return df

    @staticmethod
    def fix_arrow_compatibility(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix DataFrame data types to prevent PyArrow serialization errors in Streamlit
        """
        df = df.copy()

        for col in df.columns:
            # Convert all object columns to string to avoid mixed type issues
            if df[col].dtype == 'object':
                # Handle mixed types by converting everything to string
                df[col] = df[col].astype(str)
                # Replace 'nan' strings with empty strings for cleaner display
                df[col] = df[col].replace(['nan', 'None', 'NaN'], '')

            # Handle numeric columns that might have mixed types
            elif df[col].dtype in ['int64', 'float64']:
                # Ensure numeric columns are properly typed
                try:
                    # Try to convert to numeric, coercing errors to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Fill NaN with 0 for display purposes
                    df[col] = df[col].fillna(0)
                except:
                    # If conversion fails, convert to string
                    df[col] = df[col].astype(str)

        logger.info("DataFrame types fixed for Arrow compatibility")
        return df


# Global cleaner instance
data_cleaner = DataCleaner()
