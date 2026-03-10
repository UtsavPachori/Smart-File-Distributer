import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import sys
from utils.size_formatter import format_size

class DuplicateViewer:
    def __init__(self, master, duplicate_groups, wasted_space):
        self.master = tk.Toplevel(master) 
        self.master.title("Duplicate Files")
        self.master.geometry("750x450")
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)
        
        self.master.iconbitmap(resource_path("favicon.ico"))

        self.duplicate_groups = duplicate_groups
        self.wasted_space = wasted_space
        self.check_vars = [] 

        self.create_widgets()

    def create_widgets(self):
        header = ttk.Label(
        self.master,
        text=f"Total Recoverable Space: {format_size(self.wasted_space)}",
        font=("Arial", 11, "bold"),
        foreground="green"
        )
        header.pack(pady=10)
        container = ttk.Frame(self.master)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for group in self.duplicate_groups:
            original_path = group[0]

            try:
                file_size = os.path.getsize(original_path)
                size_text = format_size(file_size)
                waste = file_size * (len(group) - 1)
                waste_text = format_size(waste)
            except Exception:
                size_text = "Unknown"
                waste_text = "Unknown"

            label = ttk.Label(
                self.scrollable_frame,
                text=f"Original: {Path(original_path).name}",
                font=("Arial", 10, "bold")
            )
            label.pack(anchor="w", pady=(10, 0))

            info_label = ttk.Label(
                self.scrollable_frame,
                text=f"Size: {size_text} each | Recoverable space: {waste_text}",
                font=("Arial", 9),
                foreground="blue"
            )
            info_label.pack(anchor="w", padx=10)

            for file_path in group[1:]:
                var = tk.IntVar()

                try:
                    size = os.path.getsize(file_path)
                    size_text = format_size(size)
                except Exception:
                    size_text = "Unknown size"

                display_text = f"{Path(file_path).name}  ({size_text})"

                cb = ttk.Checkbutton(
                    self.scrollable_frame,
                    text=display_text,
                    variable=var
                )
                cb.pack(anchor="w", padx=20)

                path_label = ttk.Label(
                    self.scrollable_frame,
                    text=file_path,
                    font=("Arial", 8),
                    foreground="gray"
                )
                path_label.pack(anchor="w", padx=40)

                self.check_vars.append((var, file_path))

        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=10)

        select_all_btn = ttk.Button(
            button_frame,
            text="Select All",
            command=self.select_all
        )
        select_all_btn.pack(side="left", padx=5)

        unselect_all_btn = ttk.Button(
            button_frame,
            text="Unselect All",
            command=self.unselect_all
        )
        unselect_all_btn.pack(side="left", padx=5)

        auto_delete_btn = ttk.Button(
            button_frame,
            text="Delete All Duplicates",
            command=self.delete_all_duplicates
        )
        auto_delete_btn.pack(side="left", padx=5)

        keep_newest_btn = ttk.Button(
            button_frame,
            text="Keep Newest",
            command=self.keep_newest
        )
        keep_newest_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_selected
        )
        delete_btn.pack(side="left", padx=5)

    def select_all(self):
        for var, _ in self.check_vars:
            var.set(1)

    def unselect_all(self):
        for var, _ in self.check_vars:
            var.set(0)

    def delete_selected(self):
        to_delete = [path for var, path in self.check_vars if var.get() == 1]

        if not to_delete:
            messagebox.showinfo("Info", "No files selected for deletion.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(to_delete)} files?")
        if not confirm:
            return

        deleted = 0
        recovered_space = 0

        for path in to_delete:
            try:
                file_size = os.path.getsize(path)
                os.remove(path)

                deleted += 1
                recovered_space += file_size

            except Exception as e:
                print(f"Failed to delete {path}: {e}")

        messagebox.showinfo(
            "Deleted", 
            f"{deleted} files deleted successfully.\n\nSpace recovered: {format_size(recovered_space)}"
        )

        self.master.destroy()

    def delete_all_duplicates(self):
        to_delete = []

        for group in self.duplicate_groups:
            duplicates = group[1:]
            to_delete.extend(duplicates)

        if not to_delete:
            messagebox.showinfo("Info", "No duplicates to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete {len(to_delete)} duplicate files?"
        )

        if not confirm:
            return

        deleted = 0
        recovered_space = 0

        for path in to_delete:
            try:
                size = os.path.getsize(path)
                os.remove(path)

                deleted += 1
                recovered_space += size

            except Exception as e:
                print(f"Failed to delete {path}: {e}")

        messagebox.showinfo(
            "Deleted",
            f"{deleted} duplicate files removed.\n\nSpace recovered: {format_size(recovered_space)}"
        )

        self.master.destroy()

    def keep_newest(self):
        to_delete = []

        for group in self.duplicate_groups:
            newest_file = max(group, key=os.path.getmtime)

            for path in group:
                if path != newest_file:
                    to_delete.append(path)

        if not to_delete:
            messagebox.showinfo("Info", "Nothing to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete {len(to_delete)} older duplicate files?"
        )

        if not confirm:
            return

        deleted = 0
        recovered_space = 0

        for path in to_delete:
            try:
                size = os.path.getsize(path)
                os.remove(path)

                deleted += 1
                recovered_space += size

            except Exception as e:
                print(f"Failed to delete {path}: {e}")

        messagebox.showinfo(
            "Completed",
            f"{deleted} older duplicates deleted.\n\nSpace recovered: {format_size(recovered_space)}"
        )
        
        self.master.destroy()