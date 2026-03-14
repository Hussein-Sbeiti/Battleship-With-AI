# Battleship AI

A Battleship game built with Python and Tkinter. The project supports local pass-and-play, AI opponents, random shots, limited-use special attacks, end-game stats, replay flow, and optional wallpaper support.

## Overview

This project is a multi-screen Battleship app with a shared game state and separated game rules. Players can:

- choose a fleet size from 1 to 5 ships
- play local two-player mode on one screen
- play against an Easy or Medium AI
- use a `RANDOM` shot button
- use a limited `SPECIAL` 3x3 area shot
- forfeit from the menu during battle
- review final stats on the win screen

## Project Structure

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

## Current Features

- Welcome screen with local two-player, AI Easy, and AI Medium start options
- Placement screen with active-player highlighting and hidden inactive board
- Ship placement in required order from length `1` through selected fleet size
- Orientation toggle button plus `H` / `V` keyboard shortcuts during placement
- Ship removal by clicking an already placed ship
- Battle screen with:
  - normal fire
  - `RANDOM` fire on an unknown cell
  - `SPECIAL` 3x3 blast with limited uses per player
  - hidden enemy board
  - turn handoff blackout for local play
  - AI turn flow for computer games
- Scoreboard with shots, hits, misses, ships remaining, and per-ship damage counters
- Win screen with summary stats and replay support
- Menu support for forfeit and wallpaper controls
- Optional wallpaper loading when Pillow is installed

## What We Added And Fixed

Recent improvements included in the current version:

- Added a user-triggered `RANDOM` shot button
- Added a limited-use `SPECIAL` 3x3 shot
- Cleaned up the main UI so screens are more consistent and readable
- Improved placement feedback so the active player is clearer
- Improved battle controls so button states are more consistent
- Added safer transition handling so delayed screen callbacks do not leak into replay or screen changes
- Fixed wallpaper handling so the app still runs even if Pillow is not installed
- Added automated unit tests for rules and game-state reset behavior
- Updated project documentation and manual validation coverage

## Game Flow

1. Launch the app with `python3 main.py`.
2. Choose the number of ships.
3. Start either local two-player mode or an AI mode.
4. Place ships in order from size `1` up to the selected fleet size.
5. Enter battle mode and attack using normal shots, `RANDOM`, or `SPECIAL`.
6. Sink all opponent ships or win by forfeit.
7. Review the win screen and choose `Play Again` or `Exit`.

## Controls

- `Esc`: exit fullscreen
- `H` / `V`: switch placement orientation while on the placement screen
- `RANDOM`: automatically fire at a random unknown cell
- `SPECIAL`: arm or cancel the 3x3 special attack
- `Forfeit` menu item: end the current battle and award the win to the opponent
- `Choose Wallpaper` / `Clear Wallpaper`: update the background when Pillow is available

## How To Run

```bash
python3 main.py
```

## How To Run Tests

```bash
python3 -m unittest
```

## Manual Validation Checklist

- Start a local two-player game and complete both placement turns.
- Confirm only the active player’s board is visible during placement.
- Verify invalid ship placement shows an error and does not modify the board.
- Remove a placed ship and place it again in a new location.
- Start an AI Easy game and confirm player 2 ships are auto-generated.
- Start an AI Medium game and confirm the AI takes turns correctly.
- Use `RANDOM` and confirm it only fires at unknown cells.
- Arm `SPECIAL`, preview the blast area, fire it, and confirm the counter decreases.
- Use all special shots and confirm the special control disables correctly.
- Trigger a forfeit during battle and confirm the correct win screen appears.
- Finish a full game and confirm replay returns to the welcome screen cleanly.
- Confirm no stale delayed transitions occur after replay or forfeit.
- If Pillow is installed, choose a wallpaper and clear it.
- If Pillow is not installed, confirm the app still works and wallpaper actions fail gracefully.

## Automated Test Coverage

The current unit tests cover:

- `fire_shot()` miss, hit, sink, and already-fired cases
- `fire_area_shot()` center shots, edge clipping, and already-fired accounting
- `ships_remaining()`
- `GameState.reset_for_new_game()`

## Notes

- Tkinter is included with most Python installations.
- Pillow is optional and only needed for wallpaper image support.
- The project currently favors manual GUI validation plus automated rule/state tests.

## Future Implementations

Potential next improvements for the project:

- Hard AI with stronger search and targeting strategy
- Sound effects for hits, misses, sinks, and victory
- Better animations and transitions between turns and screens
- Smarter battle summaries, including move history
- Save/load game state
- Adjustable game settings for special-shot limits and turn timing
- Keyboard targeting shortcuts during battle
- Optional ship-placement randomizer for the player
- More robust GUI-level smoke tests
- Packaging the game as a desktop app build
