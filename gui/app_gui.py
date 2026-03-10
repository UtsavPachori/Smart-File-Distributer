import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
from tkinter import messagebox
from collections import defaultdict
from pathlib import Path
import shutil
import os
import sys
from tkinterdnd2 import DND_FILES, TkinterDnD
from core.scanner import scan_folder
from core.file_mover import move_file, get_destination
from core.scanner_plus import scan_folder_with_data
from core.duplicate_finder import find_duplicates, get_file_hash
from utils.size_formatter import format_size
from gui.duplicate_viewer import DuplicateViewer

class AppGUI:

    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Smart File Organizer - by Utsav")
        self.root.geometry("650x500")

        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)
        
        self.root.iconbitmap(resource_path("favicon.ico"))

        self.selected_folder = None
        self.move_history = []

        self.scan_folders = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.drop_folder)

        self.select_button = tk.Button(
            self.root,
            text="Select Folder",
            command=self.select_folder
        )
        self.select_button.pack(pady=10)

        self.checkbox = tk.Checkbutton(
            self.root,
            text="Scan inside folders",
            variable=self.scan_folders
        )
        self.checkbox.pack()

        self.start_button = tk.Button(
            self.root,
            text="Start Organizing",
            command=self.start_organizing
        )
        self.start_button.pack(pady=10)

        self.duplicate_button = tk.Button(
            self.root,
            text="Scan For Duplicates",
            command=self.scan_duplicates
        )

        self.duplicate_button.pack(pady=10)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(pady=10)

        self.status_label = tk.Label(
            self.root,
            text="Select a folder to begin",
            wraplength=400,
            justify="left"
        )
        self.status_label.pack(pady=20)

        self.result_box = tk.Text(self.root, height=6, width=60)
        self.result_box.pack(pady=10)
        self.result_box.insert("1.0", "Results will appear here.")
        self.result_box.config(state="disabled")

        self.clean_downloads_button = tk.Button(
            self.root,
            text="Clean Downloads Folder",
            command=self.clean_downloads
        )

        self.clean_downloads_button.pack(pady=10)

        self.undo_button = tk.Button(
            self.root,
            text="Undo Last Organization",
            command=self.undo_last
        )
        self.undo_button.pack(pady=5)

    def clean_downloads(self):
        downloads_path = Path.home() / "Downloads"

        if not downloads_path.exists():
            messagebox.showerror("Error", "Downloads folder not found.")
            return

        self.selected_folder = str(downloads_path)

        confirm = messagebox.askyesno(
            "Clean Downloads",
            "This will organize all files in your Downloads folder.\n\nContinue?"
        )

        if not confirm:
            return

        thread = threading.Thread(target=self.organize_files)
        thread.start()

    def select_folder(self):
        folder = filedialog.askdirectory()

        if folder:
            self.selected_folder = folder
            self.status_label.config(text=f"Selected Folder:\n{folder}")

    def update_progress(self, done):
        self.root.after(0, lambda: self.progress.config(value=done))

    def start_organizing(self):
        if not self.selected_folder:
            self.status_label.config(text="Please select a folder first.")
            return
        
        self.set_ui_state("disabled")

        thread = threading.Thread(target=self.organize_files)
        thread.start()

    def organize_files(self):
        scan_option = self.scan_folders.get()

        self.status_label.config(text="Scanning files...")
        self.root.update()

        files = scan_folder(self.selected_folder, scan_option)

        if not files:
            self.status_label.config(text="No files found.")
            self.set_ui_state("normal")
            return

        stats = defaultdict(int)

        preview_lines = []

        for file_path in files:
            ext = file_path.suffix.lower()
            stats[ext] += 1
            destination = get_destination(ext, self.selected_folder)

            if destination:
                preview_lines.append(f"{file_path.name} → {destination.name}")

                preview_text = "\n".join(preview_lines[:20])

                if len(preview_lines) > 20:
                    preview_text += "\n..."

                confirm = messagebox.askyesno(
                    "Preview Changes",
                    f"Files to be organized:\n\n{preview_text}\n\nProceed?"
                )

                if not confirm:
                    self.status_label.config(text="Operation cancelled.")
                    self.set_ui_state("normal")
                    return

                total_files = len(files)

                self.progress["maximum"] = total_files
                self.progress["value"] = 0

                for index, file_path in enumerate(files, start=1):
                    result, new_location = move_file(file_path, self.selected_folder)
                    self.move_history.append((new_location, file_path))
                    message = f"{index}/{total_files} : {file_path.name} → {result}"
                    self.root.after(0, lambda m=message: self.status_label.config(text=m))
                    self.progress["value"] = index
                    self.root.update()

                self.root.after(0, lambda: self.status_label.config(text="Organization Completed."))

                summary_lines = [f"{ext}: {count}" for ext, count in stats.items()]
                summary_text = "\n".join(summary_lines)

                self.root.after(0, self.update_result(summary_text))

                os.startfile(self.selected_folder)

                self.set_ui_state("normal")

            self.set_ui_state("normal")
            self.root.after(0, lambda: self.status_label.config(text="No Files Found To Organize."))
            return

    def scan_duplicates(self):
        self.set_ui_state("disabled")

        thread = threading.Thread(target=self.run_dup_scan)
        thread.start()

    def run_dup_scan(self):
        folder = self.selected_folder

        if not folder:
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, "Please select a folder first.")
            self.set_ui_state("normal")
            return
        
        self.root.after(0, lambda: self.status_label.config(text="Scanning files for duplicates..."))
        
        scan_option = self.scan_folders.get()
        files = scan_folder_with_data(folder, recursive=scan_option)

        self.progress["maximum"] = len(files)
        self.progress["value"] = 0

        duplicates_list, wasted_space = find_duplicates(files, progress_callback=self.update_progress)

        duplicate_groups = duplicates_list

        result_text = (
            f"Files scanned: {len(files)}\n"
            f"Duplicates found: {len(duplicates_list)}\n"
            f"Space recoverable: {format_size(wasted_space)}"
        )

        self.root.after(0, self.update_result(result_text))

        self.root.after(0, lambda: self.status_label.config(text="Duplicate scan completed."))

        if duplicate_groups:
            self.root.after(0, lambda: DuplicateViewer(self.root, duplicate_groups, wasted_space))

        self.set_ui_state("normal")

    def update_result(self, result_text):
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, result_text)
        self.result_box.config(state="disabled")

    def set_ui_state(self, state):
        self.select_button.config(state=state)
        self.start_button.config(state=state)

    def undo_last(self):
        if not self.move_history:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        for new, old in reversed(self.move_history):
            try:
                shutil.move(new, old)
            except Exception as e:
                print(f"Failed to undo move: {e}")

        self.move_history.clear()
        os.startfile(self.selected_folder)

        messagebox.showinfo("Undo", "Last organization undone.")

    def drop_folder(self, event):
        folder = event.data.strip("{}")

        self.selected_folder = folder
        self.status_label.config(text=f"Dropped Folder:\n{folder}")

    def run(self):
        self.root.mainloop()