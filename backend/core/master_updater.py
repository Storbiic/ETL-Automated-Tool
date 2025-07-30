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
            "duplicates": [],
            "updated_records": [],
            "inserted_records": []
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
                updated_count, updated_records = MasterBOMUpdater._update_existing_records(
                    updated_master, status_records, lookup_column, key_column
                )
                stats["updated_count"] += updated_count
                stats["updated_records"].extend(updated_records)
                
            elif status == '0':
                # Check for duplicates, insert if not duplicate
                duplicates, inserted_count, inserted_records = MasterBOMUpdater._handle_zero_status(
                    updated_master, status_records, key_column, lookup_column
                )
                stats["duplicates"].extend(duplicates)
                stats["duplicates_count"] += len(duplicates)
                stats["inserted_count"] += inserted_count
                stats["inserted_records"].extend(inserted_records)
                
            elif status == 'NOT_FOUND':
                # Insert as new records with filtered column set to 'X'
                inserted_count, inserted_records = MasterBOMUpdater._insert_new_records(
                    updated_master, status_records, key_column, lookup_column
                )
                stats["inserted_count"] += inserted_count
                stats["inserted_records"].extend(inserted_records)
        
        logger.info(f"Master BOM update completed: {stats}")
        return updated_master, stats
    
    @staticmethod
    def _update_existing_records(
        master_df: pd.DataFrame,
        records_to_update: pd.DataFrame,
        lookup_column: str,
        key_column: str
    ) -> Tuple[int, List[Dict]]:
        """Update existing records in Master BOM where status is 'D', then change D to X"""
        updated_count = 0
        updated_records = []

        for _, record in records_to_update.iterrows():
            yazaki_pn = record[key_column]

            # Find matching record in master
            mask = master_df[key_column] == yazaki_pn
            matching_indices = master_df[mask].index

            if len(matching_indices) > 0:
                # Store record before update for preview
                before_record = master_df.loc[matching_indices[0]].to_dict()

                # First update the lookup column value to 'D'
                master_df.loc[matching_indices[0], lookup_column] = 'D'
                # Then immediately change 'D' to 'X' as requested
                master_df.loc[matching_indices[0], lookup_column] = 'X'

                # Store record after update for preview
                after_record = master_df.loc[matching_indices[0]].to_dict()

                updated_records.append({
                    "YAZAKI_PN": yazaki_pn,
                    "Action": "Updated D → X",
                    "Column": lookup_column,
                    "Before": before_record.get(lookup_column, ''),
                    "After": after_record.get(lookup_column, ''),
                    "Record": after_record
                })

                updated_count += 1
                logger.debug(f"Updated {yazaki_pn}: D -> X in column {lookup_column}")

        return updated_count, updated_records
    
    @staticmethod
    def _handle_zero_status(
        master_df: pd.DataFrame,
        records_to_check: pd.DataFrame,
        key_column: str,
        lookup_column: str
    ) -> Tuple[List[Dict], int, List[Dict]]:
        """Handle records with status '0' - check for duplicates"""
        duplicates = []
        inserted_count = 0
        inserted_records = []

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
                # No duplicate found - insert as new record with filtered column set to 'X'
                new_record = MasterBOMUpdater._prepare_new_record(record, master_df, lookup_column)
                master_df.loc[len(master_df)] = new_record

                # Store for preview
                inserted_records.append({
                    "YAZAKI_PN": yazaki_pn,
                    "Action": "Inserted (Status 0)",
                    "Column": lookup_column,
                    "Value": "X",
                    "Record": new_record.to_dict()
                })

                inserted_count += 1
                logger.debug(f"Inserted new record for {yazaki_pn} with filtered column '{lookup_column}' set to 'X'")

        return duplicates, inserted_count, inserted_records
    
    @staticmethod
    def _insert_new_records(
        master_df: pd.DataFrame,
        records_to_insert: pd.DataFrame,
        key_column: str,
        lookup_column: str
    ) -> Tuple[int, List[Dict]]:
        """Insert new records for NOT_FOUND status with filtered column set to 'X'"""
        inserted_count = 0
        inserted_records = []

        for _, record in records_to_insert.iterrows():
            yazaki_pn = record[key_column]
            new_record = MasterBOMUpdater._prepare_new_record(record, master_df, lookup_column)
            master_df.loc[len(master_df)] = new_record

            # Store for preview
            inserted_records.append({
                "YAZAKI_PN": yazaki_pn,
                "Action": "Inserted (NOT_FOUND)",
                "Column": lookup_column,
                "Value": "X",
                "Record": new_record.to_dict()
            })

            inserted_count += 1
            logger.debug(f"Inserted NOT_FOUND record for {yazaki_pn} with filtered column '{lookup_column}' set to 'X'")

        return inserted_count, inserted_records
    
    @staticmethod
    def _prepare_new_record(source_record: pd.Series, master_df: pd.DataFrame, lookup_column: str = None) -> pd.Series:
        """Prepare a new record for insertion into Master BOM"""
        # Create a new record with the same structure as master
        new_record = pd.Series(index=master_df.columns, dtype=object)

        # Fill with default values
        new_record = new_record.fillna('')

        # Copy available data from source record
        for col in source_record.index:
            if col in new_record.index and col != 'ACTIVATION_STATUS':
                new_record[col] = source_record[col]

        # Set the filtered column (lookup column) to 'X' for new records
        if lookup_column and lookup_column in new_record.index:
            new_record[lookup_column] = 'X'
            logger.debug(f"Set {lookup_column} = 'X' for new record")

        return new_record


# Global updater instance
master_updater = MasterBOMUpdater()
