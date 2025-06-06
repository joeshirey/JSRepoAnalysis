import tkinter as tk
from tkinter import filedialog
import os
import sys
from io import StringIO
from main import main as process_main_function # Import the modified main function

class TkinterUI:
    def __init__(self, master):
        self.master = master
        master.title("File/Folder Processor")

        self.path_label = tk.Label(master, text="No file or folder selected.")
        self.path_label.pack(pady=10)

        self.select_file_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_file_button.pack(pady=5)

        self.select_folder_button = tk.Button(master, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(pady=5)

        self.process_button = tk.Button(master, text="Process", command=self.process_path)
        self.process_button.pack(pady=10)

        self.output_text = tk.Text(master, height=20, width=80)
        self.output_text.pack(pady=10)

        self.selected_path = None

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_path = file_path
            self.path_label.config(text=f"Selected File: {self.selected_path}")
            self.output_text.delete(1.0, tk.END) # Clear previous output

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_path = folder_path
            self.path_label.config(text=f"Selected Folder: {self.selected_path}")
            self.output_text.delete(1.0, tk.END) # Clear previous output

    def process_path(self):
        if self.selected_path:
            self.output_text.delete(1.0, tk.END) # Clear previous output
            self.output_text.insert(tk.END, f"Processing: {self.selected_path}\n")
            
            # Redirect stdout to capture print statements from main.py
            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output

            try:
                process_main_function(self.selected_path)
                output = redirected_output.getvalue()
                self.output_text.insert(tk.END, output)
            except Exception as e:
                self.output_text.insert(tk.END, f"An error occurred: {e}\n")
            finally:
                sys.stdout = old_stdout # Restore stdout
        else:
            self.output_text.insert(tk.END, "Please select a file or folder first.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TkinterUI(root)
    root.mainloop()
