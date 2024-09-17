iTunes Backup Explorer

iTunes Backup Explorer is a Python-based GUI tool designed to explore and manage iTunes backups. It provides users with an intuitive interface for searching, categorizing, and inspecting backup data files. It includes support for SQLite databases, plist files, symlink handling, and backup info loading.

Features

Browse iTunes Backup Files: Categorize and explore backup files by type.

Drag & Drop Interface: Easily drag and drop backup folders to explore their contents.

Search Functionality: Search files in the backup by name.

Device Information Display: Automatically extracts and displays device information from Info.plist files.

Database Integration: Load and display backup data stored in Manifest.db SQLite databases.

Backup Handling: Backup files to a selected directory.

Symlink Management: Identify and handle symbolic links in backup directories.

Cross-Platform: Works on Windows, macOS, and Linux.




Requirements

Python 3.6+
Required Libraries:
tkinter
tkinterdnd2
sqlite3
plistlib
shutil
json
threading

Installation

1.Clone or download the repository.

2.Install the required dependencies using pip:
pip install tkinter tkinterdnd2

3.Ensure you have the tkinterdnd2 library installed for drag-and-drop functionality. You can install it using:
pip install tkinterdnd2

Usage

1.Launch the application:
python main.py

2.Use the File menu to:

-Select a folder containing the iTunes backup.

-Backup files to another directory.

-Handle symlinks in the folder.

-Load backup information from JSON files.


3.Use the search bar to search for specific files within the backup.

4.Double-click on any file in the file tree to open it using your default system application.

Key Features

1. Drag and Drop:

Drag and drop a backup folder into the window to automatically categorize and display its contents.

2. Search Functionality:

Type into the search bar and use the "Next" button to highlight and navigate between matching results in the backup tree.

3. Backup Folder Handling:

Use the Backup Files option to create a copy of the selected folder.

4. Symlink Management:

Select a folder to detect and resolve symlinks, displaying their real paths.

5. Database Connection:

The tool connects to Manifest.db to fetch and display backup file metadata, categorized by AppDomain or non-AppDomain entries.

6. Device Information:

Automatically extracts and displays device information such as Device Name, Product Type, and more from the Info.plist file in the backup.

File Structure

main.py: The main script containing the GUI and logic.

icons/: Directory for icons used in the GUI.

Manifest.db: SQLite database file for iTunes backup (should be included in the iTunes backup folder).

Info.plist: Plist file containing device information (part of the iTunes backup).

License

This project is licensed under the MIT License. See LICENSE for more information.


Acknowledgments

-TkinterDnD2 for enabling drag-and-drop functionality within the Tkinter GUI.

-SQLite for database operations.
plistlib for handling plist files.
