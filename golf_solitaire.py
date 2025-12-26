import copy
import random

# CONSTANTS
CARD_FACES = ["H", "C", "S", "D"]
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_WIDTH = 5
LINE_SEP = " "

FACE_MAPPING = {
    "H": "♡",
    "S": "♠",
    "C": "♣",
    "D": "♢"
}

# Basic card class
class Card:
    def __init__(self, face, value, hidden = False):
        self.face: str = face
        self.value: str = value
        self.hidden: bool = hidden

    def __repr__(self):
        return f"{{{self.face}{self.value} hidden: {self.hidden}}}"
    
    def __str__(self):
        return "[**]" if self.hidden else f"[{self.face}{self.value}]"
    
    def can_place_on_top(self, other: Card) -> bool:
        return abs(CARD_VALUES.index(other.value) - CARD_VALUES.index(self.value)) == 1 or (other.value == "K" and self.value == "A") or (other.value == "A" and self.value == "K")

# Class for a pile of cards
class Pile:
    def __init__(self, cards, faceDown=False):
        self.cards: list[Card] = cards
        if faceDown:
            for card in self.cards:
                card.hidden = True

    def __repr__(self):
        return f"{",".join([repr(card) for card in self.cards])}"

    def draw_card(self) -> Card|None:
        if len(self.cards) > 0:
            card = self.cards.pop()
            card.hidden = False
            return card
        else:
            return None
    
    def peek_card(self) -> Card|None:
        if len(self.cards) > 0:
            return self.cards[-1]
        else: 
            return None
    
    def place_card(self, card):
        self.cards.append(card)

# Class to handle undoing of actions
class Redo:
    def __init__(self):
        self.state: list[GolfGame] = []

    def undo(self):
        if len(self.state) > 1:
            self.state.pop()
            return self.state[-1]
        return None
    
    def add(self, state):
        state_snapshot = state.__dict__.copy()

        if 'movestack' in state_snapshot:
            del state_snapshot['movestack']
        
        for key in ['tableau', 'stockpile', 'wastepile']:
            if key in state_snapshot:
                state_snapshot[key] = copy.deepcopy(state_snapshot[key])

        self.state.append(state_snapshot)
        print(f"DEBUG: State saved. Stack size: {len(self.state)}")

# Class to represent the state of a game of Golf Solitaire
class GolfGame:
    def __init__(self):
        self.selected = 1
        cards = CardDeck()
        cards.shuffle()
        self.tableau: list[Pile] = []
        for i in range(7):
            col = Pile(cards.draw_card(5))
            self.tableau.append(col)
        self.stockpile: Pile = Pile(cards.draw_card(15), faceDown=True)
        self.wastepile: Pile = Pile(cards.draw_card(1))
        self.movestack: Redo = Redo()
        self.moves: int = 0
        self.movestack.add(self)
    
    def __repr__(self):
        return f"Tableau:\n{"\n".join([repr(tab) for tab in self.tableau])}\n\nStock Pile\n{self.stockpile}\nWaste Pile\n{self.wastepile}"

    def draw_from_wastepile(self):
        newCard = self.stockpile.draw_card()
        if (newCard is not None):
            self.moves += 1
            self.wastepile.place_card(newCard)
            self.movestack.add(self)
            return "Drew a card from the stockpile"
        return "No more cards on the stockpile"
    
    def try_put_on_wastepile(self, card: Card) -> bool:
        topCard = self.wastepile.peek_card()
        if topCard is not None:
            if topCard.can_place_on_top(card):
                self.moves += 1
                self.wastepile.place_card(card=card)
                self.movestack.add(self)
                return True
        return False
    
    def try_draw_card(self, row):
        newCard = self.tableau[row].peek_card()
        topCard = self.wastepile.peek_card()
        if (newCard is not None):
            if (topCard is not None):
                if(topCard.can_place_on_top(newCard)):
                    self.moves += 1
                    self.tableau[row].draw_card()
                    self.wastepile.place_card(newCard)
                    self.movestack.add(self)
                    return "Placed card on wastepile"
                return f"Move not allowed! {topCard.value} vs. {newCard.value}"
            return "No cards on wastepile"
        return "No cards on selected pile"

    def undo(self):
        self.moves += 1
        previous_snapshot = self.movestack.undo()
        
        if previous_snapshot is None:
            return "No previous moves to undo!"
           
        self.__dict__.update(previous_snapshot) # type: ignore
        return "Undone last move"
    
    def draw_tableau(self) -> str:
        output = []
        max_len = max(len(col.cards) for col in self.tableau)
        for i in range(max_len): # Exclude the bottom-most card
        
            # Line 1 (Top Border for the stacked card): +---+, +---+, ...
            top_line = ""
            for col in self.tableau:
                if i < len(col.cards)+1 and len(col.cards) > 0:
                    # Card is present at this depth
                    top_line += "+---+" + LINE_SEP
                else:
                    # Empty space for alignment
                    top_line += " " * CARD_WIDTH + LINE_SEP
        
            # Line 2 (Card Face for the stacked card): |A  |, |Q  |, ...
            face_line = ""
            for col in self.tableau:
                if i < len(col.cards):
                    card = col.cards[i]
                    face = (card.value + FACE_MAPPING[card.face]).ljust(CARD_WIDTH - 2)
                    face_line += f"|{face}|" + LINE_SEP
                else:
                    # Empty space for alignment
                    face_line += " " * CARD_WIDTH + LINE_SEP
                
            output.append(top_line)
            output.append(face_line)

        # --- Draw Bottom-most Card (The fully visible top card) ---
        bottom_line = ""
        for col in self.tableau:
            if max_len > 0 and max_len - 1 < len(col.cards):
                # Only draw the bottom border if a card exists at this final depth
                bottom_line += "+---+" + LINE_SEP
            else:
                # Empty space
                bottom_line += " " * CARD_WIDTH + LINE_SEP
    
        output.append(bottom_line)
        
        return "\n".join(output)
    
    def draw_piles(self):
        output = []
        empty = " "*5
        stockTop = self.stockpile.peek_card()
        wasteTop = self.wastepile.peek_card()
        for i in range (3):
            line = ""
            if i%2 == 0:
                line += empty if stockTop is None else "+---+"
                line += LINE_SEP
                line += empty if wasteTop is None else "+---+"
            else:
                line += empty if stockTop is None else f"|***|"
                line += LINE_SEP
                line += empty if wasteTop is None else f"|{(wasteTop.value + FACE_MAPPING[wasteTop.face]).ljust(CARD_WIDTH - 2)}|"
            output.append(line)
        return "\n".join(output)  

    def draw_self(self) -> str:
        # Draw title

        # Draw Menu
        menu_bar_pt1 = f"Score:{self.moves}  Stock:{len(self.stockpile.cards)}\n"
        menu_bar_pt2 = "-"*7*6+"\n"
        menu_bar_pt3 = []
        for i in range(7):
            menu_bar_pt3.append(f" |{i+1}| ")
        menu_bar_pt3 = LINE_SEP.join(menu_bar_pt3)
        menu_bar_pt3 += "\n"
        # Draw Tableau
        tableau = self.draw_tableau()
        # Draw Bottom Piles
        bottom_part1 = "--S-- --W--\n"
        bottom_part2 = self.draw_piles()        
    
        return menu_bar_pt1+menu_bar_pt2+menu_bar_pt3+tableau+"\n\n"+bottom_part1+bottom_part2
    
    def check_game_state(self) -> str:
        if (len(self.stockpile.cards) == 0 and len(self.wastepile.cards) != 52):
            allInvalid = True
            for col in self.tableau:
                top = col.peek_card()
                if (top):
                    if (top.can_place_on_top(self.wastepile.peek_card())): # type: ignore
                        allInvalid = False
            return "lose" if allInvalid else "running"
        for col in self.tableau:
            val = col.peek_card()
            if not val is None:
                return "running"
        return "win"

# Class to represent one card deck
class CardDeck:
    def __init__(self):
        self.cards = []
        for face in CARD_FACES:
            for value in CARD_VALUES:
                self.cards.append(Card(face, value))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self, number=1):
        drawn = []
        for x in range(min(number, len(self.cards))):
            drawn.append(self.cards.pop())
        return drawn   

