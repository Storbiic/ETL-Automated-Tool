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
        
        return df, stats
    
    @staticmethod
    def clean_master_with_insights(
        master_df: pd.DataFrame,
        target_df: pd.DataFrame,
        target_column: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean master BOM with insights and X→D updates for YAZAKI PNs not found in target
        """
        df = master_df.copy()

        # First perform standard master cleaning
        df, basic_stats = DataCleaner.clean_master_yazaki(df)

        # Get target YAZAKI PNs for comparison
        target_yazaki_pns = set()
        if 'YAZAKI PN' in target_df.columns:
            target_yazaki_pns = set(target_df['YAZAKI PN'].dropna().astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True))

        # Analyze target column insights
        insights = {
            "total_records": len(df),
            "status_x_count": 0,
            "status_d_count": 0,
            "status_0_count": 0,
            "x_to_d_updates": 0
        }

        if target_column in df.columns:
            # Count current statuses
            status_counts = df[target_column].value_counts()
            insights["status_x_count"] = status_counts.get('X', 0)
            insights["status_d_count"] = status_counts.get('D', 0)
            insights["status_0_count"] = status_counts.get('0', 0)

            # Update X → D for YAZAKI PNs not found in target sheet
            master_yazaki_pns = set(df['YAZAKI PN'].dropna().astype(str))
            not_found_in_target = master_yazaki_pns - target_yazaki_pns

            # Update X to D for records not found in target
            mask = (df['YAZAKI PN'].isin(not_found_in_target)) & (df[target_column] == 'X')
            df.loc[mask, target_column] = 'D'
            insights["x_to_d_updates"] = mask.sum()

            # Update counts after changes
            status_counts_after = df[target_column].value_counts()
            insights["status_x_count"] = status_counts_after.get('X', 0)
            insights["status_d_count"] = status_counts_after.get('D', 0)
            insights["status_0_count"] = status_counts_after.get('0', 0)

        logger.info(f"Master BOM insights: {insights}")

        return df, insights

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


# Global cleaner instance
data_cleaner = DataCleaner()
