import customtkinter as ctk
from customtkinter import filedialog
import os
import sys

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Txt")
        self.geometry("700x400")
        self.current_path = None
        self.is_dirty = False

        self.toolbar_frame = ctk.CTkFrame(master=self, height=40)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew")

        self.btn_open = ctk.CTkButton(master=self.toolbar_frame, text="Open", width=30, command=self.open_file)
        self.btn_open.pack(side="left", padx=0, pady=0)
        self.btn_open.configure(fg_color="transparent")

        self.btn_save = ctk.CTkButton(master=self.toolbar_frame, text="Save", width=30, command=self.save_file)
        self.btn_save.pack(side="left", padx=0, pady=0)
        self.btn_save.configure(fg_color="transparent")
        self.bind("<Control-s>", self.save_file)

        self.btn_new = ctk.CTkButton(master=self.toolbar_frame, text="new", width=30, command=self.new_file)
        self.btn_new.pack(side="left", padx=0, pady=0)
        self.btn_new.configure(fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(master=self, width=650,height=300, corner_radius=0)
        self.textbox.grid(row=1, column=0, sticky="nsew")

        self.status_frame = ctk.CTkFrame(master=self, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, sticky="ew")   
        self.status_label = ctk.CTkLabel(master=self.status_frame, text="caracter:  | word:  ")
        self.status_label.pack(side="right", padx=10)

        self.textbox.bind("<KeyRelease>", self.text_changed)
        
        if len(sys.argv) > 1:
            outside_file = sys.argv[1].strip("'").strip('"')

            if os.path.exists(outside_file):
                try:
                    with open(outside_file, "r", encoding="utf-8") as file:
                        text = file.read()

                    self.textbox.insert("0.0", text)
                    self.current_path = outside_file
                    self.set_title()

                    word_num = len(text.split())
                    caracter_num = len(text)
                    self.status_label.configure(text=f"caracter: {caracter_num} | word: {word_num}")
                except Exception as e:
                    # Çökmek yerine Textbox'a hatayı yazdır
                    self.textbox.insert("0.0", f"Hata olustu: {e}")

    def open_file(self, event=None):
        filepath = filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()

            self.textbox.delete("0.0", "end-1c")
            self.textbox.insert("0.0", text)
            self.current_path = filepath
            self.is_dirty = False
            self.set_title() 

    def save_file(self, event=None):
        if self.current_path:
            text = self.textbox.get("0.0", "end-1c")
            with open(self.current_path, "w", encoding="utf-8") as file:
                file.write(text)
            self.is_dirty = False
            self.set_title()
        else:
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("text file", ".txt"), ("All file", "*.*")]
            )

            if filepath:
                text =self.textbox.get("0.0", "end")

                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(text)
                self.current_path = filepath
                self.is_dirty = False
                self.set_title()

    def new_file(self, event=None):
        self.textbox.delete("0.0", "end") 
        self.current_path = None          
        self.is_dirty = False
        self.set_title()

    def set_title(self):
        title = "Text pad"
        if self.current_path:
            file_name = os.path.basename(self.current_path)
            title += f" - {file_name}"
        
        if self.is_dirty:
            title += "   *"
            
        self.title(title)

    def text_changed(self, event=None):
        if not self.is_dirty:
            self.is_dirty = True
            self.set_title()

        text = self.textbox.get("0.0", "end-1c")

        word_num = len(text.split())
        caracter_num = len(text)

        self.status_label.configure(text=f"caracter: {caracter_num} | word: {word_num}")       

app = App()
app.mainloop()
