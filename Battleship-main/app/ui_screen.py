# ui_screen.py
# Battleship Project - UI screens
# Created: 2026-02-06

'''
This is the largest and most important UI file, containing all three game screens and nearly all player interaction.

WelcomeScreen lets the user choose how many ships to play with and initializes the game state accordingly.

PlacementScreen handles ship placement for both players, enforcing turn order, ship sizes, orientation toggling, overlap rules, and allowing ships to be removed by clicking them again.

BattleScreen manages the actual gameplay: selecting targets, firing shots, displaying hits/misses/sinks, switching turns with a delay, updating the scoreboard, and detecting win conditions.

This file focuses on UI behavior and flow, while delegating rule enforcement (hits, sinks, remaining ships) to the game.rules module

'''

import tkinter as tk
from tkinter import ttk, messagebox
from game.rules import fire_shot, ships_remaining, ship_hit_counters, UNKNOWN, MISS, HIT
from game.coords import col_to_letter, row_to_number


MIN_SHIPS = 1
MAX_SHIPS = 5
GRID_SIZE = 10

ACTIVE_BG = "#ffffff"
COVER_BG = "#2b2b2b"

P1_SHIP_BG = "#2ecc71"
P2_SHIP_BG = "#e67e22"

MISS_BG = "#95a5a6"
HIT_BG = "#c0392b"

HIGHLIGHT_BG = "#f1c40f"
TURN_DELAY_MS = 3000


class WelcomeScreen(tk.Frame):  # Screen 1: pick number of ships, then move to placement
    def __init__(self, parent, app):
        super().__init__(parent)  # Initialize Tkinter Frame base class
        self.app = app  # Store reference to the main App (lets us access state + screen switching)

        self.bg_label = tk.Label(self, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.refresh_wallpaper()

        inner = tk.Frame(self)  # Inner frame holding the actual widgets
        inner.place(relx=0.5, rely=0.45, anchor="center")  # Center-ish placement on screen

        tk.Label(inner, text="Battleship", font=("Arial", 62, "bold")).pack(pady=(0, 18))  # Big title
        tk.Label(inner, text="Choose how many ships you want (1–5)", font=("Arial", 18)).pack(pady=(0, 12))  # Subtitle

        self.choice_var = tk.IntVar(value=MIN_SHIPS)  # Stores the selected number of ships (default = 1)

        row = tk.Frame(inner)  # Row container for label + dropdown
        row.pack(pady=(0, 12))  # Add spacing under it
        tk.Label(row, text="Ships:", font=("Arial", 18)).pack(side="left", padx=8)  # Label next to dropdown

        ttk.Combobox(  # Dropdown for ship count selection
            row,
            textvariable=self.choice_var,  # Connected to choice_var so we can read selected value
            values=list(range(MIN_SHIPS, MAX_SHIPS + 1)),  # Options [1..5]
            state="readonly",  # User must pick from list (no typing random values)
            width=5,  # Visual width of dropdown
            justify="center",  # Center the selected value text
        ).pack(side="left")  # Place dropdown next to the label

        tk.Label(  # Small explanation text about ship sizes
            inner,
            text="Ship sizes are based on this number.\nExample: 3 ships means 1x1, 1x2, 1x3.",
            font=("Arial", 14),
            fg="#444",  # Gray text color
            justify="center",  # Center align multi-line text
        ).pack(pady=(0, 18))  # Add spacing below text

        tk.Button(inner, text="Continue →", width=18, font=("Arial", 16, "bold"), command=self.on_continue).pack()  # Button that triggers on_continue()

    def tkraise(self, aboveThis=None):
        self.refresh_wallpaper()
        super().tkraise(aboveThis)

    def refresh_wallpaper(self):
        photo = getattr(self.app, "_bg_photo", None)
        self.bg_label.config(image=photo if photo else "", bg="#0b1f33")
        self.bg_label.image = photo
        self.bg_label.lower()

    def on_continue(self):
        n = int(self.choice_var.get())  # Read selected ship count from dropdown variable

        if not (MIN_SHIPS <= n <= MAX_SHIPS):  # Safety check (should always pass due to readonly combobox)
            messagebox.showerror("Invalid", "Pick a number from 1 to 5.")  # Show error popup
            return  # Stop if invalid

        self.app.state.reset_for_new_game()  # Clear old boards/ships/hits/turns (fresh start)
        self.app.state.num_ships = n  # Save ship count into shared GameState
        self.app.show_screen("PlacementScreen")  # Go to placement phase


class PlacementScreen(tk.Frame):  # Screen 2: both players place ships before battle
    """
    Two 10x10 grids:
    - Left = Player 1 placement
    - Right = Player 2 placement

    Player 1 places first, clicks Ready.
    Player 2 places next, clicks Ready.
    Then we move to BattleScreen (placeholder for now).
    """

    def __init__(self, parent, app):
        super().__init__(parent)  # Initialize Tkinter Frame base class
        self.app = app  # Store reference to the main App (state + screen switching)

        root = tk.Frame(self)  # Root container for this screen
        root.pack(fill="both", expand=True, padx=30, pady=20)  # Fill screen with padding

        top = tk.Frame(root)  # Top bar container (status + buttons)
        top.pack(fill="x", pady=(0, 15))  # Stretch horizontally + spacing below

        self.status_lbl = tk.Label(top, text="", font=("Arial", 22, "bold"))  # Shows placement instructions
        self.status_lbl.pack(side="left")  # Align left

        self.orient_btn = tk.Button(  # Button to toggle horizontal/vertical placement
            top,
            text="Toggle (H)",  # Default orientation display
            command=self.toggle_orientation,  # Calls toggle function
            width=14,  # Button width
        )
        self.orient_btn.pack(side="left", padx=(20, 0))  # Place next to status label

        self.ready_btn = tk.Button(  # Button to finish current player's placement
            top,
            text="Ready",
            command=self.on_ready,  # Calls ready handler
            width=12,
        )
        self.ready_btn.pack(side="right")  # Align right

        boards = tk.Frame(root)  # Container holding both player grids
        boards.pack(fill="both", expand=True)  # Let boards take remaining space

        # Player 1 panel (left side)
        p1_panel = tk.Frame(boards)  # Left panel container
        p1_panel.pack(side="left", fill="both", expand=True, padx=(0, 25))  # Left with spacing to middle
        tk.Label(p1_panel, text="Player 1", font=("Arial", 22, "bold")).pack(pady=(0, 10))  # Title label
        self.p1_grid = tk.Frame(p1_panel)  # Grid frame for Player 1 cells
        self.p1_grid.pack()  # Pack the grid frame

        # Player 2 panel (right side)
        p2_panel = tk.Frame(boards)  # Right panel container
        p2_panel.pack(side="left", fill="both", expand=True, padx=(25, 0))  # Right with spacing from middle
        tk.Label(p2_panel, text="Player 2", font=("Arial", 22, "bold")).pack(pady=(0, 10))  # Title label
        self.p2_grid = tk.Frame(p2_panel)  # Grid frame for Player 2 cells
        self.p2_grid.pack()  # Pack the grid frame

        self.p1_buttons = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]  # Store Player 1 cell widgets
        self.p2_buttons = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]  # Store Player 2 cell widgets

        self._make_grid(player=1)  # Build Player 1 grid widgets + bindings
        self._make_grid(player=2)  # Build Player 2 grid widgets + bindings

    def tkraise(self, aboveThis=None):
        # Re-enable buttons in case they were disabled in previous game
        self.ready_btn.config(state="normal")      # Allow pressing Ready again
        self.orient_btn.config(state="normal")     # Allow toggling orientation again

        self.refresh_ui()                          # Redraw board + update status text
        super().tkraise(aboveThis)                 # Bring this screen to front


    def _make_grid(self, player: int):
        frame = self.p1_grid if player == 1 else self.p2_grid  # Choose correct grid frame
        cells = self.p1_buttons if player == 1 else self.p2_buttons  # Choose correct button matrix

        tk.Label(frame, text="", width=4).grid(row=0, column=0)  # Top-left empty corner

        # Column headers (A–J)
        for c in range(GRID_SIZE):
            tk.Label(
                frame,
                text=col_to_letter(c),  # Convert column index to letter
                font=("Arial", 16, "bold")
            ).grid(row=0, column=c + 1)

        # Row headers + actual grid cells
        for r in range(GRID_SIZE):
            tk.Label(
                frame,
                text=row_to_number(r),  # Convert row index to 1–10
                font=("Arial", 16, "bold")
            ).grid(row=r + 1, column=0)

            for c in range(GRID_SIZE):
                cell = tk.Label(
                    frame,
                    text="",
                    width=6,
                    height=3,
                    bg=ACTIVE_BG,  # Default active color
                    relief="solid",
                    borderwidth=1,
                )
                cell.grid(row=r + 1, column=c + 1, padx=1, pady=1)

                # Click handler wrapper to preserve loop variables
                def handler(event, rr=r, cc=c, pp=player):
                    self.on_cell_click(pp, rr, cc)

                cell._click_handler = handler  # Store handler reference
                cell.bind("<Button-1>", cell._click_handler)  # Bind click event

                cells[r][c] = cell  # Save widget reference in matrix

    def toggle_orientation(self):
        s = self.app.state
        s.placing_orientation = "V" if s.placing_orientation == "H" else "H"
        self.orient_btn.config(text=f"Toggle ({s.placing_orientation})")
        self.refresh_ui()

    def on_cell_click(self, player: int, row: int, col: int):
        s = self.app.state

        if player != s.placing_player:  # Prevent clicking wrong player's board
            return

        if s.num_ships is None:  # Safety check
            return

        board = self._board_for_player(player)  # Get correct board array
        ships_list = self._ships_list_for_player(player)  # Get correct ship list

        # If clicking an occupied cell → remove entire ship
        if board[row][col] == 1:
            for i, ship in enumerate(ships_list):
                if (row, col) in ship:
                    for rr, cc in ship:  # Clear all ship cells from board
                        board[rr][cc] = 0
                    ships_list.pop(i)  # Remove ship from list
                    self.refresh_ui()
                    return

        # Otherwise place the next required ship
        length = self._next_required_length(player)  # Determine which ship length is next

        if length > s.num_ships:  # All ships placed
            return

        orient = s.placing_orientation  # Current orientation

        if not self.can_place(board, row, col, length, orient):  # Validate placement
            messagebox.showerror("Invalid placement", "That ship doesn't fit there or overlaps another ship.")
            return

        coords = self.place_ship(board, row, col, length, orient)  # Place ship
        ships_list.append(coords)  # Add ship coordinates to state

        self.refresh_ui()


    def can_place(self, board, row, col, length, orient) -> bool:
        if orient == "H":
            if col + length - 1 >= GRID_SIZE:  # Right boundary check
                return False
            cells = [(row, col + i) for i in range(length)]
        else:
            if row + length - 1 >= GRID_SIZE:  # Bottom boundary check
                return False
            cells = [(row + i, col) for i in range(length)]

        return all(board[r][c] == 0 for r, c in cells)  # Overlap check


    def place_ship(self, board, row, col, length, orient):
        coords = []  # Will store ship coordinates

        if orient == "H":
            for i in range(length):
                board[row][col + i] = 1  # Mark board
                coords.append((row, col + i))  # Store coordinate
        else:
            for i in range(length):
                board[row + i][col] = 1
                coords.append((row + i, col))

        return coords  # Return full ship coordinate list


    def on_ready(self):
        s = self.app.state

        if s.num_ships is None:  # Safety check
            return

        ships_list = self._ships_list_for_player(s.placing_player)  # Get current player's ships

        # Ensure all required ships are placed
        if len(ships_list) < s.num_ships:
            remaining = s.num_ships - len(ships_list)
            messagebox.showinfo("Not ready", f"Place all ships first. Remaining: {remaining}")
            return

        if s.placing_player == 1:
            # Switch to Player 2 placement phase
            s.placing_player = 2
            s.placing_ship_len = 1  # Reset ship length tracker
            s.placing_orientation = "H"  # Reset orientation
            self.orient_btn.config(text="Toggle (H)")  # Reset button label
            self.refresh_ui()
            return

        # If Player 2 finished → short delay before battle phase
        self.status_lbl.config(text="All ships placed! Starting battle...")  # Show transition message

        self.ready_btn.config(state="disabled")   # Prevent double clicks during delay
        self.orient_btn.config(state="disabled")  # Prevent orientation toggling during delay

        # Hide both placement boards immediately so neither player can see the other's ships
        # (cover with dark background and disable interactions). This is for
        # local single-screen play so Player 1 cannot see Player 2's board after placement.
        self._render_board(self.p1_buttons, s.p1_board, show_ships=False,
                   ship_color=P1_SHIP_BG, covered=True)
        self._render_board(self.p2_buttons, s.p2_board, show_ships=False,
                   ship_color=P2_SHIP_BG, covered=True)

        # Disable clicks on both boards during the transition
        self._set_active(self.p1_buttons, active=False)
        self._set_active(self.p2_buttons, active=False)

        self.after(3000, lambda: self.app.show_screen("BattleScreen"))  # Wait 3 seconds, then switch
        return  # IMPORTANT: stop function here
    

    def refresh_ui(self):
        s = self.app.state

        if s.num_ships is None:
            self.status_lbl.config(text="Placement")
            return

        next_len = self._next_required_length(s.placing_player)  # Determine next ship length

        if next_len <= s.num_ships:
            self.status_lbl.config(
                text=f"Placement — Player {s.placing_player}: place ship length {next_len}"
            )
        else:
            self.status_lbl.config(
                text=f"Placement — Player {s.placing_player}: all ships placed. Click Ready."
            )

        # Determine which board is active
        p1_turn = (s.placing_player == 1)
        p2_turn = (s.placing_player == 2)

        # Render boards
        self._render_board(self.p1_buttons, s.p1_board, show_ships=True,
                           ship_color=P1_SHIP_BG, covered=not p1_turn)

        self._render_board(self.p2_buttons, s.p2_board, show_ships=True,
                           ship_color=P2_SHIP_BG, covered=not p2_turn)

        # Enable/disable click interaction per board
        self._set_active(self.p1_buttons, active=p1_turn)
        self._set_active(self.p2_buttons, active=p2_turn)


    def _render_board(self, cells, board, show_ships: bool, ship_color: str, covered: bool):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):

                if covered:  # Hide entire board when not player's turn
                    cells[r][c].config(bg=COVER_BG)
                    continue

                if board[r][c] == 1 and show_ships:
                    cells[r][c].config(bg=ship_color)  # Show ship color
                else:
                    cells[r][c].config(bg=ACTIVE_BG)  # Default empty cell color


    def _set_active(self, cells, active: bool):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if active:
                    cells[r][c].bind("<Button-1>", cells[r][c]._click_handler)  # Enable clicks
                else:
                    cells[r][c].unbind("<Button-1>")  # Disable clicks

                    
    def _ships_list_for_player(self, player: int):
        s = self.app.state
        return s.p1_ships if player == 1 else s.p2_ships  # Return correct ship list


    def _board_for_player(self, player: int):
        s = self.app.state
        return s.p1_board if player == 1 else s.p2_board  # Return correct board array


    def _next_required_length(self, player: int) -> int:
        s = self.app.state

        if s.num_ships is None:
            return 1

        placed_lengths = {len(ship) for ship in self._ships_list_for_player(player)}  # Set of placed ship sizes

        for L in range(1, s.num_ships + 1):  # Ships must be placed in order 1..N
            if L not in placed_lengths:
                return L

        return s.num_ships + 1  # All ships placed


class BattleScreen(tk.Frame):
    """
    Battle Phase:
    - Left: current player's own board (ships visible) + incoming marks (what opponent did to you)
    - Right: opponent board hidden except your shots (hit/miss shown)
    - Click selects a target cell (highlight only)
    - FIRE confirms the shot
    - Show big HIT/MISS/SINK, then switch turns after TURN_DELAY_MS
    - Scoreboard shows both players stats and ships remaining
    """

    def __init__(self, parent, app):
        super().__init__(parent)  # Initialize Tkinter Frame base class
        self.app = app  # Store reference to App (for state + screen switching)

        self.selected = None        # Stores selected target cell as (row, col)
        self.input_locked = False   # True while waiting during turn-delay / win-delay

        root = tk.Frame(self)  # Root container for this screen
        root.pack(fill="x", expand=True)  # Expand horizontally

        # Delay a bit then set wrap length based on current window width
        self.after(50, lambda: self.score_lbl.config(wraplength=self.winfo_width() - 80))

        header = tk.Frame(root)  # Header area (turn + result message)
        header.pack(fill="x", expand=True)

        self.turn_lbl = tk.Label(  # Shows "Player X's turn"
            header,
            text="",
            font=("Arial", 28, "bold"),
            anchor="center",
        )
        self.turn_lbl.pack(fill="x")

        self.result_lbl = tk.Label(  # Big feedback text: HIT / MISS / SINK / WINS
            header,
            text="",
            font=("Arial", 40, "bold"),
            anchor="center",
        )
        self.result_lbl.pack(fill="x", expand=True, pady=(10, 10))

        controls = tk.Frame(root)  # Row with FIRE button
        controls.pack(fill="x", pady=(0, 12))

        self.fire_btn = tk.Button(  # Confirm shot button
            controls,
            text="FIRE",
            font=("Arial", 24, "bold"),
            width=10,
            command=self.on_fire_pressed,  # Fires the currently selected cell
        )
        self.fire_btn.pack()

        boards = tk.Frame(root)  # Container holding two boards
        boards.pack(fill="both", expand=True)

        # Left panel: Own board
        left = tk.Frame(boards)  # Container for own board
        left.pack(side="left", expand=True, padx=(0, 25))
        self.left_title = tk.Label(left, text="Your Board", font=("Arial", 20, "bold"))  # Own board title
        self.left_title.pack(pady=(0, 8))
        self.own_grid = tk.Frame(left)  # Frame that holds the own board grid
        self.own_grid.pack()

        # Right panel: Target board
        right = tk.Frame(boards)  # Container for opponent board
        right.pack(side="left", expand=True, padx=(25, 0))
        self.right_title = tk.Label(right, text="Opponent Board", font=("Arial", 20, "bold"))  # Target title
        self.right_title.pack(pady=(0, 8))
        self.target_grid = tk.Frame(right)  # Frame holding target board grid
        self.target_grid.pack()

        # 2D matrices holding cell widgets
        self.own_cells = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]  # Own board widgets
        self.target_cells = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]  # Target board widgets

        self._make_grid(self.own_grid, self.own_cells, clickable=False)  # Build own board (no clicks)
        self._make_grid(self.target_grid, self.target_cells, clickable=True)  # Build target board (clickable)

        # Scoreboard label (shows both players stats)
        self.score_lbl = tk.Label(
            root,
            text="",
            font=("Arial", 20, "bold"),
            justify="center",
            anchor="center",
        )
        self.score_lbl.pack(pady=(14, 0), fill="x")  # Place scoreboard under boards

        # --- Shot blackout (used after a valid shot to briefly cover BOTH boards for hand-off) ---
        # Implemented by temporarily rendering both grids with COVER_BG (same idea as PlacementScreen).
        self._shot_blackout_active = False
        self._shot_blackout_job = None
        self._shot_blackout_hide_job = None


    def tkraise(self, aboveThis=None):
        # Reset per-game / per-entry UI state when this screen is shown
        self.selected = None  # Clear any previous selection
        self.input_locked = False  # Allow input again
        self.result_lbl.config(text="")  # Clear result text
        self.fire_btn.config(state="normal")  # Re-enable FIRE button
        self._cancel_shot_blackout()
        self._end_shot_blackout()

        self.refresh_ui()  # Re-render boards + scoreboard based on current GameState
        super().tkraise(aboveThis)  # Bring this screen to the front


    def _make_grid(self, frame, cells, clickable: bool):
        tk.Label(frame, text="", width=4).grid(row=0, column=0)  # Top-left empty corner (aligns headers)

        # Column headers A–J
        for c in range(GRID_SIZE):
            tk.Label(
                frame,
                text=col_to_letter(c),  # Convert column index to A–J
                font=("Arial", 16, "bold")
            ).grid(row=0, column=c + 1)  # +1 because col 0 is reserved for row labels

        # Row headers 1–10 + create grid cells
        for r in range(GRID_SIZE):
            tk.Label(
                frame,
                text=row_to_number(r),  # Convert row index to 1–10
                font=("Arial", 16, "bold")
            ).grid(row=r + 1, column=0)  # +1 because row 0 is reserved for column labels

            for c in range(GRID_SIZE):
                cell = tk.Label(
                    frame,
                    text="",
                    width=5,
                    height=2,
                    bg=ACTIVE_BG,  # Default background
                    relief="solid",
                    borderwidth=1,
                    font=("Arial", 20, "bold"),
                )
                cell.grid(row=r + 1, column=c + 1, padx=1, pady=1)  # Place cell widget

                if clickable:  # Only target grid should be clickable
                    def handler(event, rr=r, cc=c):
                        self.on_select(rr, cc)  # Save selection and refresh UI

                    cell._click_handler = handler  # Store handler so we can rebind later
                    cell.bind("<Button-1>", cell._click_handler)  # Bind click event

                cells[r][c] = cell  # Store the widget in the 2D matrix


    def on_select(self, row: int, col: int):
        if self.input_locked:  # Prevent selecting during turn switch delay / win delay
            return

        self.selected = (row, col)  # Store current target selection
        self.refresh_ui()  # Refresh to apply highlight on selected target cell

    def on_fire_pressed(self):
        if self.input_locked:  # Block firing while locked (during delay)
            return

        if self.selected is None:  # Must select a target before firing
            self.result_lbl.config(text="SELECT A CELL")
            return

        s = self.app.state  # Shortcut to shared GameState
        row, col = self.selected  # Target cell
        turn = s.current_turn  # Whose turn (1 or 2)

        # Choose attacker/defender structures based on current turn
        if turn == 1:
            attacker_shots = s.p1_shots  # What P1 has fired at P2 (public marks)
            defender_incoming = s.p2_incoming  # What P2 has received from P1 (for P2 own-board view)
            defender_ships = s.p2_ships  # P2 ship coordinate lists
            defender_hits = s.p2_hits  # P2 hit set
            winner_num = 1  # If defender loses all ships, attacker is player 1
        else:
            attacker_shots = s.p2_shots  # What P2 has fired at P1
            defender_incoming = s.p1_incoming  # What P1 has received from P2
            defender_ships = s.p1_ships  # P1 ships
            defender_hits = s.p1_hits  # P1 hits
            winner_num = 2  # If defender loses all ships, attacker is player 2

        # Use rules engine to resolve the shot and update boards/sets
        result = fire_shot(
            attacker_shots,      # Attacker's shot-mark board
            defender_incoming,   # Defender's incoming-mark board
            defender_ships,      # Defender ships (list of coord lists)
            defender_hits,       # Defender hit set (tracks all hit coords)
            row,                 # Target row
            col                  # Target col
        )

        # If this cell was already fired on, do not proceed
        if result == "already":
            self.result_lbl.config(text="ALREADY SHOT")
            return

        # Show HIT/MISS/SINK immediately
        self.result_lbl.config(text=result.upper())

        self.selected = None  # Clear current target selection
        self.refresh_ui()  # Repaint boards so shot mark appears immediately
        # 1.5s after a valid shot, briefly black out the screen for hand-off
        self._schedule_shot_blackout(1500, 1500)

        # Check win condition: if defender has 0 ships remaining, attacker wins
        if ships_remaining(defender_ships, defender_hits) == 0:
            self.input_locked = True  # Prevent any more interaction
            self.fire_btn.config(state="disabled")  # Disable FIRE button
            self.result_lbl.config(text=f"PLAYER {winner_num} WINS!")  # Show win message on BattleScreen

            def go_to_win():
                win_screen = self.app.screens["WinScreen"]  # Get WinScreen instance
                win_screen.set_winner(f"PLAYER {winner_num} WINS!")  # Set winner text
                win_screen.set_stats()  # Compute + display final stats
                self.app.show_screen("WinScreen")  # Switch to WinScreen

            self._pending_after = self.after(1500, go_to_win)  # Delay 1.5 sec then go to win screen
            return

        # If no win, lock input and schedule turn switch
        self.input_locked = True  # Lock input during delay
        self.fire_btn.config(state="disabled")  # Disable FIRE button during delay
        self._pending_after = self.after(TURN_DELAY_MS, self._switch_turn)  # Schedule turn swap

    def _schedule_shot_blackout(self, delay_ms: int = 1500, duration_ms: int = 1500):
        """Wait `delay_ms` after a valid shot, then cover BOTH boards for `duration_ms`."""
        self._cancel_shot_blackout()
        self._shot_blackout_job = self.after(delay_ms, lambda: self._start_shot_blackout(duration_ms))

    def _cancel_shot_blackout(self):
        if self._shot_blackout_job is not None:
            try:
                self.after_cancel(self._shot_blackout_job)
            except Exception:
                pass
            self._shot_blackout_job = None

        if self._shot_blackout_hide_job is not None:
            try:
                self.after_cancel(self._shot_blackout_hide_job)
            except Exception:
                pass
            self._shot_blackout_hide_job = None

    def _start_shot_blackout(self, duration_ms: int = 1500):
        """Cover both boards (own + target) using COVER_BG for local hand-off."""
        if self._shot_blackout_active:
            return

        self._shot_blackout_active = True
        self._render_blackout_boards()

        # End blackout after duration
        self._shot_blackout_hide_job = self.after(duration_ms, self._end_shot_blackout)

    def _end_shot_blackout(self):
        """End board blackout and re-render normal UI."""
        self._shot_blackout_active = False
        self._shot_blackout_hide_job = None
        self.refresh_ui()

    def _render_blackout_boards(self):
        """Render both grids as covered (no marks, no selection, no clicks)."""
        # Cover own grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.own_cells[r][c].config(bg=COVER_BG, fg="black", text="")

        # Cover target grid and disable selection clicks
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.target_cells[r][c].config(bg=COVER_BG, fg="black", text="")
                self.target_cells[r][c].unbind("<Button-1>")

    def _switch_turn(self):
        s = self.app.state  # Shortcut to shared GameState

        s.current_turn = 2 if s.current_turn == 1 else 1  # Flip turn: 1 -> 2, 2 -> 1

        self.result_lbl.config(text="")  # Clear result message (HIT/MISS/SINK) for next player
        self.input_locked = False  # Re-enable input now that delay is over

        # These font assignments look like a UI styling attempt (not currently used elsewhere)
        self.cell_font = ("Arial", 16, "bold")   # Normal cell font
        self.mark_font = ("Arial", 26, "bold")   # Hit/miss mark font

        self.fire_btn.config(state="normal")  # Re-enable FIRE button

        self.refresh_ui()  # Re-render boards + scoreboard for new player view


    def refresh_ui(self):
        s = self.app.state  # Shared GameState
        turn = s.current_turn  # Current player turn (1 or 2)
        self.turn_lbl.config(text=f"Player {turn}'s turn")  # Update top label
        # If we're in the post-shot blackout window, cover both boards and stop.
        if self._shot_blackout_active:
            self._render_blackout_boards()
            return

        # Choose what the current player sees, based on whose turn it is
        if turn == 1:
            own_ship_board = s.p1_board      # Player 1 ship layout (1s where ships are)
            own_incoming = s.p1_incoming     # What Player 2 has done to Player 1 (hit/miss marks)
            own_color = P1_SHIP_BG           # Color to show P1 ships

            my_shots = s.p1_shots            # What P1 has fired at P2 (unknown/miss/hit)

            p1_stats = self._stats(s.p1_shots, s.p1_ships, s.p1_hits)  # P1 stats
            p2_stats = self._stats(s.p2_shots, s.p2_ships, s.p2_hits)  # P2 stats
        else:
            own_ship_board = s.p2_board      # Player 2 ship layout
            own_incoming = s.p2_incoming     # What Player 1 has done to Player 2
            own_color = P2_SHIP_BG           # Color to show P2 ships

            my_shots = s.p2_shots            # What P2 has fired at P1

            p1_stats = self._stats(s.p1_shots, s.p1_ships, s.p1_hits)  # P1 stats
            p2_stats = self._stats(s.p2_shots, s.p2_ships, s.p2_hits)  # P2 stats

        # Render left board (ships visible + incoming marks)
        self._render_own_board(self.own_cells, own_ship_board, own_incoming, own_color)

        # Render right board (opponent ships hidden except your shots)
        self._render_target_board(self.target_cells, my_shots)

        # Build ship-hit counter text for scoreboard
        p1_ship_counters = ship_hit_counters(s.p1_ships, s.p1_hits)  # List like ["1/1", "0/2", ...]
        p2_ship_counters = ship_hit_counters(s.p2_ships, s.p2_hits)

        p1_ship_line = ", ".join(p1_ship_counters) if p1_ship_counters else "-"  # Join or show "-"
        p2_ship_line = ", ".join(p2_ship_counters) if p2_ship_counters else "-"

        # Update scoreboard text (two lines, one per player)
        self.score_lbl.config(
            text=(
                f"P1 → Shots: {p1_stats['shots']} | Hits: {p1_stats['hits']} | "
                f"Misses: {p1_stats['misses']} | Ships: {p1_stats['ships']} | "
                f"Ship hits: {p1_ship_line}\n"
                f"P2 → Shots: {p2_stats['shots']} | Hits: {p2_stats['hits']} | "
                f"Misses: {p2_stats['misses']} | Ships: {p2_stats['ships']} | "
                f"Ship hits: {p2_ship_line}"
            )
        )

        # Highlight selected target cell (only if it's still UNKNOWN and input isn't locked)
        if self.selected is not None:
            r, c = self.selected
            if my_shots[r][c] == UNKNOWN and not self.input_locked:
                self.target_cells[r][c].config(bg=HIGHLIGHT_BG)  # Yellow highlight

        # Disable or restore click bindings on target board depending on lock state
        if self.input_locked:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.target_cells[r][c].unbind("<Button-1>")  # Prevent selecting during delay
        else:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.target_cells[r][c].bind("<Button-1>", self.target_cells[r][c]._click_handler)  # Re-enable selection


    def _render_own_board(self, cells, ship_board, incoming_board, ship_color: str):
        """
        Own view:
        - ships are colored
        - incoming MISS -> gray 'O'
        - incoming HIT  -> red  'X'
        """
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):

                # Base layer: show ships (if a ship exists in ship_board)
                if ship_board[r][c] == 1:
                    cells[r][c].config(bg=ship_color, fg="white", text="")  # Ship cell (colored)
                else:
                    cells[r][c].config(bg=ACTIVE_BG, fg="black", text="")  # Empty cell (white)

                # Overlay layer: show incoming marks (what opponent did to you)
                v = incoming_board[r][c]  # Cell value: UNKNOWN / MISS / HIT
                if v == MISS:
                    cells[r][c].config(bg=MISS_BG, fg="black", text="O")  # Miss mark
                elif v == HIT:
                    cells[r][c].config(bg=HIT_BG, fg="white", text="X")  # Hit mark


    def _render_target_board(self, cells, shots_board):
        """
        Target view:
        - opponent ships hidden (white)
        - your shots show:
          MISS -> gray 'O'
          HIT  -> red  'X'
        """
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                v = shots_board[r][c]  # Cell value: UNKNOWN / MISS / HIT

                if v == UNKNOWN:
                    cells[r][c].config(bg=ACTIVE_BG, fg="black", text="")  # Not shot yet
                elif v == MISS:
                    cells[r][c].config(bg=MISS_BG, fg="black", text="O")  # Missed shot
                else:
                    cells[r][c].config(bg=HIT_BG, fg="white", text="X")  # Hit shot


    def _stats(self, shots_board, ships_list, hits_set):
        hits = sum(  # Count all HIT values inside the shots_board
            1
            for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if shots_board[r][c] == HIT
        )

        misses = sum(  # Count all MISS values inside the shots_board
            1
            for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if shots_board[r][c] == MISS
        )

        shots = hits + misses  # Total shots fired = hits + misses

        ships_left = ships_remaining(ships_list, hits_set)  # Count ships not fully sunk yet

        return {"shots": shots, "hits": hits, "misses": misses, "ships": ships_left}  # Pack into a dict


class WinScreen(tk.Frame):  # Final screen: show winner + stats + play again / exit
    def __init__(self, parent, app):
        super().__init__(parent)  # Initialize Frame base class
        self.app = app  # Reference to App (for new_game + destroy + state)

        self.title_lbl = tk.Label(self, text="Game Over", font=("Arial", 30, "bold"))  # Big title label
        self.title_lbl.pack(pady=20)  # Add vertical spacing

        self.winner_lbl = tk.Label(self, text="", font=("Arial", 24))  # Winner text gets filled later
        self.winner_lbl.pack(pady=10)

        self.stats_lbl = tk.Label(self, text="", font=("Arial", 18), justify="left")  # Stats block
        self.stats_lbl.pack(pady=10)

        btn_row = tk.Frame(self)  # Container holding both buttons
        btn_row.pack(pady=25)

        play_btn = tk.Button(  # Restart the game
            btn_row,
            text="Play Again",
            font=("Arial", 16, "bold"),
            width=18,
            command=self.play_again,  # Calls play_again()
        )
        play_btn.grid(row=0, column=0, padx=10)

        exit_btn = tk.Button(  # Close the entire app
            btn_row,
            text="Exit",
            font=("Arial", 16, "bold"),
            width=18,
            command=self.exit_game,  # Calls exit_game()
        )
        exit_btn.grid(row=0, column=1, padx=10)

    def set_winner(self, winner_text: str):
        self.winner_lbl.config(text=winner_text)  # Update winner label text

    def play_again(self):
        self.app.new_game()  # Reset state and return to WelcomeScreen

    def exit_game(self):
        self.app.destroy()  # Close the Tk window and exit the program

    def set_stats(self):
        s = self.app.state  # Shortcut to shared GameState

        def counts(shots_board):
            # Count HIT and MISS values in a shots board, then compute accuracy
            hits = sum(
                1 for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                if shots_board[r][c] == HIT
            )
            misses = sum(
                1 for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                if shots_board[r][c] == MISS
            )
            shots = hits + misses  # Total shots taken
            acc = (hits / shots * 100) if shots > 0 else 0.0  # Accuracy percent
            return shots, hits, misses, acc  # Return computed stats

        p1_shots, p1_hits, p1_misses, p1_acc = counts(s.p1_shots)  # Player 1 shot stats
        p2_shots, p2_hits, p2_misses, p2_acc = counts(s.p2_shots)  # Player 2 shot stats

        p1_ships_left = ships_remaining(s.p1_ships, s.p1_hits)  # Ships still alive for Player 1
        p2_ships_left = ships_remaining(s.p2_ships, s.p2_hits)  # Ships still alive for Player 2

        p1_ship_line = ", ".join(ship_hit_counters(s.p1_ships, s.p1_hits)) or "-"  # Per-ship hit counts
        p2_ship_line = ", ".join(ship_hit_counters(s.p2_ships, s.p2_hits)) or "-"

        # Build multi-line stats text block
        text = (
            f"Player 1 Stats\n"
            f"Shots: {p1_shots} | Hits: {p1_hits} | Misses: {p1_misses} | Accuracy: {p1_acc:.1f}% | Ships left: {p1_ships_left}\n"
            f"Ship hits: {p1_ship_line}\n\n"
            f"Player 2 Stats\n"
            f"Shots: {p2_shots} | Hits: {p2_hits} | Misses: {p2_misses} | Accuracy: {p2_acc:.1f}% | Ships left: {p2_ships_left}\n"
            f"Ship hits: {p2_ship_line}"
        )

        self.stats_lbl.config(text=text)  # Display stats text on the screen
