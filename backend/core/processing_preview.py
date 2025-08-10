"""
Processing Preview Module for ETL Automation Tool
Provides preview of changes before applying them to Master BOM
"""
import pandas as pd
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ProcessingPreview:
    """Generate preview of processing changes before applying them"""
    
    @staticmethod
    def generate_preview(
        master_df: pd.DataFrame,
        target_df: pd.DataFrame,
        lookup_column: str,
        key_column: str
    ) -> Dict[str, Any]:
        """Generate comprehensive preview of all changes that will be made"""
        
        try:
            # Create copies to avoid modifying originals
            master_copy = master_df.copy()
            target_copy = target_df.copy()
            
            # Perform lookup to get activation statuses
            from .preprocessing import DataProcessor
            processor = DataProcessor()
            
            lookup_result = processor.perform_lookup(master_copy, target_copy, lookup_column, key_column)
            
            # Analyze what changes will be made
            preview_data = {
                "changes_summary": {},
                "updated_records_preview": [],
                "inserted_records_preview": [],
                "duplicates_preview": [],
                "statistics": {
                    "total_target_records": len(target_copy),
                    "records_to_update": 0,
                    "records_to_insert": 0,
                    "duplicates_found": 0,
                    "records_to_skip": 0
                }
            }
            
            # Group records by activation status
            status_groups = lookup_result.groupby('ACTIVATION_STATUS')
            
            for status, group in status_groups:
                if status == 'D':
                    # Records that will be updated (D → X)
                    preview_data["statistics"]["records_to_update"] = len(group)
                    preview_data["updated_records_preview"] = ProcessingPreview._preview_updates(
                        master_copy, group, lookup_column, key_column
                    )
                
                elif status == '0':
                    # Records that need duplicate checking
                    duplicates, new_records = ProcessingPreview._preview_zero_status(
                        master_copy, group, key_column
                    )
                    preview_data["duplicates_preview"] = duplicates
                    preview_data["statistics"]["duplicates_found"] = len(duplicates)
                    preview_data["statistics"]["records_to_insert"] += len(new_records)
                    preview_data["inserted_records_preview"].extend(new_records)
                
                elif status == 'NOT_FOUND':
                    # Records that will be inserted as new
                    new_records = ProcessingPreview._preview_new_records(group, lookup_column)
                    preview_data["inserted_records_preview"].extend(new_records)
                    preview_data["statistics"]["records_to_insert"] += len(new_records)
                
                elif status == 'X':
                    # Records that will be skipped
                    preview_data["statistics"]["records_to_skip"] = len(group)
            
            # Generate summary
            preview_data["changes_summary"] = {
                "total_changes": (
                    preview_data["statistics"]["records_to_update"] + 
                    preview_data["statistics"]["records_to_insert"]
                ),
                "backup_recommended": True,
                "estimated_processing_time": "< 1 minute",
                "risk_level": ProcessingPreview._assess_risk_level(preview_data["statistics"])
            }
            
            logger.info(f"Preview generated: {preview_data['statistics']}")
            return preview_data
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            raise
    
    @staticmethod
    def _preview_updates(
        master_df: pd.DataFrame, 
        records_to_update: pd.DataFrame, 
        lookup_column: str, 
        key_column: str
    ) -> List[Dict[str, Any]]:
        """Preview records that will be updated (D → X)"""
        
        updates_preview = []
        
        for _, record in records_to_update.iterrows():
            yazaki_pn = record[key_column]
            
            # Find matching record in master
            master_match = master_df[master_df[key_column] == yazaki_pn]
            
            if len(master_match) > 0:
                current_value = master_match.iloc[0][lookup_column] if lookup_column in master_match.columns else 'N/A'
                
                updates_preview.append({
                    "YAZAKI_PN": yazaki_pn,
                    "Action": "Update D → X",
                    "Current_Value": current_value,
                    "New_Value": "X",
                    "Column": lookup_column,
                    "Record_Data": record.to_dict()
                })
        
        return updates_preview[:10]  # Limit to first 10 for preview
    
    @staticmethod
    def _preview_zero_status(
        master_df: pd.DataFrame, 
        records_to_check: pd.DataFrame, 
        key_column: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Preview records with status '0' - identify duplicates and new records"""
        
        duplicates = []
        new_records = []
        
        for _, record in records_to_check.iterrows():
            yazaki_pn = record[key_column]
            
            # Check if already exists in master
            existing_records = master_df[master_df[key_column] == yazaki_pn]
            
            if len(existing_records) > 0:
                # Found duplicate
                duplicates.append({
                    "YAZAKI_PN": yazaki_pn,
                    "Action": "Duplicate Found",
                    "Source": "Target Sheet",
                    "Existing_In_Master": True,
                    "Master_Record": existing_records.iloc[0].to_dict(),
                    "Target_Record": record.to_dict()
                })
            else:
                # Will be inserted as new
                new_records.append({
                    "YAZAKI_PN": yazaki_pn,
                    "Action": "Insert New (Status 0)",
                    "Filtered_Column_Value": "X",
                    "Record_Data": record.to_dict()
                })
        
        return duplicates[:10], new_records[:10]  # Limit for preview
    
    @staticmethod
    def _preview_new_records(records_to_insert: pd.DataFrame, lookup_column: str) -> List[Dict[str, Any]]:
        """Preview records that will be inserted as new (NOT_FOUND status)"""
        
        new_records = []
        
        for _, record in records_to_insert.iterrows():
            new_records.append({
                "YAZAKI_PN": record.get('YAZAKI PN', 'N/A'),
                "Action": "Insert New (NOT_FOUND)",
                "Filtered_Column_Value": "X",
                "Column": lookup_column,
                "Record_Data": record.to_dict()
            })
        
        return new_records[:10]  # Limit for preview
    
    @staticmethod
    def _assess_risk_level(statistics: Dict[str, int]) -> str:
        """Assess the risk level of the processing operation"""
        
        total_changes = statistics["records_to_update"] + statistics["records_to_insert"]
        
        if total_changes == 0:
            return "NONE"
        elif total_changes <= 10:
            return "LOW"
        elif total_changes <= 100:
            return "MEDIUM"
        else:
            return "HIGH"
    
    @staticmethod
    def generate_change_report(preview_data: Dict[str, Any]) -> str:
        """Generate a human-readable change report"""
        
        stats = preview_data["statistics"]
        summary = preview_data["changes_summary"]
        
        report = f"""
📊 PROCESSING PREVIEW REPORT
{'=' * 50}

📈 STATISTICS:
• Total Target Records: {stats['total_target_records']}
• Records to Update (D→X): {stats['records_to_update']}
• Records to Insert: {stats['records_to_insert']}
• Duplicates Found: {stats['duplicates_found']}
• Records to Skip (X): {stats['records_to_skip']}

🔄 CHANGES SUMMARY:
• Total Changes: {summary['total_changes']}
• Risk Level: {summary['risk_level']}
• Backup Recommended: {'Yes' if summary['backup_recommended'] else 'No'}
• Estimated Time: {summary['estimated_processing_time']}

⚠️ IMPORTANT NOTES:
• A backup will be created automatically before processing
• All changes can be rolled back if needed
• Duplicates will be reported but not processed
• Status 'X' records will be skipped (no changes)

🛡️ SAFETY MEASURES:
• Automatic backup creation before processing
• Detailed change tracking and logging
• Rollback capability to previous versions
• Preview confirmation required before execution
        """
        
        return report.strip()
