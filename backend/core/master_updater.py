"""
Master BOM update functionality based on activation status
"""
import pandas as pd
from typing import Tuple, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MasterBOMUpdater:
    """Handles Master BOM updates based on activation status"""
    
    @staticmethod
    def process_updates(
        master_df: pd.DataFrame,
        target_df: pd.DataFrame,
        lookup_column: str,
        key_column: str = "YAZAKI PN"
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process Master BOM updates based on activation status
        
        Logic:
        - X: No update (skip)
        - D: Update existing record in Master BOM
        - 0: Check for duplicates, insert if not duplicate
        - NOT_FOUND: Insert as new record
        
        Returns: (updated_master_df, update_stats)
        """
        
        stats = {
            "updated_count": 0,
            "inserted_count": 0,
            "duplicates_count": 0,
            "skipped_count": 0,
            "duplicates": []
        }
        
        # Work with copies
        updated_master = master_df.copy()
        processed_target = target_df.copy()
        
        # Ensure ACTIVATION_STATUS column exists
        if 'ACTIVATION_STATUS' not in processed_target.columns:
            raise ValueError("Target data must have ACTIVATION_STATUS column")
        
        # Process each status type
        for status in ['X', 'D', '0', 'NOT_FOUND']:
            status_records = processed_target[processed_target['ACTIVATION_STATUS'] == status]
            
            if len(status_records) == 0:
                continue
                
            logger.info(f"Processing {len(status_records)} records with status '{status}'")
            
            if status == 'X':
                # Skip - no update needed
                stats["skipped_count"] += len(status_records)
                
            elif status == 'D':
                # Update existing records in Master BOM
                updated_count = MasterBOMUpdater._update_existing_records(
                    updated_master, status_records, lookup_column, key_column
                )
                stats["updated_count"] += updated_count
                
            elif status == '0':
                # Check for duplicates, insert if not duplicate
                duplicates, inserted_count = MasterBOMUpdater._handle_zero_status(
                    updated_master, status_records, key_column
                )
                stats["duplicates"].extend(duplicates)
                stats["duplicates_count"] += len(duplicates)
                stats["inserted_count"] += inserted_count
                
            elif status == 'NOT_FOUND':
                # Insert as new records
                inserted_count = MasterBOMUpdater._insert_new_records(
                    updated_master, status_records, key_column
                )
                stats["inserted_count"] += inserted_count
        
        logger.info(f"Master BOM update completed: {stats}")
        return updated_master, stats
    
    @staticmethod
    def _update_existing_records(
        master_df: pd.DataFrame,
        records_to_update: pd.DataFrame,
        lookup_column: str,
        key_column: str
    ) -> int:
        """Update existing records in Master BOM where status is 'D'"""
        updated_count = 0
        
        for _, record in records_to_update.iterrows():
            yazaki_pn = record[key_column]
            
            # Find matching record in master
            mask = master_df[key_column] == yazaki_pn
            matching_indices = master_df[mask].index
            
            if len(matching_indices) > 0:
                # Update the lookup column value
                master_df.loc[matching_indices[0], lookup_column] = 'D'
                updated_count += 1
                logger.debug(f"Updated {yazaki_pn} with status 'D'")
        
        return updated_count
    
    @staticmethod
    def _handle_zero_status(
        master_df: pd.DataFrame,
        records_to_check: pd.DataFrame,
        key_column: str
    ) -> Tuple[List[Dict], int]:
        """Handle records with status '0' - check for duplicates"""
        duplicates = []
        inserted_count = 0
        
        for _, record in records_to_check.iterrows():
            yazaki_pn = record[key_column]
            
            # Check if already exists in master
            existing_records = master_df[master_df[key_column] == yazaki_pn]
            
            if len(existing_records) > 0:
                # Found duplicate - add to duplicates list
                duplicate_info = {
                    "YAZAKI_PN": yazaki_pn,
                    "Source": "Target Sheet",
                    "Existing_In_Master": True,
                    "Master_Record": existing_records.iloc[0].to_dict(),
                    "Target_Record": record.to_dict()
                }
                duplicates.append(duplicate_info)
            else:
                # No duplicate found - insert as new record
                new_record = MasterBOMUpdater._prepare_new_record(record, master_df)
                master_df.loc[len(master_df)] = new_record
                inserted_count += 1
                logger.debug(f"Inserted new record for {yazaki_pn}")
        
        return duplicates, inserted_count
    
    @staticmethod
    def _insert_new_records(
        master_df: pd.DataFrame,
        records_to_insert: pd.DataFrame,
        key_column: str
    ) -> int:
        """Insert new records for NOT_FOUND status"""
        inserted_count = 0
        
        for _, record in records_to_insert.iterrows():
            new_record = MasterBOMUpdater._prepare_new_record(record, master_df)
            master_df.loc[len(master_df)] = new_record
            inserted_count += 1
            logger.debug(f"Inserted NOT_FOUND record for {record[key_column]}")
        
        return inserted_count
    
    @staticmethod
    def _prepare_new_record(source_record: pd.Series, master_df: pd.DataFrame) -> pd.Series:
        """Prepare a new record for insertion into Master BOM"""
        # Create a new record with the same structure as master
        new_record = pd.Series(index=master_df.columns, dtype=object)
        
        # Fill with default values
        new_record = new_record.fillna('')
        
        # Copy available data from source record
        for col in source_record.index:
            if col in new_record.index and col != 'ACTIVATION_STATUS':
                new_record[col] = source_record[col]
        
        return new_record


# Global updater instance
master_updater = MasterBOMUpdater()
