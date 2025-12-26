import os
from golf_solitaire import GolfGame, Card, Pile
import pygame

# --- CONSTANTS ---
CARD_WIDTH = 34
CARD_HEIGHT = 58
CARD_CACHE = {}
BACK_IMAGE = None
DARK_GREEN_COLOR = (4, 93, 29)

# --- UTILITIES ---
def load_image(path) -> pygame.Surface:
    """Load image from given path, scaled to card size"""
    try:
        # Load the image
        image = pygame.image.load(path).convert_alpha()
        # Scale the image to a standard size
        scaled_image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        return scaled_image
            
    except pygame.error as e:
        print(f"Error loading image for {path}: {e}")
        # Return a simple red rectangle as a placeholder if image fails to load
        placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        placeholder.fill((255, 0, 0)) # Red color
        return placeholder
    
def get_card_image(card: Card):
    """Retrieves image from cache or loads it if missing."""
    if card.hidden:
        return BACK_IMAGE
    
    name = f"card_{card.face}{card.value}.png"
    if name not in CARD_CACHE:
        path = os.path.join('Card_Deck_Sprites', name)
        CARD_CACHE[name] = load_image(path)
    return CARD_CACHE[name]


# --- MODELS ---

# Card Model used for card thats being dragged
class CardObject:
    def __init__(self, card: Card, x=0, y=0):
        self.x = x
        self.y = y
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
        self.golf_game = golf_game
        self.active_card: CardObject|None = None

# --- VIEWS ---

class GameView:
    def __init__(self, model: GameObject):
        self.model = model
        # Initialize views for tableau, stockpile, wastepile
        self.tableau = [ PileView(pile, x=100 + i * (CARD_WIDTH + 20), y=100) for i, pile in enumerate(self.model.golf_game.tableau) ]

        self.stockpile = StockPileView(model.golf_game.stockpile, x=200, y= 300)

        self.wastepile = WastePileView(model.golf_game.wastepile, x=100, y = 300)

    def draw(self, screen):
        ## draw tableau
        for i, pile in enumerate(self.tableau):
            pile.draw(screen, active_card=game_model.active_card)
        # draw stockpile
        self.stockpile.draw(screen=screen)

        # draw wastepile
        self.wastepile.draw(screen=screen)

        if game_model.active_card != None:
            CardView.draw(screen, game_model.active_card)

class PileView:
    def __init__(self, model: Pile, x, y, spacing=20):
        self.model = model
        self.x = x
        self.y = y
        self.spacing = spacing
        # For simplicity, we will just represent the pile as a rectangle
        self.rect = pygame.Rect(self.x, self.y, CARD_WIDTH, CARD_HEIGHT * 5 // 2)
        
    def draw(self, screen, active_card: CardObject|None = None):
        # Draw the surface
        pygame.draw.rect(screen, DARK_GREEN_COLOR, self.rect)
        # Draw the cards
        for i, card in enumerate(self.model.cards):
            if active_card is None or not active_card.card == card:
                card_x = self.x
                card_y = self.y + (i * self.spacing)
                img = get_card_image(card)
                screen.blit(img, (card_x, card_y))

class StockPileView(PileView):
    def __init__(self, model: Pile, x, y):
        super().__init__(model=model, x=x, y=y, spacing=10)
        self.rect = pygame.Rect(self.x, self.y, CARD_WIDTH * len(self.model.cards) // 2, CARD_HEIGHT)

    def draw(self, screen, active_card=None):
        # Draw the surface
        pygame.draw.rect(screen, DARK_GREEN_COLOR, self.rect)
        # Draw the cards
        for i, card in enumerate(self.model.cards):
            if active_card != card:
                card_x = self.x + (i * self.spacing)
                card_y = self.y
                screen.blit(BACK_IMAGE, (card_x, card_y))

class WastePileView(PileView):
    def __init__(self, pile: Pile, x, y) -> None:
        super().__init__(pile, x, y, spacing=0)

    def draw(self, screen, active_card=None):
        if self.model.cards:
            top_card = self.model.cards[-1]
            if not (active_card and top_card == active_card):
                img = get_card_image(top_card)
                screen.blit(img, (self.x, self.y))

class CardView:
    @staticmethod
    def draw(screen, card_object:CardObject):
        img = get_card_image(card_object.card)
        screen.blit(img, (card_object.x, card_object.y))

# --- CONTROLLERS ---
class GameController:
    def __init__(self, game: GameObject, view: GameView,):
        self.golf_game: GameObject = game
        self.game_view = view

    def notify(self, event: pygame.Event):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Check select
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("selecting")
            self.handle_pickup(mouse_pos)
        
        # Check drag
        if event.type == pygame.MOUSEMOTION and self.golf_game.active_card != None:
            print("dragging")
            self.golf_game.active_card.x = mouse_pos.x - (CARD_WIDTH // 2)
            self.golf_game.active_card.y = mouse_pos.y - (CARD_HEIGHT // 2)
        # Check release
        if event.type == pygame.MOUSEBUTTONUP and self.golf_game.active_card != None:
            print("releasing")
            self.handle_drop(mouse_pos)

    def handle_pickup(self, pos: pygame.Vector2):
        # Draw from pile
        for pile_view in self.game_view.tableau:
            rect = pile_view.rect
            if rect.collidepoint(pos):
                rect_y = (rect.y + ((len(pile_view.model.cards)-1) * 20))
                card = pile_view.model.cards[-1]
                # Initialize CardObject at the exact position it was in the pile
                self.golf_game.active_card = CardObject(card, rect.x, rect_y)
                self.origin_pile = pile_view.model
                return
        # Draw from stock
        rect = self.game_view.stockpile.rect
        if rect.collidepoint(pos):
            _ = self.golf_game.golf_game.draw_from_wastepile()
            
    def handle_drop(self, pos: pygame.Vector2):
        waste_rect = self.game_view.wastepile.rect

        active_card = self.golf_game.active_card

        if waste_rect.collidepoint(pos) and active_card is not None:
            succes = self.golf_game.golf_game.try_put_on_wastepile(active_card.card)
            if succes and self.origin_pile is not None:
                _ = self.origin_pile.draw_card()
        
        self.golf_game.active_card = None
        self.origin_pile = None

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

# --- MAIN LOOP ---
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
BACK_IMAGE = load_image(os.path.join('Card_Deck_Sprites', "card_back.png"))
running = True

# --- INITIALIZE MVC COMPONENTS ---
event_manager = EventManager()
game_model: GameObject = GameObject(GolfGame())
game_viewer: GameView = GameView(game_model)
game_controller: GameController = GameController(game_model, game_viewer)
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