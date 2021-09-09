
from a2_solution import *
import tkinter as tk
from tkinter import messagebox



#***********************************************************************
#***********************************************************************


class AbstractGrid(tk.Canvas):
    
    def __init__(self, master, rows, cols, width, height, **kwargs):
        """
        The parameters rows and cols are the number of rows and column
        in the grid, width and height are the width and height of the 
        grid(in pixels).
        """
        tk.Canvas.__init__(self, master, width=width, height=height, **kwargs)

    def get_bbox(self, position: Position) -> tuple:
        """
        Returns the bounding box for the (row, column) position; this is
        a tuple containing information about the pixel positions of the
        edges of the shape, in the form(x_min, y_min, x_max, y_max).
        """
        return (position.get_x()*CELL_SIZE,
                position.get_y()*CELL_SIZE,
                position.get_x()*CELL_SIZE + CELL_SIZE,
                position.get_y()*CELL_SIZE + CELL_SIZE)

    def pixel_to_position(self, pixel: tuple) -> Position:
        """
        Converts the (x, y) pixel position to a (row, column) position.
        """
        return Position(pixel[0]//CELL_SIZE,
                        pixel[1]//CELL_SIZE)

    def get_position_center(self, position: Position) -> tuple:
        """
        Gets the graphics coordinates for the center of the cell at the
        given (row, column) position.
        """
        return (position.get_x() * CELL_SIZE + CELL_SIZE//2,
                position.get_y() * CELL_SIZE + CELL_SIZE//2)

    def annotate_position(self, position: Position, text: str) -> None:
        """
        Annotates the center of the cell at the given (row, column) po-
        sition with the provided text.
        """
        pixel_center = self.get_position_center(position)
        self.create_text(pixel_center[0], pixel_center[1], text=text)


class BasicMap(AbstractGrid):
    """
    BasicMap is a view class which inherits from AbstractGrid. Entities
    are drawn on the map using coloured at different (row, column) po-
    sition. The size is number of rows(=column).
    """

    def __init__(self, master, size, **kwargs):
        super().__init__(master, size, size,
                         width=size*CELL_SIZE, height=size*CELL_SIZE, **kwargs)

    def draw_entity(self, position: Position, tile_type: str) -> None:
        """
        Draws the entity with tile_type at the given position using a
        coloured rectangle with superimposed text indentifying the en-
        tity.
        """
        colour = ENTITY_COLOURS[tile_type]
        bbox = self.get_bbox(position)
        self.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3] ,fill=colour)
        self.annotate_position(position, text=tile_type)


class InventoryView(AbstractGrid):
    """
    InventoryView is a view class which inherits from AbstractGrid and
    displays the items the player has in their inventory. This class
    also provides a mechanism through which the user can activate an
    item held in the player's inventory.
    """
    def __init__(self, master, rows, **kwargs):
        """
        The parameter rows should be set to the number of rows in the
        game map.
        """
        super().__init__(master, rows, 1, 
                         INVENTORY_WIDTH, rows*CELL_SIZE,**kwargs)

    def draw(self, inventory:Inventory):
        """
        Draws the inventory label and current items with their remaining
        lifetimes.
        """
        #Inventory Title
        self.create_text(INVENTORY_WIDTH//2, CELL_SIZE//2,
                         text="Inventory", fill=DARK_PURPLE, font='bold')
        
        #Inventory List
        for i in range(len(inventory.get_items())):
            if inventory.get_items()[i].is_active():
                bcolour = DARK_PURPLE
                tcolour = 'white'
                self.create_rectangle(0,
                                      (i+1)*CELL_SIZE, 
                                      INVENTORY_WIDTH,
                                      (i+2)*CELL_SIZE,
                                      fill=bcolour)
                #item
                self.create_text(CELL_SIZE,
                                 (i+1)*CELL_SIZE+CELL_SIZE//2,
                                 text=inventory.get_items()[i].__class__.__name__,
                                 fill=tcolour)
                #lifetime
                self.create_text(3*CELL_SIZE,
                                 (i+1)*CELL_SIZE+CELL_SIZE//2,
                                 text=inventory.get_items()[i].get_lifetime(),
                                 fill=tcolour)
            else:
                #item
                self.create_text(CELL_SIZE,
                                 (i+1)*CELL_SIZE+CELL_SIZE//2, 
                                 text=inventory.get_items()[i].__class__.__name__)
                #lifetime
                self.create_text(3*CELL_SIZE,
                                 (i+1)*CELL_SIZE+CELL_SIZE//2, 
                                text=inventory.get_items()[i].get_lifetime())

class BasicGraphicalInterface:
    """
    The BaiscGraphicalInterface should manage the overall view(i.e. con-
    structing the three major widgets) and event handling.
    """
    def __init__(self, root, size):
        """
        The parameter root represents the root window and size represent
        the number of rows(=column) in the game map. This method will 
        draw the title label, and instantiate and pack the BasicMap
        and InventoryView.
        """
        #title
        self._label = tk.Label(root,
                               text=TITLE,
                               bg=DARK_PURPLE,
                               fg='white',
                               height=3)
        self._label.pack(side=tk.TOP,fill=tk.BOTH)

        #map
        self._map = BasicMap(root, size, bg=LIGHT_BROWN)
        self._map.pack(side=tk.LEFT)

        #inventory
        self._inventory = InventoryView(root, size,bg=LIGHT_PURPLE)
        self._inventory.pack(side=tk.RIGHT)

        #fire toggle flag
        self._is_firing = False

        self._root = root
        self._after_id = None

    def _inventory_click(self, event, inventory:Inventory):
        """
        This method should be called when the user left clicks on inven-
        tory view. It handles activating or deactivating the clicked
        item and update both the model and the view accrodingly.
        """
        click_row = event.y//CELL_SIZE

        try:
            inventory.get_items()[click_row - 1].toggle_active()

            #redraw the inventory list
            self._inventory.delete(tk.ALL)
            self._inventory.draw(inventory)
        except:
            pass

    def draw(self, game: AdvancedGame):
        """
        Clears and redraws the view based on the current game state.
        """
        self._map.delete(tk.ALL)
        self._inventory.delete(tk.ALL)
        mapping = game.get_grid().get_mapping()
        inv = game.get_player().get_inventory()

        #draw current map
        for position, tile_type in mapping.items():
            self._map.draw_entity(position, tile_type.display())
        
        #draw current inventory
        self._inventory.draw(inv)
    
    def _move(self, game: AdvancedGame, direction: str):
        """
        Handles moving the player and redrawing the game.
        """
        player = game.get_player()
        items = player.get_inventory()

        # Ensure player has a weapon that they can fire.
        if player.get_inventory().contains(CROSSBOW) and items.has_active(CROSSBOW):
            self._is_firing = True

        if self._is_firing == True and items.has_active(CROSSBOW):
                
            # Fire the weapon in the indicated direction, if possible.
            if direction in ARROWS_TO_DIRECTIONS:
                start = game.get_grid().find_player()
                offset = game.direction_to_offset(ARROWS_TO_DIRECTIONS[direction])
                if start is None or offset is None:
                    return  #Should never happen.

                # Find the first entity in the direction player fired.
                first = first_in_direction(
                game.get_grid(), start, offset)
                        
                # If the entity is a zombie, kill it.
                if first is not None and first[1].display() in ZOMBIES:
                    position, entity = first
                    game.get_grid().remove_entity(position)
            
                self._is_firing = False
            
            elif direction in DIRECTIONS:
                game.move_player(game.direction_to_offset(direction))
                serialize = game.get_grid().serialize()

        elif self._is_firing != True and direction in DIRECTIONS:
            game.move_player(game.direction_to_offset(direction))
            serialize = game.get_grid().serialize()
        

        #draw current map and inventory
        self.draw(game)

        if game.has_won():
            self._root.after_cancel(self._after_id)
            reset = messagebox.askyesno(title='message', message='You win!\nDo you want to play again?')
            
            if reset == True:
                self._after_id = None
                game = advanced_game(MAP_FILE)
                self.play(game)
                return
            else:
                self._root.quit()

    def _keypress_handler(self, event, game: AdvancedGame):
        """
        Handles the key that user pressed to move the player.
        """
        key_pressed = event.keysym
        if key_pressed.upper() in DIRECTIONS:
            self._move(game, key_pressed.upper())
        elif key_pressed in ARROWS_TO_DIRECTIONS:
            self._move(game, key_pressed)

    def _step(self, game: AdvancedGame):
        """
        The _step method is called every second. This method triggers the
        step method for the game and updates the view accrodingly.
        """
        if game.has_lost():
            self._root.after_cancel(self._after_id)
            reset = messagebox.askyesno(title='message', message='You lose!\nDo you want to play again?')
            
            if reset == True:
                self._after_id = None
                game = advanced_game(MAP_FILE)
                self.play(game)
                return
            else:
                self._root.quit()

        game.step()
        self.draw(game)

        self._after_id = self._root.after(1000, lambda: self._step(game))

    def play(self, game: AdvancedGame):
        """
        Binds events and initialises gameplay. This method will need to
        be called on the instantiated BasicGraphicalInterface in main
        to commence gameplay.
        """
        self.draw(game)
        self._inventory.bind('<Button-1>', 
                             lambda event: self._inventory_click(event, game.get_player().get_inventory()))
        self._root.bind('<KeyPress>',
                       lambda event: self._keypress_handler(event, game))
        
        self._step(game)
        self._root.mainloop()




 



    



def main() -> None:
    
    root = tk.Tk()
    root.title(TITLE)
    game = advanced_game(MAP_FILE)
    gui = BasicGraphicalInterface(root, game.get_grid().get_size())
    gui.play(game)
    

    """
    root = tk.Tk()
    a = BasicMap(root, 5)
    #a = AbstractGrid(root, 5, 5, 250, 250)
    a.pack()
    a.draw_entity(Position(3,0), PLAYER)
    #print(a.get_position_center(Position(8,0)))
    #print(a.pixel_to_position((150,50)))
    #print(a.get_bbox(Position(1,3)))
    root.mainloop()
    """

    

if __name__ == "__main__":
    main()
