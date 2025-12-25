import os
from golf_solitaire import GolfGame, Card, Pile
import pygame

CARD_WIDTH = 34
CARD_HEIGHT = 58

DARK_GREEN_COLOR = (4, 93, 29)

pygame.init()
screen = pygame.display.set_mode((1280, 720))

def load_image(path) -> pygame.Surface:
    try:
        # Load the image
        image = pygame.image.load(path).convert_alpha()
        # Scale the image to a standard size (optional, but good for consistency)
        scaled_image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        return scaled_image
            
    except pygame.error as e:
        print(f"Error loading image for {path}: {e}")
        # Return a simple red rectangle as a placeholder if image fails to load
        placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        placeholder.fill((255, 0, 0)) # Red color
        return placeholder

BACK_IMAGE = load_image(os.path.join('Card_Deck_Sprites', "card_back.png"))

class CardObject:
    def __init__(self, card: Card, x=0, y=0):
        self.x = x
        self.y = y
        self.being_dragged = False
        self.card = card

    def is_colliding(self, cord: pygame.Vector2) -> bool:
        return self.x <= cord.x < self.x + CARD_WIDTH and self.y <= cord.y < self.y + CARD_HEIGHT

    def move(self, cord: pygame.Vector2):
        self.x = cord.x
        self.y = cord.y
    
    def place(self):
        pass

class PileObject:
    def __init__(self, pile: Pile, x=0, y=0):
        self.x = x
        self.y = y
        self.pile = pile

    def is_colliding(self, cord: pygame.Vector2) -> bool:
        return self.x <= cord.x < self.x + CARD_WIDTH and self.y <= cord.y < self.y + (CARD_HEIGHT * len(self.pile.cards))
    
class GameObject:
    def __init__(self, golf_game: GolfGame):
        self.x = 0
        self.y = 0
        self.golf_game = golf_game


class TableauController:
    pass

class GameController:
    def __init__(self, game: GameObject):
        self.golf_game: GameObject = game
        # init tableau

        # init stockpile

        # init wastepile

    def notify(self, event: pygame.Event):
        ##print(event)
        pass

class CardController:
    def __init__(self, model: CardObject):
        self.model = model
        
    def notify(self, event: pygame.Event):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Check select
        if event.type == pygame.MOUSEBUTTONDOWN and not self.model.card.hidden:
            print("selecting")
            if self.model.is_colliding(mouse_pos):
                self.model.being_dragged = True
        # Check drag
        if event.type == pygame.MOUSEMOTION and self.model.being_dragged:
            print("dragging")
            self.model.move(mouse_pos)
        # Check release
        if event.type == pygame.MOUSEBUTTONUP and self.model.being_dragged:
            print("releasing")
            self.model.being_dragged = False

class GameView:
    def __init__(self, model: GameObject):
        self.model = model
        # Initialize views for tableau, stockpile, wastepile
        self.tableau = [ PileView(PileObject(pile, x=100 + i * (CARD_WIDTH + 10), y=100)) for i, pile in enumerate(self.model.golf_game.tableau) ]

        self.stockpile = StockPileView(PileObject(model.golf_game.stockpile, x=200, y= 300))

        self.wastepile = WastePileView(PileObject(model.golf_game.wastepile, x=100, y = 300))

    def draw(self, screen):
        ## draw tableau
        for i, pile in enumerate(self.tableau):
            pile.draw(screen)
        # draw stockpile
        self.stockpile.draw(screen=screen)

        # draw wastepile
        self.wastepile.draw(screen=screen)

class StockPileView:
    def __init__(self, model: PileObject):
        self.model = model
        self.card_models = [CardObject(card, self.model.x + i * CARD_HEIGHT // 2, self.model.y) 
                    for i, card in enumerate(self.model.pile.cards)]
        self.rect = pygame.Rect(self.model.x, self.model.y, CARD_WIDTH * len(self.model.pile.cards) // 2, CARD_HEIGHT)

        self.card_views = [CardView(m) for m in self.card_models]

    def draw(self, screen):
        # Draw the surface
        pygame.draw.rect(screen, DARK_GREEN_COLOR, self.rect)
        # Draw the cards
        for i, card in enumerate(self.card_views):
            card.draw(screen=screen)

class WastePileView:
    def __init__(self, model: PileObject) -> None:
        self.model = model
        self.card_models = [CardObject(card, self.model.x, self.model.y)]
        self.rect = pygame.Rect(self.model.x, self.model.y, CARD_WIDTH, CARD_HEIGHT)
        self.card_views = [CardView(m) for m in self.card_models]

    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GREEN_COLOR, self.rect)
        self.card_views[-1].draw(screen=screen)

class PileView:
    def __init__(self, model: PileObject):
        self.model = model
        self.card_models = [CardObject(card, self.model.x, self.model.y + i * CARD_HEIGHT // 2) 
                    for i, card in enumerate(self.model.pile.cards)]
        # For simplicity, we will just represent the pile as a rectangle
        self.rect = pygame.Rect(self.model.x, self.model.y, CARD_WIDTH, CARD_HEIGHT * len(self.model.pile.cards) // 2)

        # card views
        self.card_views = [CardView(m) for m in self.card_models]

    def draw(self, screen):
        # Draw the surface
        pygame.draw.rect(screen, DARK_GREEN_COLOR, self.rect)
        # Draw the cards
        for i, card in enumerate(self.card_views):
            if not card.model.being_dragged:
                card.draw(screen=screen)

class CardView:
    def __init__(self, model: CardObject):
        self.model = model
        self.image = self.load_image()
        # Set a default position (you'd typically pass this in or calculate it)
        self.rect = self.image.get_rect(topleft=(self.model.x, self.model.y))

    def load_image(self):
        # Ensure face and value are strings for filename creation
        face_str = str(self.model.card.face)
        value_str = str(self.model.card.value)
        
        # Construct the filename
        filename = f"card_{face_str}{value_str}.png"
        
        # Create the full path
        image_path = os.path.join('Card_Deck_Sprites', filename) 
        
        try:
            # Load the image
            image = pygame.image.load(image_path).convert_alpha()
            # Scale the image to a standard size (optional, but good for consistency)
            scaled_image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
            return scaled_image
            
        except pygame.error as e:
            print(f"Error loading image for {filename}: {e}")
            # Return a simple red rectangle as a placeholder if image fails to load
            placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            placeholder.fill((255, 0, 0)) # Red color
            return placeholder
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def draw(self, screen):
        self.rect.topleft = (self.model.x, self.model.y)
        # The image is drawn at the position stored in self.rect
        if self.model.card.hidden:
            screen.blit(BACK_IMAGE, self.rect)
        else:
            screen.blit(self.image, self.rect)

class Event:
    """this is a superclass for any events that might be generated by an
    object and sent to the EventManager"""
    def __init__(self):
        self.name = "Generic Event"

class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""
    def __init__(self ):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def RegisterListener( self, listener ):
        self.listeners[ listener ] = 1

    def UnregisterListener( self, listener ):
        if listener in self.listeners.keys():
            del self.listeners[ listener ]

    def Post( self, event ):
        for listener in self.listeners.keys():
            #NOTE: If the weakref has died, it will be 
            #automatically removed, so we don't have 
            #to worry about it.
            listener.notify( event )

# pygame setup
clock = pygame.time.Clock()
running = True

def controller_tick(event_manager: EventManager):
    global running
    #Handle Input Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            return 0
        event_manager.Post(event=event)
    return 1

def view_tick():
    pass

event_manager = EventManager()
card = Card("H", "A")
card_model = CardObject(card=card)
card_controller = CardController(card_model)
card_viewer = CardView(card_model)
# event_manager.RegisterListener(card_controller)

game_model: GameObject = GameObject(GolfGame())
game_controller: GameController = GameController(game_model)
game_viewer: GameView = GameView(game_model)
event_manager.RegisterListener(game_controller)

while running:

    # handle input
    controller_tick(event_manager)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("green")

    # RENDER YOUR GAME HERE
    view_tick()
    # card_viewer.draw(screen=screen)
    game_viewer.draw(screen=screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()