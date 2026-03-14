---

# Battleship (Python / Tkinter)

A two-player Battleship game built in Python using Tkinter.
Turn-based gameplay with hidden boards, ship placement, battle logic, scoreboard tracking, and a dedicated win screen.

---

## Game Overview

Battleship is a strategy game where two players place ships on a 10×10 grid and take turns firing at the opponent’s board.

The goal is to sink all of the opponent’s ships first.

This project focuses on:

* Turn-based hidden-information gameplay
* Clean separation of logic (state + rules + UI)
* Clear visual feedback for hits, misses, sinks, and win state
* Restartable multi-screen flow

---

## Project Structure

```
Battleship/
│
├── main.py                # Program entry point
│
├── app/
│   ├── __init__.py
│   ├── ui_app.py          # Main Tkinter app + screen manager
│   └── ui_screen.py       # Welcome, Placement, Battle, Win screens
│
├── game/
│   ├── board.py           # Board placement validation
│   ├── rules.py           # Fire logic, sink detection, win logic
│   └── ships.py           # Ship utilities + per-ship hit counters
│
├── utils/
│   └── coords.py          # Coordinate helpers (A–J, 1–10 labels)
│
├── README.md
└── .gitignore
```

---

## Screens & Game Flow

### 1. Welcome Screen

* Choose number of ships (1–5)
* Ship sizes are automatically generated:

  * 1 ship → 1×1
  * 2 ships → 1×1, 1×2
  * ...
  * 5 ships → 1×1 through 1×5

After selecting ships, the game transitions to placement.

---

### 2. Placement Phase

* Player 1 places ships first
* Player 2 places ships second
* Ships can be placed:

  * Horizontally (H)
  * Vertically (V)
* Clicking an existing ship removes it
* Only the active player’s board is visible
* Must place all ships before continuing
* After Player 2 presses Ready, a short delay occurs before battle begins

---

### 3. Battle Phase

Each turn:

1. Select a cell on the opponent’s board
2. Press FIRE
3. Result displays:

   * HIT
   * MISS
   * SINK
4. After a short delay, turn switches

Visual indicators:

* `X` = Hit
* `O` = Miss
* Player 1 ships = Green
* Player 2 ships = Orange

Opponent ships remain hidden during battle.

---

### 4. Scoreboard

Displayed during battle for both players:

* Total shots
* Hits
* Misses
* Ships remaining
* Per-ship hit counters (example: `2/3`)

---

### 5. Win Screen

When one player’s ships are all sunk:

* Winner is displayed
* Final stats are shown for both players
* Options:

  * Play Again (returns to Welcome Screen)
  * Exit (closes the application)

---

## How to Run

```
python3 main.py
```

Requirements:

* Python 3.x
* Tkinter (included with most Python installations)

---

## Features Implemented

* Multi-screen Tkinter application
* 10×10 grid with labeled rows and columns
* Ship placement with orientation toggle
* Turn-based firing system
* Hit / Miss / Sink logic
* Hidden opponent board
* Scoreboard tracking
* Per-ship hit counters
* Win detection
* Restart flow
* Controlled transition delays between phases

---

## Future Improvements

* Sound effects for hits and sinks
* Keyboard coordinate input (e.g., B7)
* UI animations and polish
* AI opponent mode
* Game settings screen
* Code documentation expansion

---

