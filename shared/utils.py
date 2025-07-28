import pandas as pd
import numpy as np
from typing import Dict, Any

def detect_file_type(filename: str) -> str:
    """Detect file type based on extension"""
    if filename.endswith('.csv'):
        return 'csv'
    elif filename.endswith('.xlsx'):
        return 'xlsx'
    elif filename.endswith('.xls'):
        return 'xls'
    else:
        raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS files.")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard ETL operations to clean the dataframe"""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Remove completely empty rows and columns
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    
    # Remove duplicate rows
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # Handle missing values by column type
    for col in df.columns:
        if df[col].dtype == 'object':
            # For string/object columns, fill with 'Unknown' or most frequent value
            mode_val = df[col].mode()
            fill_val = mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown'
            df[col] = df[col].fillna(fill_val)
        elif df[col].dtype in ['int64', 'float64']:
            # For numeric columns, fill with median
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
        elif 'datetime' in str(df[col].dtype):
            # For datetime columns, fill with mode or forward fill
            mode_date = df[col].mode()
            if len(mode_date) > 0:
                df[col] = df[col].fillna(mode_date.iloc[0])
            else:
                df[col] = df[col].fillna(method='ffill')
    
    # Data type coercion and normalization
    for col in df.columns:
        if df[col].dtype == 'object':
            # Clean string columns
            df[col] = df[col].astype(str).str.strip()
            
            # Try to convert string columns to numeric if they look numeric
            if _is_numeric_string(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Fill any NaN values created during conversion
                    if df[col].isna().any():
                        df[col] = df[col].fillna(df[col].median())
                    continue
                except:
                    pass
            
            # Try to convert to datetime if it looks like dates
            if _is_datetime_string(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    # Fill any NaT values created during conversion
                    if df[col].isna().any():
                        mode_date = df[col].mode()
                        if len(mode_date) > 0:
                            df[col] = df[col].fillna(mode_date.iloc[0])
                    continue
                except:
                    pass
            
            # Standardize text case for categorical data
            if len(df[col].unique()) < len(df) * 0.5:  # If less than 50% unique values, treat as categorical
                df[col] = df[col].str.title()  # Convert to title case
    
    # Remove any remaining rows with all NaN values (shouldn't happen, but safety check)
    df = df.dropna(how='all')
    
    return df

def _is_numeric_string(series: pd.Series) -> bool:
    """Check if a string series could be converted to numeric"""
    try:
        # Sample a few values to check
        sample_size = min(100, len(series))
        sample = series.dropna().head(sample_size)
        
        numeric_count = 0
        for val in sample:
            try:
                float(str(val))
                numeric_count += 1
            except (ValueError, TypeError):
                pass
        
        # If more than 80% of sampled values are numeric, consider it numeric
        return numeric_count / len(sample) > 0.8 if len(sample) > 0 else False
    except:
        return False

def _is_datetime_string(series: pd.Series) -> bool:
    """Check if a string series could be converted to datetime"""
    try:
        # Sample a few values to check
        sample_size = min(50, len(series))
        sample = series.dropna().head(sample_size)
        
        datetime_count = 0
        for val in sample:
            try:
                pd.to_datetime(str(val))
                datetime_count += 1
            except (ValueError, TypeError):
                pass
        
        # If more than 70% of sampled values are datetime, consider it datetime
        return datetime_count / len(sample) > 0.7 if len(sample) > 0 else False
    except:
        return False

def generate_column_filters(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Generate filter options for each column based on data type"""
    filters = {}
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        unique_values = df[col].dropna().unique()
        
        if col_type == 'object':
            # Categorical filter - limit to reasonable number of options
            unique_list = [str(val) for val in unique_values if pd.notna(val)]
            unique_list = sorted(unique_list)[:100]  # Limit to 100 unique values
            
            filters[col] = {
                'type': 'categorical',
                'options': unique_list
            }
        elif col_type in ['int64', 'float64']:
            # Numeric range filter
            min_val = float(df[col].min()) if pd.notna(df[col].min()) else 0
            max_val = float(df[col].max()) if pd.notna(df[col].max()) else 100
            
            filters[col] = {
                'type': 'numeric',
                'min': min_val,
                'max': max_val
            }
        elif 'datetime' in col_type:
            # Date range filter
            min_date = df[col].min()
            max_date = df[col].max()
            
            filters[col] = {
                'type': 'date',
                'min': min_date.isoformat() if pd.notna(min_date) else None,
                'max': max_date.isoformat() if pd.notna(max_date) else None
            }
        else:
            # Default to categorical for unknown types
            unique_list = [str(val) for val in unique_values if pd.notna(val)]
            unique_list = sorted(unique_list)[:100]
            
            filters[col] = {
                'type': 'categorical',
                'options': unique_list
            }
    
    return filters

def format_dataframe_for_display(df: pd.DataFrame, max_rows: int = 1000) -> pd.DataFrame:
    """Format dataframe for display in frontend"""
    display_df = df.head(max_rows).copy()
    
    # Convert datetime columns to string for JSON serialization
    for col in display_df.columns:
        if 'datetime' in str(display_df[col].dtype):
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif display_df[col].dtype == 'object':
            # Ensure all object columns are strings
            display_df[col] = display_df[col].astype(str)
    
    # Replace NaN values with empty strings for better display
    display_df = display_df.fillna('')
    
    return display_df

def validate_join_keys(left_df: pd.DataFrame, right_df: pd.DataFrame, 
                      left_key: str, right_key: str) -> Dict[str, Any]:
    """Validate join keys and return statistics"""
    result = {
        'valid': True,
        'warnings': [],
        'stats': {}
    }
    
    # Check if keys exist
    if left_key not in left_df.columns:
        result['valid'] = False
        result['warnings'].append(f"Left key '{left_key}' not found in left dataset")
        return result
    
    if right_key not in right_df.columns:
        result['valid'] = False
        result['warnings'].append(f"Right key '{right_key}' not found in right dataset")
        return result
    
    # Get statistics
    left_unique = left_df[left_key].nunique()
    right_unique = right_df[right_key].nunique()
    left_total = len(left_df)
    right_total = len(right_df)
    
    # Find overlapping values
    left_values = set(left_df[left_key].dropna().astype(str))
    right_values = set(right_df[right_key].dropna().astype(str))
    overlap = len(left_values.intersection(right_values))
    
    result['stats'] = {
        'left_unique_values': left_unique,
        'right_unique_values': right_unique,
        'left_total_rows': left_total,
        'right_total_rows': right_total,
        'overlapping_values': overlap,
        'left_key_type': str(left_df[left_key].dtype),
        'right_key_type': str(right_df[right_key].dtype)
    }
    
    # Add warnings for potential issues
    if overlap == 0:
        result['warnings'].append("No overlapping values found between join keys")
    elif overlap < min(left_unique, right_unique) * 0.1:
        result['warnings'].append("Very few overlapping values found - join may result in small dataset")
    
    if left_df[left_key].dtype != right_df[right_key].dtype:
        result['warnings'].append("Join keys have different data types - this may cause issues")
    
    return result