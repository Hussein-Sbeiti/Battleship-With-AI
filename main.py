'''
Battleship/
  main.py
  app/
    __init__.py
    app_models.py
    ui_app.py
    ui_screen.py
    models.py
  game/
    __init__.py
    game_board.py
    game_models.py
    ships.py
    rules.py        
    coords.py       
'''

'''
This file is the entry point of the Battleship application. 
Its only responsibility is to create an instance of the App class and start Tkinter’s event loop using mainloop(), 
which keeps the window running and responsive. 
It intentionally contains no UI layout, no game logic, and no state handling, keeping startup logic clean and isolated. 
The if __name__ == "__main__" guard ensures the app only launches when this file is run directly, not when imported elsewhere.
'''

# main.py
# Battleship Project - Program entry point
# This file is responsible only for starting the application.
# It should not contain any UI layout or game logic.
#
# Created: 2026-02-06

from app.ui_app import App

def main():
    """
    Entry point for the Battleship application.

    Creates the main App instance and starts the Tkinter
    event loop, which keeps the window running until the
    user closes the application.
    """
    app = App()
    app.mainloop()


# Ensures this file is only executed when run directly,
# and not when imported as a module.
if __name__ == "__main__":
    main()

