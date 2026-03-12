# ui_app.py
# Battleship Project - Tkinter app + screen manager
# Created: 2026-02-06

import tkinter as tk  # Tkinter GUI framework
from tkinter import filedialog, messagebox, ttk  # File picker + simple alerts
from app.app_models import GameState  # Shared game state object
from app.ui_screen import WelcomeScreen, PlacementScreen, BattleScreen, WinScreen  # All screen classes
from PIL import Image, ImageTk  # Pillow library for image handling (if needed for UI)
from pathlib import Path  # For file path handling


'''
This file defines the main Tkinter application class, App, which acts as the screen manager. 
It creates the root window, initializes the shared GameState, and loads all screens (WelcomeScreen, PlacementScreen, and BattleScreen) 
into a single container frame. The app controls which screen is visible using tkraise(), allowing smooth screen transitions without destroying widgets. 
It also configures fullscreen behavior and provides a single place for screens to access shared state.
'''

class App(tk.Tk):  # Main application window inherits from Tk
    def __init__(self):
        super().__init__()  # Initialize Tk base class
        self.title("Battleship")  # Set window title
        self.state = GameState()  # Create shared game state object

        # Make text larger across the app by default.
        self.option_add("*Font", ("Arial", 16))
        style = ttk.Style(self)
        style.configure("TCombobox", font=("Arial", 16))

        # --- Wallpaper / background setup ---
        self._bg_original = None      # PIL.Image (original)
        self._bg_photo = None         # ImageTk.PhotoImage (resized)
        self._bg_label = tk.Label(self, bd=0)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._on_resize)  # auto-resize wallpaper when window changes

        # Container frame to hold all screens (kept above wallpaper)
        self._container = tk.Frame(self, bg="")
        self._container.pack(fill="both", expand=True)  # Make container fill window
        self._container.lift()  # keep screens above the wallpaper

        self._container.grid_rowconfigure(0, weight=1)  # Allow vertical expansion
        self._container.grid_columnconfigure(0, weight=1)  # Allow horizontal expansion

        self.screens = {}  # Dictionary to store screen instances

        # Create and register each screen
        for Screen in (WelcomeScreen, PlacementScreen, BattleScreen, WinScreen):
            self._add_screen(Screen)

        self.show_screen("WelcomeScreen")  # Show welcome screen first

        self.attributes("-fullscreen", True)  # Start in fullscreen mode
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))  # ESC exits fullscreen

        # Wallpaper picker: Cmd/Ctrl+O to choose an image
        self.bind_all("<Command-o>", lambda e: self.choose_wallpaper())
        self.bind_all("<Control-o>", lambda e: self.choose_wallpaper())

        # Optional menu (works even in fullscreen on some platforms)
        menubar = tk.Menu(self)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Choose Wallpaper…", command=self.choose_wallpaper)
        view_menu.add_command(label="Clear Wallpaper", command=self.clear_wallpaper)
        menubar.add_cascade(label="View", menu=view_menu)
        self.config(menu=menubar)

        # Try to load a default wallpaper if it exists in the project root
        default_wallpaper = "assets/HD-wallpaper-battleship-oceans-clouds-sea.jpg"
        try:
            self.set_wallpaper(default_wallpaper)
        except Exception:
            pass

    def _add_screen(self, ScreenClass):
        screen = ScreenClass(parent=self._container, app=self)  # Create screen instance
        self.screens[ScreenClass.__name__] = screen  # Store by class name
        screen.grid(row=0, column=0, sticky="nsew")  # Stack screens on top of each other

    def show_screen(self, name: str):
        self.screens[name].tkraise()  # Bring selected screen to the front

    def new_game(self):
        n = self.state.num_ships  # Remember selected ship count

        self.state.reset_for_new_game()  # Reset all boards, hits, shots, turns

        self.state.num_ships = n  # Restore ship count

        # Reset placement phase variables
        self.state.placing_player = 1       # Player 1 starts placement again
        self.state.placing_orientation = "H"  # Default orientation
        self.state.placing_ship_len = 1     # First ship size starts at 1

        self.show_screen("WelcomeScreen")  # Return to welcome screen

    def choose_wallpaper(self):
        """Open a file picker so the user can choose a wallpaper image."""
        path = filedialog.askopenfilename(
            title="Choose a wallpaper image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            self.set_wallpaper(path)
        except Exception as e:
            messagebox.showerror("Wallpaper Error", f"Could not load that image.\n\n{e}")

    def set_wallpaper(self, path: str):
        """Load wallpaper from a path.

        - Absolute paths (from the file picker) work as-is.
        - Relative paths (repo assets like 'assets/..') resolve from the project root.
        """
        p = Path(path)

        # If a relative path is provided, resolve it from the project root (Battleship/)
        if not p.is_absolute():
            project_root = Path(__file__).resolve().parents[1]  # .../Battleship/
            p = project_root / p

        img = Image.open(p)
        self._bg_original = img
        self._render_wallpaper()

    def clear_wallpaper(self):
        """Remove the wallpaper."""
        self._bg_original = None
        self._bg_photo = None
        self._bg_label.config(image="")

    def _on_resize(self, event):
        # Avoid doing work before an image is loaded
        if self._bg_original is None:
            return
        # Only respond to root window resize events
        if event.widget is not self:
            return
        self._render_wallpaper()

    def _render_wallpaper(self):
        """Resize the original wallpaper to the current window size and apply it."""
        if self._bg_original is None:
            return

        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())

        # Use high-quality resizing
        resized = self._bg_original.resize((w, h), Image.LANCZOS)
        self._bg_photo = ImageTk.PhotoImage(resized)
        self._bg_label.config(image=self._bg_photo)
        self._bg_label.lower()         # keep it behind
        self._container.lift()         # keep screens above

        welcome = self.screens.get("WelcomeScreen")
        if welcome and hasattr(welcome, "refresh_wallpaper"):
            welcome.refresh_wallpaper()
