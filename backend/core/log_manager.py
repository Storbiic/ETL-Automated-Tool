"""
Log Manager for ETL Automation Tool
Handles log collection, formatting, and export functionality
"""
import logging
import io
import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

class LogManager:
    """Manages application logs and provides export functionality"""
    
    def __init__(self):
        self.session_logs = []
        self.detailed_logs = []
        
    def add_session_log(self, message: str, level: str = "INFO"):
        """Add a session log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.session_logs.append(log_entry)
        
    def add_detailed_log(self, operation: str, details: Dict[str, Any]):
        """Add detailed operation log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        self.detailed_logs.append(log_entry)
        
    def get_session_logs(self) -> List[Dict[str, Any]]:
        """Get all session logs"""
        return self.session_logs
        
    def get_detailed_logs(self) -> List[Dict[str, Any]]:
        """Get all detailed logs"""
        return self.detailed_logs
        
    def export_logs_as_text(self) -> str:
        """Export logs as formatted text"""
        output = []
        output.append("=" * 80)
        output.append("ETL AUTOMATION TOOL v2.0 - SESSION LOG EXPORT")
        output.append("=" * 80)
        output.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Total Session Logs: {len(self.session_logs)}")
        output.append(f"Total Detailed Logs: {len(self.detailed_logs)}")
        output.append("")
        
        # Session logs
        output.append("SESSION LOGS:")
        output.append("-" * 40)
        for log in self.session_logs:
            timestamp = log["timestamp"][:19].replace("T", " ")
            output.append(f"[{timestamp}] {log['level']}: {log['message']}")
        
        output.append("")
        
        # Detailed logs
        output.append("DETAILED OPERATION LOGS:")
        output.append("-" * 40)
        for log in self.detailed_logs:
            timestamp = log["timestamp"][:19].replace("T", " ")
            output.append(f"[{timestamp}] {log['operation']}:")
            for key, value in log["details"].items():
                output.append(f"  {key}: {value}")
            output.append("")
        
        return "\n".join(output)
        
    def export_logs_as_json(self) -> str:
        """Export logs as JSON"""
        export_data = {
            "export_info": {
                "tool": "ETL Automation Tool v2.0",
                "export_date": datetime.now().isoformat(),
                "total_session_logs": len(self.session_logs),
                "total_detailed_logs": len(self.detailed_logs)
            },
            "session_logs": self.session_logs,
            "detailed_logs": self.detailed_logs
        }
        return json.dumps(export_data, indent=2)
        
    def export_logs_as_csv(self) -> str:
        """Export logs as CSV"""
        # Combine all logs into a single DataFrame
        all_logs = []
        
        # Add session logs
        for log in self.session_logs:
            all_logs.append({
                "timestamp": log["timestamp"],
                "type": "SESSION",
                "level": log["level"],
                "operation": "SESSION_LOG",
                "message": log["message"],
                "details": ""
            })
        
        # Add detailed logs
        for log in self.detailed_logs:
            details_str = "; ".join([f"{k}={v}" for k, v in log["details"].items()])
            all_logs.append({
                "timestamp": log["timestamp"],
                "type": "DETAILED",
                "level": "INFO",
                "operation": log["operation"],
                "message": "",
                "details": details_str
            })
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(all_logs)
        df = df.sort_values("timestamp")
        
        # Export to CSV string
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
        
    def clear_logs(self):
        """Clear all logs"""
        self.session_logs.clear()
        self.detailed_logs.clear()
        
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of current logs"""
        return {
            "session_logs_count": len(self.session_logs),
            "detailed_logs_count": len(self.detailed_logs),
            "latest_session_log": self.session_logs[-1] if self.session_logs else None,
            "latest_detailed_log": self.detailed_logs[-1] if self.detailed_logs else None
        }

# Global log manager instance
log_manager = LogManager()

# Custom log handler to capture logs
class ETLLogHandler(logging.Handler):
    """Custom log handler to capture logs for export"""
    
    def emit(self, record):
        try:
            message = self.format(record)
            level = record.levelname
            log_manager.add_session_log(message, level)
        except Exception:
            pass  # Ignore errors in log handler

# Set up the custom log handler
def setup_log_capture():
    """Set up log capture for export functionality"""
    handler = ETLLogHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
