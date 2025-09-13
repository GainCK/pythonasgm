import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk  # use to setup the picture
import json
import webbrowser
import os
import re

# ================== Note Data Classes ================== #

class Note:
    """
    Represents a single note object.
    Each note has:
      - title (string)
      - content blocks (text, images, links)
      - tags (list of labels for categorization)
      - links (list of external references/URLs)
    """

    def __init__(self, title):
        """
        Initialize a note with a given title.
        Content blocks, tags, and links are initialized as empty lists.
        """
        self._title = title   # Note title (private)
        self._content_blocks = []  # Stores text, images, links in structured format
        self._tags = []  # Stores tags for categorization
        self._link = []  # Stores note-specific links

    # ===== Encapsulation: getter and setter methods ===== #

    def get_title(self):
        """Return the note title."""
        return self._title
    
    def set_title(self, title):
        """Update the note title."""
        self._title = title

    def get_content_blocks(self):
        """Return all content blocks (text, images, links)."""
        return self._content_blocks

    def set_content_blocks(self, blocks):
        """Update content blocks for the note."""
        self._content_blocks = blocks

    def get_tags(self):
        """Return the list of tags associated with the note."""
        return self._tags

    def set_tags(self, tags):
        """Update the note's tags."""
        self._tags = tags

    def get_link(self):
        """Return stored links for the note."""
        return self._link

    def set_link(self, link):
        """Update the note's links."""
        self._link = link

    # ===== Polymorphism support (serialization) ===== #
    def to_dict(self):
        """
        Convert note object into a dictionary for JSON storage.
        Includes title, content blocks, tags, and links.
        """
        return {
            "type": "note",
            "title": self._title,
            "content_blocks": self._content_blocks,
            "tags": self._tags,
            "link": self._link
        }

    @staticmethod
    def from_dict(data):
        """
        Create a Note object from dictionary data (deserialization).
        Ensures backward compatibility with missing fields.
        """
        n = Note(data.get("title", ""))
        n.set_content_blocks(data.get("content_blocks", []))
        n.set_tags(data.get("tags", []))
        n.set_link(data.get("link", []))   
        return n


class NoteApp:
    """
    Main application class for the NoteApp.
    Handles:
      - Initialization of the Tkinter root window
      - Folder and note data management
      - File persistence (loading/saving notes)
      - Frame switching between Folder, Note, and Editor views
    """

    def __init__(self):
        """
        Initialize the NoteApp:
          - Creates Tkinter root window
          - Loads stored data from file (if available)
          - Sets up frames for folder, note, and editor
          - Starts the main Tkinter event loop
        """
        self.root = tk.Tk()
        self.root.title("Note APP")
        self.root.geometry("500x700")

        # Private-like attributes (encapsulation applied via getters/setters)
        self._folders = {}  # Stores folders and their notes
        self._current_folder = None  # Tracks currently selected folder
        self._current_note_index = None  # Tracks index of selected note

        # Load data from file on startup
        self.load_from_file()

        # Frame setup (three main screens of the app)
        self.folder_frame = FolderFrame(self.root, self)   # Folder selection UI
        self.editor_frame = EditorFrame(self.root, self)   # Note editor UI
        self.note_frame = NoteFrame(self.root, self)       # Notes list UI

        # Start with folder view
        self.show_folder_frame()

        # Run the Tkinter event loop
        self.root.mainloop()

    # ===== Getter / Setter methods (Encapsulation) ===== #

    def get_folders(self):
        """Return all folders with their notes."""
        return self._folders

    def set_folders(self, folders):
        """Update the folder collection."""
        self._folders = folders

    def get_current_folder(self):
        """Return the currently selected folder name."""
        return self._current_folder

    def set_current_folder(self, folder):
        """Set the currently selected folder name."""
        self._current_folder = folder

    def get_current_note_index(self):
        """Return the index of the currently selected note."""
        return self._current_note_index

    def set_current_note_index(self, index):
        """Set the index of the currently selected note."""
        self._current_note_index = index

    # ================== File handling ================== #

    def load_from_file(self):
        """
        Load data from 'notes_data.json'.
        - Deserializes saved notes into Note objects.
        - Handles file corruption with error message.
        """
        if os.path.exists("notes_data.json"):
            try:
                with open("notes_data.json", "r") as file:
                    raw_data = json.load(file)
                    # Reconstruct folders and notes from saved JSON
                    self._folders = {
                        folder: [Note.from_dict(note) for note in notes]
                        for folder, notes in raw_data.items()
                    }
            except json.JSONDecodeError:
                # Handle corrupted JSON file gracefully
                messagebox.showerror("Error", "Failed to load data. The file may be corrupted.")
                self.folders = {}

    def save_to_file(self):
        """
        Save notes data into 'notes_data.json'.
        - Converts Note objects into dictionary form for JSON.
        - Handles file I/O errors gracefully.
        """
        try: 
            with open("notes_data.json", "w") as file:
                # Convert notes into serializable dict format
                folders_to_save = {
                    folder: [note.to_dict() for note in notes]
                    for folder, notes in self._folders.items()
                }
                json.dump(folders_to_save, file, indent=4)
        except (OSError, PermissionError) as e:
            # Handle write permission issues or OS errors
            messagebox.showerror("Error", f"Failed to save notes: {e}")

    # ================ Frame switching ================= #

    def show_folder_frame(self):
        """
        Switch to the folder frame.
        - Displays list of folders
        - Refreshes folder display
        """
        self.root.config(menu=self.folder_frame.menubar)  # Use folder menu
        self.note_frame.hide()
        self.editor_frame.hide()
        self.folder_frame.show()
        self.folder_frame.refresh_folder_list()

    def show_note_frame(self):
        """
        Switch to the note frame of the current folder.
        - Displays notes belonging to the selected folder
        - Updates folder title in UI
        """
        self.root.config(menu="")  # Remove menu bar in note view
        self.note_frame.show()
        self.editor_frame.hide()
        self.folder_frame.hide()
        
        # Update folder title display if available
        if self.get_current_folder():
            self.note_frame.note_title_label.config(text=f"📂 {self.get_current_folder()}")
        
        # Ensure folder list stays updated
        self.folder_frame.refresh_folder_list()

    def show_editor_frame(self):
        """
        Switch to the editor frame.
        - Enables editing of the selected note
        - Updates back button with folder name for easy navigation
        """
        self.folder_frame.hide()
        self.note_frame.hide()
        self.editor_frame.show()
        self.editor_frame.back_btn_editor.config(text=f"← {self.get_current_folder()}")


# ==================== Base Frame ======================= #

class BaseFrame(tk.Frame):
    """
    BaseFrame class (inherits from tk.Frame).
    Provides common functionality for all UI frames in the NoteApp.
    Includes:
      - Reference to the main application
      - Methods to show or hide the frame consistently
    """

    def __init__(self, parent, app):
        """
        Initialize the base frame.
        :param parent: The parent Tkinter widget (root or container).
        :param app: Reference to the NoteApp instance.
        """
        super().__init__(parent)
        self.app = app  # Store reference to main app for communication

    def show(self):
        """
        Display this frame on the window.
        Uses pack() with full expansion to fill available space.
        """
        self.pack(fill="both", expand=True)

    def hide(self):
        """
        Hide this frame from the window.
        Uses pack_forget() to temporarily remove from view.
        """
        self.pack_forget()

#==================== Folder Frame =======================#

class FolderFrame(BaseFrame):
    """Folder management screen. Handles add, delete, search, and rename folders."""

    def __init__(self, parent, app):
        super().__init__(parent, app)

        # Title
        self.folder_title_label = tk.Label(self, text="📂 Folders", font=("Arial", 14, "bold"))
        self.folder_title_label.pack(pady=(10, 5))

        # Menu bar (Add/Delete folder options)
        self.menubar = tk.Menu(self.app.root)
        self.menubar.add_command(label="Add Folder", command=self.add_folder)
        self.menubar.add_command(label="Delete Folder", command=self.delete_folder)
        self.app.root.config(menu=self.menubar) 

        # Top frame (search bar + button)
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="both")
        self.top_frame.columnconfigure(0, weight=1) 

        self.search_entry = tk.Entry(self.top_frame, font=('Arial', 10))
        self.search_entry.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.search_folder())  # real-time search
        self.search_button = tk.Button(self.top_frame, text="Search", command=self.search_folder)
        self.search_button.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=5)

        # Folder list
        self.folder_listbox = tk.Listbox(self, font=('Arial', 10))
        self.folder_listbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.folder_listbox.bind("<Double-Button-1>", self.enter_folder)  # open folder

        # Right-click menu (Rename/Delete)
        self.folder_menu = tk.Menu(self.folder_listbox, tearoff=0)
        self.folder_menu.add_command(label="Rename Folder", command=self.rename_folder) 
        self.folder_menu.add_command(label="Delete Folder", command=self.delete_folder)
        self.folder_listbox.bind("<Button-3>", self.show_folder_menu)

    def rename_folder(self):
        """Rename selected folder."""
        selection = self.folder_listbox.curselection()
        if not selection:
            return
        old_name = self.folder_listbox.get(selection[0])
        new_name = simpledialog.askstring("Rename Folder", "Enter new name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            folders = self.app.get_folders()
            if new_name in folders:
                messagebox.showerror("Error", "Folder name already exists!")
                return
            # Move notes to new folder name
            folders[new_name] = folders.pop(old_name)
            self.app.set_folders(folders)
            self.app.save_to_file()
            self.refresh_folder_list()

    def show_folder_menu(self, event):
        """Show right-click menu for folder actions."""
        try:
            index = self.folder_listbox.nearest(event.y)
            self.folder_listbox.selection_clear(0, tk.END)
            self.folder_listbox.selection_set(index)
            self.folder_listbox.activate(index)
            self.folder_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.folder_menu.grab_release()

    def delete_folder(self):
        """Delete selected folder with confirmation."""
        selection = self.folder_listbox.curselection()
        if not selection:
            messagebox.showwarning("Delete Folder", "Please select a folder to delete.")
            return
        
        folder_name = self.folder_listbox.get(selection[0])
        confirm = messagebox.askyesno("Confirm Delete", f"Delete folder '{folder_name}' and all its notes?")
        if confirm:
            folders = self.app.get_folders()
            del folders[folder_name]
            self.app.set_folders(folders)
            self.app.save_to_file()
            self.refresh_folder_list()

    def add_folder(self):
        """Add new folder (with validation)."""
        folderName = simpledialog.askstring("New Folder", "Folder Name: ", parent=self.app.root)
        if not folderName or not folderName.strip():
            messagebox.showwarning("Warning", "Folder name cannot be empty.")
            return
        folderName = folderName.strip()

        folders = self.app.get_folders()
        if folderName in folders:
            messagebox.showerror("Error", "Folder name already exists!")
            return
        
        folders[folderName] = []  # create empty folder
        self.app.set_folders(folders)
        self.refresh_folder_list()
        self.app.save_to_file()

    def refresh_folder_list(self, folders=None):
        """Update folder listbox display."""
        self.folder_listbox.delete(0, tk.END)
        show_folders = folders if folders is not None else self.app.get_folders()
        for folder in show_folders:
            self.folder_listbox.insert(tk.END, folder)

    def search_folder(self):
        """Search folder by keyword (real-time)."""
        keyword = self.search_entry.get().strip()
        folders = self.app.get_folders()
        if not keyword:
            self.refresh_folder_list()
            return
        result = [f for f in folders if keyword.lower() in f.lower()]
        self.refresh_folder_list(result)

    def enter_folder(self, event):
        """Enter selected folder and show its notes."""
        selection = self.folder_listbox.curselection()
        if selection:
            folder_name = self.folder_listbox.get(selection[0])
            self.app.set_current_folder(folder_name)
            self.app.note_frame.refresh_note_list()
            self.app.show_note_frame()


# ==================== Note Frame ======================= #

class NoteFrame(BaseFrame):
    """Screen for managing notes inside a folder (add, delete, search, open)."""

    def __init__(self, parent, app):
        super().__init__(parent, app)

        # Title (folder name shown here)
        self.note_title_label = tk.Label(self, text="", font=("Arial", 14, "bold"))
        self.note_title_label.pack(pady=(5, 0))

        # Top section with buttons and search
        self.top_note = tk.Frame(self)
        self.top_note.pack(fill="x")
        self.top_note.columnconfigure(0, weight=1)

        # Back button
        self.back_btn = tk.Button(self.top_note, text="← Folders", command=self.app.show_folder_frame)
        self.back_btn.grid(row=0, column=0, sticky="w", padx=(10, 5))

        # Add note button
        self.add_note = tk.Button(self.top_note, text="Add Note", command=self.add_note)
        self.add_note.grid(row=0, column=0, sticky="e", padx=(5, 0))

        # Delete note button  
        self.delete_note_btn = tk.Button(self.top_note, text="Delete Note", command=self.delete_note)
        self.delete_note_btn.grid(row=0, column=1, sticky="e", padx=(5, 10))

        # Search bar and button
        self.search_entry_note = tk.Entry(self.top_note, font=('Arial', 10))
        self.search_entry_note.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(10, 5))
        self.search_entry_note.bind("<KeyRelease>", lambda event: self.search_note())  # real-time search

        self.search_button_note = tk.Button(self.top_note, text="Search", command=self.search_note)
        self.search_button_note.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))

        # List of notes
        self.note_list = tk.Listbox(self, font=('Arial', 10))
        self.note_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.note_list.bind("<Double-Button-1>", self.app.editor_frame.open_note_editor)  # open note editor

        # Right-click menu
        self.note_menu = tk.Menu(self.note_list, tearoff=0)
        self.note_menu.add_command(label="Delete Note", command=self.delete_note)
        self.note_list.bind("<Button-3>", self.show_note_menu)

    def show_note_menu(self, event):
        """Show right-click menu for note actions."""
        try:
            index = self.note_list.nearest(event.y)
            self.note_list.selection_clear(0, tk.END)
            self.note_list.selection_set(index)
            self.note_list.activate(index)
            self.note_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.note_menu.grab_release()

    def delete_note(self):
        """Delete selected note with confirmation."""
        selection = self.note_list.curselection()
        if not selection:
            messagebox.showwarning("Delete Note", "Please select a note to delete.")
            return
    
        index = selection[0]
        current_folder = self.app.get_current_folder()
        folders = self.app.get_folders()
        note = folders[current_folder][index]

        confirm = messagebox.askyesno("Confirm Delete", f"Delete note '{note.get_title()}'?")
        if confirm:
            del folders[current_folder][index]
            self.app.set_folders(folders)
            self.app.save_to_file()
            self.refresh_note_list()

    def add_note(self):
        """Add a new note to the current folder."""
        current_folder = self.app.get_current_folder()
        note_title = simpledialog.askstring("New Note", f"Note for {current_folder}:", parent=self.app.root)
        if note_title:
            folders = self.app.get_folders()
            new_note = Note(note_title) 
            folders[current_folder].append(new_note)
            self.app.set_folders(folders)
            self.refresh_note_list()
            self.app.save_to_file()

    def refresh_note_list(self, notes=None, highlight_keyword=None):
        """Refresh note list. Optionally highlight search results."""
        self.note_list.delete(0, tk.END)
        current_folder = self.app.get_current_folder()
        if not current_folder:
            return
        
        folders = self.app.get_folders()
        notes_to_show = notes if notes is not None else folders.get(current_folder, [])
        
        for i, note in enumerate(notes_to_show):
            tags_text = f" [{'] ['.join(note.get_tags())}]" if note.get_tags() else ""
            display_text = f"{note.get_title()}{tags_text}"
            self.note_list.insert(tk.END, display_text)

            # Reset background color
            self.note_list.itemconfig(i, {'bg': 'SystemWindow'})

            # Highlight if matches keyword
            if highlight_keyword and highlight_keyword.lower() in display_text.lower():
                self.note_list.itemconfig(i, {'bg': 'yellow'})

    def search_note(self):
        """Search notes by title or tags."""
        keyword = self.search_entry_note.get().strip().lower()
        current_folder = self.app.get_current_folder()
        if not keyword:
            self.refresh_note_list()
            return
        
        folders = self.app.get_folders()
        all_note = folders.get(current_folder, [])
        result = [note for note in all_note if keyword in note.get_title().lower() or any(keyword in t.lower() for t in note.get_tags())]
        self.refresh_note_list(result, highlight_keyword=keyword)

                    
# ==================== Editor Frame ==================== #
class EditorFrame(BaseFrame):
    """
    Screen for creating and editing notes.
    Allows user to add text, images, links, and tags.
    """

    def __init__(self, parent, app):
        super().__init__(parent, app)

        self.tags = []  # store tags for current note

        # ===== Top control bar ===== #
        self.top_editor_frame = tk.Frame(self)
        self.top_editor_frame.pack(fill="both", pady=(10, 0))

        # Back to note list
        self.back_btn_editor = tk.Button(self.top_editor_frame, text="", command=self.app.show_note_frame)
        self.back_btn_editor.pack(side="left", padx=(10, 0))

        # Save button
        self.save_btn = tk.Button(self.top_editor_frame, text="Save", command=self.save_note_content)
        self.save_btn.pack(side="right", padx=(0, 10))

        # Manage tags
        self.tag_btn = tk.Button(self.top_editor_frame, text="Add Tags", command=self.edit_tags)
        self.tag_btn.pack(side="left", anchor="w", padx=(10, 0), pady=(5, 5))

        # Attach image button
        self.attach_image_btn = tk.Button(self.top_editor_frame, text="Attach Image", command=self.attach_image)
        self.attach_image_btn.pack(side="left", padx=(10, 5))

        # ===== Title section ===== #
        title_frame = tk.Frame(self)
        title_frame.pack(fill="x", padx=10, pady=(5, 5))

        title_label = tk.Label(title_frame, text="Title:")
        title_label.pack(side="left", padx=(0, 5))

        # Note title field
        self.note_title_var = tk.StringVar()
        self.title_entry = tk.Entry(title_frame, textvariable=self.note_title_var, font=('Arial', 12, 'bold'))
        self.title_entry.pack(side="left", fill="x", expand=True)

        # ===== Main text editor ===== #
        self.note_text = tk.Text(self, wrap="word", font=('Arial', 11))
        self.note_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Style links inside text
        self.note_text.tag_config("link", foreground="blue", underline=True)
        self.note_text.tag_bind("link", "<Button-1>", self._on_link_click)

        # Detect links automatically when typing
        self.note_text.bind("<<Modified>>", self._detect_links)

    def edit_tags(self):
        """Open dialog to add/edit tags for the note."""
        current_tags = ", ".join(self.tags) if self.tags else ""
        result = simpledialog.askstring("Add Tags", "Enter tags (comma separated):", initialvalue=current_tags)
        if result is not None:
            self.tags = [tag.strip() for tag in result.split(",") if tag.strip()]
            self.tag_btn.config(text=f"Add Tags ({len(self.tags)})")

    def attach_image(self):
        """Attach an image into the note."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if not file_path:
            return
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Invalid image file or path.")
            return

        try:
            # Open and resize image
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return

        # Keep reference so image is not lost
        if not hasattr(self.note_text, "image_refs"):
            self.note_text.image_refs = []
        self.note_text.image_refs.append(photo)

        # Save image path for persistence
        if not hasattr(self.note_text, "image_name_to_path"):
            self.note_text.image_name_to_path = {}
        self.note_text.image_name_to_path[str(photo)] = file_path

        # Insert image at cursor position
        self.note_text.image_create(tk.INSERT, image=photo)

    def _detect_links(self, event=None):
        """Scan text for URLs and highlight them as clickable links."""
        self.note_text.tag_remove("link", "1.0", tk.END)
        url_pattern = re.compile(r"https?://[^\s]+")

        line_index = 1
        while True:
            line_start = f"{line_index}.0"
            line_end = f"{line_index}.end"
            if self.note_text.compare(line_start, ">=", tk.END):
                break

            line_text = self.note_text.get(line_start, line_end)
            for match in url_pattern.finditer(line_text):
                start = f"{line_index}.{match.start()}"
                end = f"{line_index}.{match.end()}"
                self.note_text.tag_add("link", start, end)

            line_index += 1

        # Reset modified flag
        self.note_text.edit_modified(False)

    def _on_link_click(self, event):
        """Open clicked link in default browser."""
        index = self.note_text.index(f"@{event.x},{event.y}")
        ranges = self.note_text.tag_prevrange("link", index + "+1c")
        if ranges:
            url = self.note_text.get(ranges[0], ranges[1])
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open link: {e}")

    def open_note_editor(self, event):
        """Open selected note and load content into editor."""
        selection = self.app.note_frame.note_list.curselection()
        if not selection:
            return

        index = selection[0]
        self.app.set_current_note_index(index)

        current_folder = self.app.get_current_folder()
        folders = self.app.get_folders()
        note = folders[current_folder][index]

        # Switch to editor view
        self.app.show_editor_frame()

        # Load title and clear text area
        self.note_title_var.set(note.get_title())
        self.note_text.delete("1.0", tk.END)

        # Prepare for images
        self.note_text.image_refs = []
        self.note_text.image_name_to_path = {}

        # Load note content blocks
        for block in note.get_content_blocks():
            if block['type'] == "text":
                self.note_text.insert(tk.END, block['content'])

            elif block['type'] == "image":
                if os.path.exists(block['path']):
                    try:
                        img = Image.open(block['path'])
                        img.thumbnail((300, 300))
                        photo = ImageTk.PhotoImage(img)
                        self.note_text.image_refs.append(photo)
                        self.note_text.image_name_to_path[str(photo)] = block['path']
                        self.note_text.image_create(tk.END, image=photo)
                    except Exception as e:
                        self.note_text.insert(tk.END, f"[Error loading image: {e}]")
                else:
                    self.note_text.insert(tk.END, f"[Image not found: {block['path']}]")

            elif block['type'] == "link":
                self.link = note.get_link()
                start_index = self.note_text.index(tk.END)
                self.note_text.insert(tk.END, self.link)
                end_index = self.note_text.index(tk.END)
                self.note_text.tag_add("link", start_index, end_index)
                self.note_text.tag_bind("link", "<Button-1>", self._on_link_click)

        # Load tags
        self.tags = note.get_tags()
        self.tag_btn.config(text=f"Add Tags ({len(self.tags)})" if self.tags else "Add Tags")
        
        # Highlight links
        self._detect_links()

    def save_note_content(self):
        """Save the edited note (title, text, images, links, tags)."""
        current_folder = self.app.get_current_folder()
        current_note_index = self.app.get_current_note_index()
        if current_folder is None or current_note_index is None:
            return

        folders = self.app.get_folders()
        note = folders[current_folder][current_note_index]
        note.set_title(self.note_title_var.get())

        if isinstance(note, Note):
            blocks = []
            # Dump text widget into structured content blocks
            for kind, value, index in self.note_text.dump("1.0", "end-1c", text=True, image=True, tag=True):
                if kind == "text" and value:
                    blocks.append({"type": "text", "content": value})
                elif kind == "image":
                    path = getattr(self.note_text, "image_name_to_path", {}).get(value)
                    if path:
                        blocks.append({"type": "image", "path": path})
                elif kind == "tagon" and value == "link":
                    url = self.note_text.get(index, f"{index} lineend").strip()
                    if url.startswith("http"):
                        blocks.append({"type": "link", "url": url})

        # Save content and tags
        note.set_content_blocks(blocks)
        self.app.set_folders(folders)
        note.set_tags(self.tags)
        self.app.save_to_file()
        self.app.note_frame.refresh_note_list()
        self.app.show_note_frame()


NoteApp()