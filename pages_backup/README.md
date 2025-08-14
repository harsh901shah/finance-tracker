# Pages Backup Directory

This directory contains deprecated or refactored pages that have been removed from the main navigation.

## Criteria for Moving Pages Here

Pages are moved to this backup directory when they meet one of these criteria:

### ❌ **Deprecated Pages** (Remove from navigation)
- **Functionality consolidated** into other pages
- **Redundant features** that duplicate existing functionality
- **Incomplete implementations** that are not production-ready

### 🔄 **Refactored Pages** (Temporary staging)
- Pages being **redesigned or restructured**
- **Breaking changes** that need testing before deployment
- **Feature experiments** that may be restored later

## Current Backup Status

### **budget_page.py** - ❌ DEPRECATED
- **Reason:** Budget functionality consolidated into Dashboard
- **Status:** Budget tracking available in Dashboard page
- **Action:** Safe to delete after confirming Dashboard budget works

### **settings_page.py** - ❌ DEPRECATED  
- **Reason:** Settings moved to Dashboard user preferences panel
- **Status:** User preferences available in Dashboard
- **Action:** Safe to delete after confirming preferences work

### **document_upload_page.py** - ❌ DEPRECATED
- **Reason:** Incomplete feature, not production-ready
- **Status:** Feature removed from navigation
- **Action:** Complete implementation or delete

### **db_viewer_page.py** - ❌ DEPRECATED
- **Reason:** Development tool, not for end users
- **Status:** Removed for security and UX reasons
- **Action:** Keep for development use only

## Restoration Process

To restore a page from backup:

1. **Move file** from `pages_backup/` to `pages/`
2. **Add import** to `finance_tracker.py`
3. **Add to pages dictionary** in FinanceApp class
4. **Add navigation button** in sidebar
5. **Test functionality** thoroughly
6. **Update this README** with restoration notes

## Cleanup Guidelines

- **Review quarterly** - Check if backup pages are still needed
- **Delete permanently** - Remove pages that won't be restored
- **Document decisions** - Update this README with any changes