class Ship:

    V_ORIENTATION = 0
    H_ORIENTATION = 1

    def __init__(self, decks, main_cell, orientation="h"):
        self.decks = decks
        self.main_cell = main_cell
        self.orientation = orientation
        self.coordinats = []
        self.hits = 0
        self.is_destroyed = False
