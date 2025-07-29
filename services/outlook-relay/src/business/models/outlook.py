"""
Outlook configuration model for outlook-relay
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta

@dataclass
class OutlookConfiguration:
    """
    Configuration for Outlook email operations
    """
    folder_name: str = "Inbox"
    time_range_hours: int = 24
    sender_filter: Optional[str] = None
    attachment_required: bool = True  # Only fetch emails with attachments
    csv_attachments_only: bool = True  # Only fetch emails with CSV attachments
    
    # Date filtering
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Advanced filtering
    subject_keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    max_emails: int = 100
    
    def get_time_range(self) -> tuple[datetime, datetime]:
        """Get the actual time range for email fetching"""
        if self.start_date and self.end_date:
            return self.start_date, self.end_date
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=self.time_range_hours)
        return start_time, end_time
    
    def should_process_email(self, subject: str, sender: str, has_attachments: bool) -> bool:
        """Business logic for determining if an email should be processed"""
        
        # Check attachment requirement
        if self.attachment_required and not has_attachments:
            return False
            
        # Check sender filter
        if self.sender_filter and self.sender_filter.lower() not in sender.lower():
            return False
            
        # Check subject keywords
        if self.subject_keywords:
            subject_lower = subject.lower()
            if not any(keyword.lower() in subject_lower for keyword in self.subject_keywords):
                return False
                
        # Check exclude keywords
        if self.exclude_keywords:
            subject_lower = subject.lower()
            if any(keyword.lower() in subject_lower for keyword in self.exclude_keywords):
                return False
                
        return True
