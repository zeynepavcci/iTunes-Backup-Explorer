import tkinter as tk
from tkinter import filedialog, messagebox, ttk, PhotoImage
import os
import shutil
import json
from datetime import datetime
import plistlib
import sys  # Import sys for cross-platform file opening
import sqlite3  # Import sqlite3 for database connection
from tkinterdnd2 import DND_FILES, TkinterDnD  # TkinterDnD modülünü ekledik
from tkinter import Scrollbar
import threading


class IntegratedApp(TkinterDnD.Tk):  # TkinterDnD.Tk'yi kullanıyoruz
    def __init__(self):
        super().__init__()
        self.title("iTunes Backup Explorer")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")

        # Check if the icon file exists before loading
        icon_path = "icons/ITunes_logo.svg.png"
        if os.path.exists(icon_path):
            icon = PhotoImage(file=icon_path)
            self.iconphoto(False, icon)
        else:
            messagebox.showerror("Error", f"Icon file not found: {icon_path}")

        # Create a frame for the header and new buttons
        header_frame = tk.Frame(self, bg="#ffffff")
        header_frame.pack(side=tk.TOP, pady=0, fill=tk.X)

        # Create a frame for new buttons
        menu_frame = tk.Frame(header_frame, bg="#ffffff")
        menu_frame.pack(side=tk.LEFT, padx=0)

        # New buttons: File, Edit, Help
        self.file_button = tk.Menubutton(menu_frame, text="File", bg="#ffffff", fg="black", font=("Segoe UI", 9),
                                         relief="flat", anchor='w')
        self.file_menu = tk.Menu(self.file_button, tearoff=0, bg="#ffffff", fg="black", font=("Segoe UI", 9))
        self.file_button.config(menu=self.file_menu)
        self.file_button.pack(side=tk.LEFT, padx=5)

        # Add items to the File menu
        self.file_menu.add_command(label="Select Folder", command=self.select_folder)
        self.file_menu.add_command(label="Backup Files", command=self.backup_files)
        self.file_menu.add_command(label="Handle Symlinks", command=self.handle_symlinks)
        self.file_menu.add_command(label="Load Backup Info", command=self.load_backup_info)
        self.file_menu.add_command(label="Load Data from DB", command=self.show_files)

        self.edit_button = tk.Button(menu_frame, text="Edit", bg="#ffffff", fg="black", font=("Segoe UI", 9),
                                     relief="flat")
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.help_button = tk.Button(menu_frame, text="Help", bg="#ffffff", fg="black", font=("Segoe UI", 9),
                                     relief="flat")
        self.help_button.pack(side=tk.LEFT, padx=5)

        # Create a frame for search bar and button (moved to top-right corner)
        search_frame = tk.Frame(self, bg="#f0f0f0")
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5, anchor='e')

        # Add a search bar
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10), width=20)
        self.search_entry.pack(side=tk.RIGHT, padx=5)

        # Add a search button
        self.search_button = tk.Button(search_frame, text="Search", command=self.perform_search)
        self.search_button.pack(side=tk.RIGHT, padx=5)

        # Create a frame for device info
        info_frame = tk.Frame(self, bg="#f0f0f0", width=200)
        info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Add a title for the device info section
        info_title = tk.Label(info_frame, text="Device\nInformation", font=("Segoe UI", 12), bg="#f0f0f0", anchor='w')
        info_title.pack(anchor='w', padx=40, pady=(0, 10))

        # Add a text area to display device information
        self.device_info_text = tk.StringVar()
        info_label = tk.Label(info_frame, textvariable=self.device_info_text, bg="#f0f0f0", anchor="w", justify="left")
        info_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Create a frame for file display
        tree_frame = tk.Frame(self, bg="#f0f0f0")
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # Create buttons: "Information" and "Files"
        button_frame = tk.Frame(tree_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.TOP, anchor="w")

        self.show_info_button = tk.Button(button_frame, text="Information", font=("Segoe UI", 9), bg="#ffffff",
                                          anchor="w", command=self.show_information)
        self.show_info_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(self, text="Next", command=self.next_match)
        self.next_button.pack()

        # Add the new "Files" button
        self.files_button = tk.Button(button_frame, text="Files", font=("Segoe UI", 9), bg="#ffffff",
                                      anchor="w", command=self.show_files)
        self.files_button.pack(side=tk.LEFT, padx=5)

        # Add the new "Apps" button
        self.apps_button = tk.Button(button_frame, text="Apps", font=("Segoe UI", 9), bg="#ffffff",
                                     anchor="w", command=self.show_apps)
        self.apps_button.pack(side=tk.LEFT, padx=5)

        # Add a default white area for the treeview (this will be shown by default)
        self.tree_placeholder = tk.Frame(tree_frame, bg="white", height=300)
        self.tree_placeholder.pack(pady=0, fill=tk.BOTH, expand=True)

        # Center icon and text in the placeholder
        self.placeholder_content = tk.Frame(self.tree_placeholder, bg="white")
        self.placeholder_content.pack(expand=True)

        # Add a file icon
        file_icon_path = "icons/file_icon.PNG"
        if os.path.exists(file_icon_path):
            file_icon = PhotoImage(file=file_icon_path)
            file_icon = file_icon.subsample(6)
            file_icon_label = tk.Label(self.placeholder_content, image=file_icon, bg="white")
            file_icon_label.image = file_icon
            file_icon_label.pack(pady=10)

        # Add "Drag & Drop" text
        drag_drop_label = tk.Label(self.placeholder_content, text="Drag & Drop", font=("Segoe UI", 10), bg="white")
        drag_drop_label.pack()

        # Enable drag-and-drop on the placeholder
        self.tree_placeholder.drop_target_register(DND_FILES)
        self.tree_placeholder.dnd_bind('<<Drop>>', self.on_file_drop)

        # Treeview to display file type and file names (initially hidden)
        self.tree = ttk.Treeview(tree_frame, columns=("File Type", "File Name", "File Size", "Last Modified"),
                                 show="tree headings")
        self.tree.heading("#0", text="Name", anchor='w')
        self.tree.heading("File Type", text="File Type")
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("File Size", text="File Size")
        self.tree.heading("Last Modified", text="Last Modified")
        self.tree.column("#0", stretch=True, width=200)
        self.tree.column("File Type", stretch=True, width=100)
        self.tree.column("File Name", stretch=True, width=200)
        self.tree.column("File Size", stretch=True, width=100)
        self.tree.column("Last Modified", stretch=True, width=150)

        self.tree.tag_configure("highlight", background="yellow")

        # TreeView'e Scrollbar ekleme (dikey ve yatay)
        self.tree_scroll_y = Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_scroll_x = Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.configure(yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)

        # Bind double-click event to open file
        self.tree.bind("<Double-1>", self.open_selected_file)

        # Dictionary to store file paths (for child nodes)
        self.file_paths = {}

        # Veritabanı bağlantısını başlat
        self.connect_to_db()

    def connect_to_db(self):
        """Connect to the Manifest.db database."""
        try:
            self.conn = sqlite3.connect("Manifest.db")
            self.cursor = self.conn.cursor()
            messagebox.showinfo("DB Connection", "Successfully connected to the database!")
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"Error connecting to database: {e}")

    def load_data_from_db(self):
        """Veritabanından veri çek."""
        try:
            # You may want to modify this based on your actual database schema
            self.cursor.execute("SELECT fileID, domain, relativePath FROM Files")
            rows = self.cursor.fetchall()
            for row in rows:
                print(row)  # Verileri konsolda yazdırabilir ya da GUI'de gösterebilirsiniz
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"Error fetching data from database: {e}")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.categorize_folder(folder_path)
            self.display_device_info_from_plist(folder_path)

    def _categorize_folder(self, folder_path):
        # Start a new thread to handle the folder categorization

        self.tree.delete(*self.tree.get_children())  # Clear existing items
        # Dictionary to store file types and their files
        self.file_types = {}
        self.file_paths = {}  # Reset file paths
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_type = self.categorize_file(file_path)
                metadata = self.extract_file_metadata(file_path)
                # Store files by file type
                if file_type not in self.file_types:
                    self.file_types[file_type] = []  # Create a list for each file type
                self.file_types[file_type].append((file, file_path, metadata))
        # After categorizing, populate the TreeView hierarchically
        self.populate_treeview()

        messagebox.showinfo("Folder Selected", f"Files in '{folder_path}' have been categorized.")

    def categorize_folder(self, folder_path):
        threading.Thread(target=self._categorize_folder, args=(folder_path,), daemon=True).start()

    def populate_treeview(self):
        """Populate the TreeView with hierarchical data."""
        for file_type, files in self.file_types.items():
            # Insert file type as parent node
            parent_id = self.tree.insert("", "end", text=file_type, values=(file_type, "", "", ""))
            for file_name, file_path, metadata in files:
                # Insert each file as a child node
                self.tree.insert(parent_id, "end", text=file_name,
                                 values=(file_type, file_name, f"{metadata['size']} bytes", metadata['last_modified']))
                self.file_paths[file_name] = file_path  # Store the path with file name as key

    def extract_file_metadata(self, file_path):
        """Extract metadata from the file."""
        try:
            metadata = {}
            metadata['size'] = os.path.getsize(file_path)
            metadata['last_modified'] = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(
                '%Y-%m-%d %H:%M:%S')
            return metadata
        except Exception as e:
            messagebox.showerror("Error", f"Could not extract metadata: {e}")
            return {}

    def categorize_file(self, file_path):
        """Categorize file based on its content or extension."""
        try:

            # Option 2: Categorize based on file header (commented out)

            with open(file_path, 'rb') as f:
                header = f.read(16)
                if header.startswith(b'\x53\x51\x4C\x69'):  # SQLite signature
                    return "SQLite Database"
                elif header.startswith(b'bplist'):
                    return "Configuration File"
                else:
                    return "Unknown File Type"

        except Exception as e:
            messagebox.showerror("Error", f"File could not be read: {e}")
            return "Error"

    def show_apps(self):
        """Veritabanındaki dosyaları domain bilgisine göre göster (sadece 'AppDomain' ile başlayanları)."""
        try:
            # Veritabanından fileID, domain ve relativePath bilgilerini çekiyoruz
            self.cursor.execute("SELECT fileID, domain, relativePath FROM Files")
            rows = self.cursor.fetchall()

            # TreeView'i temizle
            self.tree.delete(*self.tree.get_children())

            # Domainlere göre dosyaları kategorize et
            domain_files = {}
            for row in rows:
                file_id, domain, relative_path = row
                # Sadece 'AppDomain' ile başlayan domain'leri filtrele
                if domain.startswith("AppDomain"):
                    if domain not in domain_files:
                        domain_files[domain] = []
                    domain_files[domain].append((file_id, relative_path))

            # Kategorize edilen dosyaları TreeView'e ekle
            for domain, files in domain_files.items():
                parent_id = self.tree.insert("", "end", text=domain, values=(domain, "", "", ""))
                for file_id, relative_path in files:
                    self.tree.insert(parent_id, "end", text=relative_path,
                                     values=("", relative_path, file_id, ""))
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"Error fetching data from database: {e}")

    def show_files(self):
        """Veritabanındaki dosyaları domain bilgisine göre göster (AppDomain ile başlamayanları)."""
        try:
            # Veritabanından fileID, domain ve relativePath bilgilerini çekiyoruz
            self.cursor.execute("SELECT fileID, domain, relativePath FROM Files")
            rows = self.cursor.fetchall()

            # TreeView'i temizle
            self.tree.delete(*self.tree.get_children())

            # Domainlere göre dosyaları kategorize et
            domain_files = {}
            for row in rows:
                file_id, domain, relative_path = row
                # 'AppDomain' ile başlayanları filtrele (görmezden gel)
                if not domain.startswith("AppDomain"):
                    if domain not in domain_files:
                        domain_files[domain] = []
                    domain_files[domain].append((file_id, relative_path))

            # Kategorize edilen dosyaları TreeView'e ekle
            for domain, files in domain_files.items():
                parent_id = self.tree.insert("", "end", text=domain, values=(domain, "", "", ""))
                for file_id, relative_path in files:
                    self.tree.insert(parent_id, "end", text=relative_path,
                                     values=("", relative_path, file_id, ""))
        except sqlite3.Error as e:
            messagebox.showerror("DB Error", f"Error fetching data from database: {e}")

    def show_information(self):
        """Function to show the information headers when button is clicked."""
        self.tree_placeholder.pack_forget()  # Hide the placeholder when the tree is shown
        self.tree.pack(pady=10, expand=True, fill=tk.BOTH)
        self.tree.delete(*self.tree.get_children())
        self.populate_treeview()
        # Bind single-click event to expand/collapse categories if needed
        # self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def perform_search(self):
        search_query = self.search_var.get().lower()  # Arama kutusundan alınan girdiyi küçük harf yapar
        self.reset_highlights()  # Önceki vurguları temizler

        if not search_query:
            # Eğer arama kutusu boşsa, hiçbir işlem yapma
            messagebox.showinfo("Search", "Please enter a search term.")
            return

        # Eşleşen item'ları tutmak için bir liste oluştur
        self.matching_items = []

        # Tüm ana öğeleri ve alt öğeleri dolaşarak arama yap
        for item_id in self.tree.get_children():
            self.search_in_tree(item_id, search_query)

        if not self.matching_items:
            messagebox.showinfo("Search", "No matching files found.")
        else:
            self.current_match_index = 0  # İlk eşleşen öğeyi başlat
            self.highlight_current_match()
            messagebox.showinfo("Search", f"Found {len(self.matching_items)} matching files.")

    def search_in_tree(self, item_id, search_query):
        file_name = self.tree.item(item_id, "text").lower()
        match = search_query in file_name

        if match:
            # Eğer dosya ismi aramayla eşleşirse, bu dosyayı görünür yap ve listeye ekle
            self.tree.see(item_id)  # Öğeyi görünür yapar
            self.matching_items.append(item_id)
            return True

        # Alt öğeleri kontrol et
        for child_id in self.tree.get_children(item_id):
            if self.search_in_tree(child_id, search_query):
                # Eğer bir alt öğe eşleşirse, o zaman üst öğeyi de genişlet
                self.tree.item(item_id, open=True)  # Kategoriyi genişlet
                return True

        return False

    def highlight_current_match(self):
        """Şu anda eşleşen öğeyi vurgular."""
        self.reset_highlights()  # Önce tüm vurguları kaldır

        if self.matching_items:
            current_item = self.matching_items[self.current_match_index]
            self.tree.item(current_item, tags=("highlight",))
            self.tree.see(current_item)  # Vurgulanan öğeyi görünür yapar


    def next_match(self):
        """Sonraki eşleşen öğeye gider."""
        if self.matching_items:
            self.current_match_index = (self.current_match_index + 1) % len(self.matching_items)
            self.highlight_current_match()

    def reset_highlights(self):
        """Tüm vurguları temizle."""
        for item_id in self.tree.get_children():
            self.tree.item(item_id, tags=())
            for child_id in self.tree.get_children(item_id):
                self.tree.item(child_id, tags=())

    def backup_files(self):
        folder_path = filedialog.askdirectory(title="Select Folder for Backup")
        if folder_path:
            # Implementation for backup (example: zip or copy files)
            messagebox.showinfo("Backup", f"Backup for '{folder_path}' initiated.")

    def handle_symlinks(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Symlinks")
        if folder_path:
            for root, dirs, files in os.walk(folder_path):
                for name in dirs + files:
                    path = os.path.join(root, name)
                    if os.path.islink(path):
                        real_path = os.path.realpath(path)
                        messagebox.showinfo("Symlink Info", f"Symlink: {path}\nReal Path: {real_path}")

    def load_backup_info(self):
        backup_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if backup_file:
            with open(backup_file, "r") as file:
                backup_info = json.load(file)
            # Process backup info here (e.g., display or use it)
            messagebox.showinfo("Backup Info Loaded", f"Backup information loaded from {backup_file}.")

    def display_device_info_from_plist(self, folder_path):
        """Display device information from Info.plist."""
        plist_path = os.path.join(folder_path, "Info.plist")
        try:
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)
                device_info = {
                    'Device Name': plist_data.get('Device Name', 'Unknown'),
                    'Product Type': plist_data.get('Product Type', 'Unknown'),
                    'Build Version': plist_data.get('Build Version', 'Unknown'),
                    'Serial Number': plist_data.get('Serial Number', 'Unknown'),
                    'Product Version': plist_data.get('Product Version', 'Unknown')
                }
                self.device_info_text.set("\n".join([f"{key}: {value}" for key, value in device_info.items()]))
        except Exception as e:
            messagebox.showerror("Error", f"Error reading plist file: {e}")
            self.device_info_text.set(
                "Device Name: Unknown\nProduct Type: Unknown\nBuild Version: Unknown\nSerial Number: Unknown\nProduct Version: Unknown")

    def on_file_drop(self, event):
        """Handles files dropped into the placeholder area."""
        dropped_files = self.tk.splitlist(event.data)
        if dropped_files:
            # Assume the first file dropped is the folder to categorize
            folder_path = dropped_files[0]
            if os.path.isdir(folder_path):
                self.categorize_folder(folder_path)
                self.display_device_info_from_plist(folder_path)
            else:
                messagebox.showerror("Error", "Please drop a valid folder.")

    def open_selected_file(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            parent_id = self.tree.parent(item_id)
            if parent_id:
                file_name = self.tree.item(item_id, 'text')
                file_path = self.file_paths.get(file_name)
                if file_path:
                    try:
                        if sys.platform == "win32":
                            os.startfile(file_path)
                        elif sys.platform == "darwin":
                            os.system(f"open '{file_path}'")
                        else:
                            os.system(f"xdg-open '{file_path}'")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open file: {e}")
                else:
                    messagebox.showwarning("File Not Found", "The selected file path could not be found.")


if __name__ == "__main__":
    app = IntegratedApp()
    app.mainloop()
