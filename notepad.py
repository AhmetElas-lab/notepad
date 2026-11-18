import customtkinter as ctk
from customtkinter import filedialog
import tkinter as tk
import os
import sys


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x400")
        self.current_path = None
        self.last_saved_content = ""
        self.is_dirty = False
        self.is_topmost = False
        self.is_focus = False
        self.set_title()

        # Toolbar Frame
        self.toolbar_frame = ctk.CTkFrame(master=self, height=40)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew")

        self.btn_open = ctk.CTkButton(master=self.toolbar_frame, text="Open", width=40, command=self.open_file)
        self.btn_open.pack(side="left", padx=2, pady=2)
        self.btn_open.configure(fg_color="transparent")

        self.btn_save = ctk.CTkButton(master=self.toolbar_frame, text="Save", width=40, command=self.save_file)
        self.btn_save.pack(side="left", padx=2, pady=2)
        self.btn_save.configure(fg_color="transparent")

        self.btn_new = ctk.CTkButton(master=self.toolbar_frame, text="New", width=40, command=self.new_file)
        self.btn_new.pack(side="left", padx=2, pady=2)
        self.btn_new.configure(fg_color="transparent")

        self.btn_pin = ctk.CTkButton(master=self.toolbar_frame, text="📌 Pin", width=55, command=self.toggle_pin)
        self.btn_pin.pack(side="left", padx=(10, 2), pady=2)
        self.btn_pin.configure(fg_color="transparent")

        self.btn_focus = ctk.CTkButton(master=self.toolbar_frame, text="🎯 Focus", width=65, command=self.toggle_focus)
        self.btn_focus.pack(side="left", padx=2, pady=2)
        self.btn_focus.configure(fg_color="transparent")

        # Grid configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main Textbox
        self.textbox = ctk.CTkTextbox(master=self, width=650, height=300, corner_radius=0, undo=True)
        self.textbox.grid(row=1, column=0, sticky="nsew")

        # Status Frame
        self.status_frame = ctk.CTkFrame(master=self, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(master=self.status_frame, text="caracter: 0 | word: 0")
        self.status_label.pack(side="right", padx=10)

        self.label_save = ctk.CTkLabel(master=self.status_frame, text="")
        self.label_save.pack(side="right", padx=10)

        # Event bindings for text changes
        self.textbox.bind("<KeyRelease>", self.text_changed)
        self.textbox.bind("<ButtonRelease-1>", self.text_changed)

        # Shortcut bindings for Save (Ctrl+S), Open (Ctrl+O), New (Ctrl+N), Save As (Ctrl+Shift+S)
        for seq in ("<Control-s>", "<Control-S>"):
            self.bind_all(seq, self.save_file)
            self.textbox.bind(seq, self.save_file)

        for seq in ("<Control-o>", "<Control-O>"):
            self.bind_all(seq, self.open_file)
            self.textbox.bind(seq, self.open_file)

        for seq in ("<Control-n>", "<Control-N>"):
            self.bind_all(seq, self.new_file)
            self.textbox.bind(seq, self.new_file)

        for seq in ("<Control-Shift-s>", "<Control-Shift-S>"):
            self.bind_all(seq, self.save_as_file)
            self.textbox.bind(seq, self.save_as_file)

        # Shortcut bindings for Pin / Always on Top (Ctrl+T or Alt+T)
        for seq in ("<Control-t>", "<Control-T>", "<Alt-t>", "<Alt-T>"):
            self.bind_all(seq, self.toggle_pin)
            self.textbox.bind(seq, self.toggle_pin)

        # Shortcut bindings for Focus Mode (Ctrl+Shift+F to toggle, Esc to exit)
        for seq in ("<Control-Shift-f>", "<Control-Shift-F>"):
            self.bind_all(seq, self.toggle_focus)
            self.textbox.bind(seq, self.toggle_focus)

        self.bind_all("<Escape>", self.on_escape)
        self.textbox.bind("<Escape>", self.on_escape)

        # Right-click context menu (allows exiting Focus Mode, toggling Pin, etc.)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.textbox.bind("<Button-3>", self.show_context_menu)
        self.bind("<Button-3>", self.show_context_menu)

        # Open file passed via command line argument / Windows file association (if any)
        if len(sys.argv) > 1:
            raw_arg = sys.argv[1].strip("'").strip('"')
            # Handle cases where Windows passes unquoted arguments with spaces
            if not os.path.exists(raw_arg) and len(sys.argv) > 2:
                joined = " ".join(sys.argv[1:]).strip("'").strip('"')
                if os.path.exists(joined):
                    raw_arg = joined

            if os.path.exists(raw_arg):
                self.load_file(os.path.abspath(raw_arg))

    def set_pin(self, enabled):
        """Sets 'Always on Top' state and updates the Pin button appearance."""
        self.is_topmost = bool(enabled)
        self.attributes("-topmost", self.is_topmost)
        if self.is_topmost:
            self.btn_pin.configure(text="📌 Pinned", fg_color=("#3B8ED0", "#1F6AA5"))
        else:
            self.btn_pin.configure(text="📌 Pin", fg_color="transparent")

    def toggle_pin(self, event=None):
        """Toggles 'Always on Top' state so the window stays visible even when losing focus."""
        self.set_pin(not self.is_topmost)
        return "break"

    def set_focus_mode(self, enabled):
        """Hides top toolbar and bottom status bar in Focus Mode and automatically enables Pin."""
        self.is_focus = bool(enabled)
        if self.is_focus:
            self.toolbar_frame.grid_remove()
            self.status_frame.grid_remove()
            self.btn_focus.configure(text="🎯 Focused", fg_color=("#3B8ED0", "#1F6AA5"))
            self.set_pin(True)
        else:
            self.toolbar_frame.grid(row=0, column=0, sticky="ew")
            self.status_frame.grid(row=2, column=0, sticky="ew")
            self.btn_focus.configure(text="🎯 Focus", fg_color="transparent")
        self.textbox.focus_set()

    def toggle_focus(self, event=None):
        """Toggles Focus Mode on or off."""
        self.set_focus_mode(not self.is_focus)
        return "break"

    def on_escape(self, event=None):
        """Exits Focus Mode when Escape is pressed."""
        if self.is_focus:
            self.set_focus_mode(False)
            return "break"
        return None

    def show_context_menu(self, event):
        """Displays a right-click context menu with Focus Mode, Pin, and editor actions."""
        self.context_menu.delete(0, "end")
        focus_label = "Exit Focus Mode (Esc)" if self.is_focus else "Focus Mode (Ctrl+Shift+F)"
        self.context_menu.add_command(label=focus_label, command=self.toggle_focus)

        pin_label = "Unpin (Always on Top)" if self.is_topmost else "Pin (Always on Top)"
        self.context_menu.add_command(label=pin_label, command=self.toggle_pin)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Open...", command=self.open_file)
        self.context_menu.add_command(label="Save", command=self.save_file)
        self.context_menu.add_command(label="New", command=self.new_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Cut",
            command=lambda: (self.textbox._textbox.event_generate("<<Cut>>"), self.after_idle(self.text_changed)),
        )
        self.context_menu.add_command(
            label="Copy",
            command=lambda: self.textbox._textbox.event_generate("<<Copy>>"),
        )
        self.context_menu.add_command(
            label="Paste",
            command=lambda: (self.textbox._textbox.event_generate("<<Paste>>"), self.after_idle(self.text_changed)),
        )
        self.context_menu.add_command(
            label="Select All",
            command=lambda: self.textbox._textbox.event_generate("<<SelectAll>>"),
        )

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
        return "break"

    def load_file(self, filepath):
        """Loads a file from the given path into the editor."""
        filepath = os.path.abspath(filepath)
        try:
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    text = file.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="cp1254") as file:
                    text = file.read()
        except Exception as e:
            text = f"Hata olustu: {e}"

        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        self.current_path = filepath
        self.last_saved_content = text
        self.is_dirty = False
        self.set_title()
        self.update_save_label()
        self.update_stats(text)

    def open_file(self, event=None):
        filepath = filedialog.askopenfilename(
            title="Choose a file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.load_file(filepath)
        return "break"

    def save_file(self, event=None):
        if self.current_path:
            text = self.textbox.get("0.0", "end-1c")
            try:
                with open(self.current_path, "w", encoding="utf-8") as file:
                    file.write(text)
                self.last_saved_content = text
                self.is_dirty = False
                self.set_title()
                self.update_save_label()
            except Exception as e:
                self.status_label.configure(text=f"Hata olustu: {e}")
            return "break"
        else:
            return self.save_as_file(event)

    def save_as_file(self, event=None):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            filepath = os.path.abspath(filepath)
            text = self.textbox.get("0.0", "end-1c")
            try:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(text)
                self.current_path = filepath
                self.last_saved_content = text
                self.is_dirty = False
                self.set_title()
                self.update_save_label()
            except Exception as e:
                self.status_label.configure(text=f"Hata olustu: {e}")
        return "break"

    def new_file(self, event=None):
        self.textbox.delete("0.0", "end")
        self.current_path = None
        self.last_saved_content = ""
        self.is_dirty = False
        self.set_title()
        self.status_label.configure(text="caracter: 0 | word: 0")
        self.update_save_label()
        return "break"

    def set_title(self):
        title = "Text pad"
        if self.current_path:
            file_name = os.path.basename(self.current_path)
            title += f" - {file_name}"

        if self.is_dirty:
            title += "   *"

        self.title(title)

    def text_changed(self, event=None):
        text = self.textbox.get("0.0", "end-1c")
        was_dirty = self.is_dirty
        self.is_dirty = (text != self.last_saved_content)

        if self.is_dirty != was_dirty:
            self.set_title()
            self.update_save_label()

        self.update_stats(text)

    def update_stats(self, text):
        word_num = len(text.split())
        caracter_num = len(text)
        self.status_label.configure(text=f"caracter: {caracter_num} | word: {word_num}")

    def update_save_label(self):
        if self.is_dirty:
            self.label_save.configure(text="NOT SAVED")
        else:
            self.label_save.configure(text="")


if __name__ == "__main__":
    app = App()
    app.mainloop()