[2025-07-21 21:59:43] 2. Create, Organize, and Update Files: Follow the project structure and ensure all necessary files and folders are created with appropriate content. Create new source files, modify existing source files, update configuration files, and add documentation files as needed. Regularly update key files, including project_plan.md and test_plan.md, to reflect progress, changes, and future improvements.

# FLL-Sim Backup Manager Guide

This guide describes how to use the Backup Manager GUI to view backup history, restore backups, and manage backup schedules.

## Features
- View backup history
- Restore backups to project root
- Refresh backup list
- Error handling and user feedback

## How to Use
1. Open the Backup Manager tab in the FLL-Sim GUI.
2. Select a backup from the list and click "Restore Selected Backup".
3. Use "Refresh Backup List" to update the backup history.

## Developer Notes
- Backup operations are logged using `src/fll_sim/utils/logger.py`.
- Restore errors are reported to the user and logged.
- See `src/fll_sim/utils/backup_utils.py` for implementation details.




