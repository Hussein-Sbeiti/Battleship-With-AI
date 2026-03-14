# Battleship (Python / Tkinter)

A local Battleship game built in Python with Tkinter. It supports two-player pass-and-play, AI opponents, random shots, limited-use 3x3 special shots, end-game stats, and replay flow.

## Project Layout

```text
Battleship-AI/
├── main.py
├── app/
│   ├── app_models.py
│   ├── ui_app.py
│   └── ui_screen.py
├── game/
│   ├── board.py
│   ├── coords.py
│   ├── game_models.py
│   ├── rules.py
│   └── ships.py
└── tests/
    ├── test_game_state.py
    └── test_rules.py
```

## Game Flow

1. Start the app from `main.py`.
2. Choose a fleet size from 1 to 5 ships.
3. Start either:
   - local two-player mode
   - AI Easy
   - AI Medium
4. Place ships in order from length 1 up to the chosen fleet size.
5. Battle using:
   - normal single-cell fire
   - `RANDOM` to fire at a random unknown cell
   - `SPECIAL` for a limited 3x3 shot
6. Win by sinking every enemy ship or by opponent forfeit.
7. Review final stats and choose replay or exit.

## Features

- Shared `GameState` for placement, battle, AI mode, and special-shot counters
- Hidden-board pass-and-play flow with handoff blackout
- Easy and medium AI opponents
- Random shot button
- Limited-use special 3x3 shot
- Forfeit menu action
- Final accuracy and ship-damage stats
- Optional wallpaper support when Pillow is installed

## Run the Game

```bash
python3 main.py
```

## Run Tests

```bash
python3 -m unittest
```

## Manual Validation Checklist

- Start a local two-player game and complete placement for both players.
- Confirm only the active player board is visible during placement.
- Verify invalid ship placement shows an error and does not change the board.
- Remove and replace a placed ship during placement.
- Start an AI Easy game and confirm player 2 ships are auto-placed.
- Start an AI Medium game and confirm the AI continues taking turns without exposing hidden boards.
- Use `RANDOM` and confirm it fires only at unknown cells.
- Arm `SPECIAL`, preview the 3x3 area, fire it, and confirm the counter decreases.
- Exhaust all special shots and confirm the special control disables cleanly.
- Trigger a forfeit during battle and confirm the win screen appears with stats.
- Finish a game normally and confirm replay returns to the welcome screen without stale delayed transitions.
- If Pillow is installed, choose and clear a wallpaper.
- If Pillow is not installed, confirm the app still runs and wallpaper actions fail gracefully.

## Notes

- Tkinter is included with most Python installations.
- Pillow is optional and only needed for wallpaper loading/resizing.
