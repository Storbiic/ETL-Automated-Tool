"""
Enhanced preprocessing functionality with better column suggestion and lookup
"""
import pandas as pd
from difflib import SequenceMatcher
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data preprocessing and lookup operations"""
    
    @staticmethod
    def suggest_column(input_name: str, columns: list) -> Tuple[str, float]:
        """
        Suggest best matching column with confidence score
        Returns: (suggested_column, confidence_score)
        """
        if not input_name.strip():
            return columns[0] if columns else "", 0.0
        
        # Extract prefix and suffix from input (e.g., J74_V710_B2_PP_YOTK -> J74_V710_B2, YOTK)
        parts = input_name.split('_')
        if len(parts) >= 4:
            prefix = '_'.join(parts[:3])  # First 3 parts
            suffix = parts[-1]  # Last part
            
            best, best_score = input_name, 0
            for col in columns:
                # Check if column starts with prefix and ends with suffix
                if col.upper().startswith(prefix.upper()) and col.upper().endswith(suffix.upper()):
                    score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
                    if score >= 0.9 and score > best_score:  # 90% threshold
                        best, best_score = col, score
            
            if best_score > 0:
                return best, best_score
        
        # Fallback to similarity matching
        best, best_score = input_name, 0
        for col in columns:
            score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
            if score > best_score:
                best, best_score = col, score
        
        return best, best_score
    
    @staticmethod
    def add_activation_status(
        master_df: pd.DataFrame, 
        target_df: pd.DataFrame, 
        key_col: str, 
        lookup_col: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Add activation status with detailed statistics
        Returns: (result_dataframe, lookup_stats)
        """
        # Remove duplicates from master
        master_clean = master_df.drop_duplicates(subset=[key_col], keep='first')
        
        # Prepare lookup dictionary
        lookup_series = master_clean[lookup_col]
        lookup_dict = pd.Series(lookup_series.values, index=master_clean[key_col]).to_dict()
        
        stats = {
            "master_records": len(master_df),
            "master_unique_records": len(master_clean),
            "target_records": len(target_df),
            "lookup_dict_size": len(lookup_dict),
            "mapping_results": {}
        }
        
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
        
        # Calculate mapping statistics
        status_counts = df['ACTIVATION_STATUS'].value_counts().to_dict()
        stats["mapping_results"] = status_counts
        stats["total_processed"] = len(df)
        
        # Calculate percentages
        total = len(df)
        stats["mapping_percentages"] = {
            status: round((count / total) * 100, 2) 
            for status, count in status_counts.items()
        }
        
        logger.info(f"Lookup completed: {stats}")
        
        return df, stats
    
    @staticmethod
    def get_column_suggestions(master_df: pd.DataFrame, start_col: int = 1, end_col: int = 22) -> list:
        """Get permissible columns for lookup from master dataframe"""
        columns = list(master_df.columns)
        # Return columns within the specified range, ensuring we don't go out of bounds
        end_idx = min(end_col, len(columns))
        return columns[start_col:end_idx]


# Global processor instance
data_processor = DataProcessor()
