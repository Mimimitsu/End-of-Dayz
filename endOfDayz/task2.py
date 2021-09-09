from a2_solution import *
from task1 import AbstractGrid, InventoryView, BasicGraphicalInterface
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

#image list initialize
entity_image = None 
entity_tkimage = list(range(400))

class StatusBar(tk.Frame):
    """
    The StatusBar will include:
        The chaser and chasee images
        A game timer
        A moves counter
        A 'Restart Game' button
        A 'Quit Game' button
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._parent = parent

        #banner
        self.banner_photo = Image.open('images/banner.png')
        self.banner_photo.thumbnail((685, 685))
        self.banner_tkphoto = ImageTk.PhotoImage(image = self.banner_photo)
        self.banner_label = tk.Label(parent, image = self.banner_tkphoto)
        self.banner_label.pack(side=tk.TOP)

        #chaser and chasee's photo
        self.chaser_photo = Image.open('images/chaser.png')
        self.chaser_tkphoto = ImageTk.PhotoImage(image = self.chaser_photo)
        self.chasee_photo = Image.open('images/chasee.png')
        self.chasee_tkphoto = ImageTk.PhotoImage(image = self.chasee_photo)

        #chaser's label
        self._chaser_label = tk.Label(self, image = self.chaser_tkphoto)
        self._chaser_label.pack(side = tk.LEFT)

        #timer
        self._timer = tk.Label(self, text = 'Timer\n0 mins 0 seconds')
        self._timer.pack(side = tk.LEFT, padx = 70)

        #counter
        self._moves_counter = tk.Label(self, text = 'Moves made\n0 moves')
        self._moves_counter.pack(side = tk.LEFT)

        #button's frame
        self._button_frame = tk.Frame(self)
        self._button_frame.pack(side = tk.LEFT, padx = 70)

        self._restart_button = tk.Button(self._button_frame, text = 'Restart Game', command = self._restart)
        self._restart_button.pack(side = tk.TOP)

        self._quit_button = tk.Button(self._button_frame, text = 'Quit Game', command = self._exit)
        self._quit_button.pack(side = tk.BOTTOM)

        #chasee's label
        self._chasee_label = tk.Label(self,image=self.chasee_tkphoto)
        self._chasee_label.pack(side = tk.LEFT)

        #restart flag
        self._restart_flag = False

    def _exit(self):
        """
        The function of Status bar to quit the game.
        """
        self._parent.destroy()

    def _restart(self):
        """
        The restart function
        """
        self._restart_flag = not self._restart_flag


class ImageMap(AbstractGrid):
    """
    A new class that extends the BasicMap class. This class will dis-
    play each square rather than rectangles.
    """

    def __init__(self, master, size, **kwargs):
        super().__init__(master, size, size,
                         size*CELL_SIZE, size*CELL_SIZE, **kwargs)

        self._image_counter = 0

    def draw_entity(self, position, tile_type):
        """
        Draw the entity in image format. If there is no entity in 
        a cell, draw a background.
        """
        global entity_image
        global entity_tkimage
        entity_image = Image.open(IMAGES[tile_type])
        entity_tkimage[self._image_counter] = ImageTk.PhotoImage(entity_image)

        self.create_image(*self.get_position_center(position),image = entity_tkimage[self._image_counter])
        self._image_counter += 1

        # Preventing overflow of image data
        if self._image_counter == 400:
            self._image_counter = 0

class ImageGraphicalInterface(BasicGraphicalInterface):
    """
    The ImageGraphicalInterface class will extend the BasicGraphical-
    Interface from task 1. It will also add more function at the same
    time.
    """
    def __init__(self, root, size):
        
        #frame initialize
        self._status_bar = StatusBar(root)
        self._status_bar.pack(side = tk.BOTTOM)
        
        #map initialize
        self._map = ImageMap(root, size)
        self._map.pack(side = tk.LEFT)

        self._inventory = InventoryView(root, size, bg = LIGHT_PURPLE)
        self._inventory.pack(side = tk.RIGHT)
        self._after_id = None
        self._root = root
        self._size = size
        self._min = 0
        self._sec = 0
        self._move_count = 0
        self._is_firing = False
        self._reset = False
        self._play_flag = False
        self._high_score_dict = {}
        
        #menue bar
        self._menubar = tk.Menu(self._root)
        self._root.config(menu=self._menubar)
        self._filemenu = tk.Menu(self._menubar)
        self._menubar.add_cascade(label="File", menu=self._filemenu)

        

    def _step(self, game: AdvancedGame):
        """
        The _step function of ImageGraphicalInterface will extend
        the _step function from task 1, which will count the second.
        """
        #super()._step(game)

        if game.has_lost():
            self._root.after_cancel(self._after_id)
            self._reset = messagebox.askyesno(title='message', message='You lose!\nDo you want to play again?')
            
            if self._reset == True:
                self._after_id = None
                game = advanced_game(MAP_FILE)
                self._sec = 0
                self._min = 0
                self._move_count = 0
                self._status_bar._timer.config(text = 'Timer\n{0} mins {1} seconds'.format(self._min, self._sec))
                self._status_bar._moves_counter.config(text = 'Moves made\n{0} moves'.format(self._move_count))
                self.play(game)
                return
            else:
                self._root.quit()

        game.step()
        self.draw(game)

        self._sec += 1
        if self._sec == 60:
            self._min += 1
            self._sec = 0

        if self._status_bar._restart_flag == True:
            #restar everything
            self._root.after_cancel(self._after_id)
            self._after_id = None
            game = advanced_game(MAP_FILE)
            self._status_bar._restart_flag = False
            self._sec = 0
            self._min = 0
            self._move_count = 0
            self._status_bar._timer.config(text = 'Timer\n{0} mins {1} seconds'.format(self._min, self._sec))
            self._status_bar._moves_counter.config(text = 'Moves made\n{0} moves'.format(self._move_count))
            

            #recall the play function
            self.play(game)
            return

        self._after_id = self._root.after(1000, lambda: self._step(game))
        
        self._status_bar._timer.config(text = 'Timer\n{0} mins {1} seconds'.format(self._min, self._sec))

    def _move(self, game:AdvancedGame, direction: str):
        """
        This _move function will extends the origin _move function
        in task 1 by counting the moves that player has made.
        """

        player = game.get_player()
        items = player.get_inventory()

        # Ensure player has a weapon that they can fire.
        if player.get_inventory().contains(CROSSBOW) and items.has_active(CROSSBOW):
            self._is_firing = True
        else:
            self._is_firing = False

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

            #new window for entering player's name
            self._high_score = tk.Toplevel()
            self._high_score.geometry("300x100")

            prompt_label = tk.Label(self._high_score, text='You won in {0} min adn {1} sec! Enter you name:'.format(self._min, self._sec))
            prompt_label.pack(side=tk.TOP)

            self.player_name = tk.StringVar()

            name_entry = tk.Entry(self._high_score, textvariable=self.player_name)
            name_entry.pack(side=tk.TOP)

            button_frame = tk.Frame(self._high_score)
            button_frame.pack(side=tk.TOP)

            score_save_button = tk.Button(button_frame, text='Enter', command=self.write_score)
            score_save_button.pack(side=tk.LEFT)

            play_again_button = tk.Button(button_frame, text='Enter and play again', command=self.write_score_play)
            play_again_button.pack(side=tk.RIGHT)

            self._high_score.mainloop()

            #self._reset = messagebox.askyesno(title='message', message='You win!\nDo you want to play again?')
            
            if self._reset == True:
                self._after_id = None
                game = advanced_game(MAP_FILE)
                self._sec = 0
                self._min = 0
                self._move_count = 0
                self._status_bar._timer.config(text = 'Timer\n{0} mins {1} seconds'.format(self._min, self._sec))
                self._status_bar._moves_counter.config(text = 'Moves made\n{0} moves'.format(self._move_count))
                self.play(game)
                return
            else:
                self._root.destroy()

        self._move_count += 1

        self._status_bar._moves_counter.config(text = 'Moves made\n{0} moves'.format(self._move_count))        

    def write_score(self):
        """
        record the current score result to the score file.
        """
        #read the old score data
        try:
            score_file = open(HIGH_SCORES_FILE, 'r')
        except FileNotFoundError:
            score_file = open(HIGH_SCORES_FILE, 'w')
            score_file.close()
            score_file = open(HIGH_SCORES_FILE, 'r')

        raw_score = score_file.readlines()
        if len(raw_score) != 0:
            self._high_score_dict = eval(raw_score[0])

        #adding the new record
        self._high_score_dict[self.player_name.get()] = self._min*60 + self._sec

        #write to the text file
        score_file.close()
        score_file = open(HIGH_SCORES_FILE, 'w')
        #clear the old data
        score_file.seek(0)
        score_file.truncate()
        score_file.write(str(self._high_score_dict))

        self._high_score.destroy()

    def write_score_play(self):
        """
        record the score and play again 
        """
        self.write_score()
        self._status_bar._restart_flag == True

    def show_high_score(self, game: AdvancedGame):
        """
        menu bar function 'High Score', pop up a window to show the first
        to third places of player
        """

        #read the score data
        score_file = open(HIGH_SCORES_FILE, 'r')
        raw_score = score_file.readlines()
        raw_score = eval(raw_score[0])#dictionary

        if len(raw_score) == 0:
            raw_score = {'None': ' ', 'None': ' ', 'None': ' '}

        raw_score = sorted((raw_score).items(), key = lambda kv:(kv[1], kv[0]))#list of tuple


        hs = tk.Toplevel()
        hs.title('Top 3')
        hs.geometry("150x300")
        #title
        tk.Label(hs, text='High Score', font='bold', fg='white', bg=DARK_PURPLE).pack(side=tk.TOP, fill='x', ipady=15)

        #first place
        tk.Label(hs, text='{0}: {1} min {2} sec'.format(raw_score[0][0], raw_score[0][1]//60, raw_score[0][1]%60)).pack(side=tk.TOP, ipady=15)

        #second place
        tk.Label(hs, text='{0}: {1} min {2} sec'.format(raw_score[1][0], raw_score[1][1]//60, raw_score[1][1]%60)).pack(side=tk.TOP, ipady=15)
        
        #third place
        tk.Label(hs, text='{0}: {1} min {2} sec'.format(raw_score[2][0], raw_score[2][1]//60, raw_score[2][1]%60)).pack(side=tk.TOP, ipady=15)

        #Done button
        done_button = tk.Button(hs, text='Done', command=hs.destroy).pack(side=tk.BOTTOM)

        hs.mainloop()

    def draw(self, game: AdvancedGame):
        """
        Clears and redraws the view based on the current game state.
        """
        self._map.delete(tk.ALL)
        self._inventory.delete(tk.ALL)
        mapping = game.get_grid().get_mapping()
        player_position = game.get_grid().find_player()
        player = game.get_grid().get_entity(player_position)
        inv = player.get_inventory()
        #inv = game.get_player().get_inventory()

        #draw current map
        for x in range(game.get_grid().get_size()):
            for y in range(game.get_grid().get_size()):

                #draw the background
                self._map.draw_entity(Position(x, y), BACK_GROUND)
                #if there's a entity, draw it
                for position, tile_type in mapping.items():
                    if (x,y) == (position.get_x(), position.get_y()):
                        self._map.draw_entity(Position(x, y), tile_type.display())

        #draw current inventory
        self._inventory.draw(inv)

    def save_file(self, game: AdvancedGame):
        """
        save current, which inclued: timer, move, inventory, map.
        """
        #stop current game
        self._root.after_cancel(self._after_id)

        #saving current status
        timer_sec = self._sec
        timer_min = self._min
        move = self._move_count
        mapping = game.get_grid().get_mapping()#dictionary
        inventory = game.get_player().get_inventory().get_items()#list  

        #pop up window
        save = tk.Toplevel()
        save.title('Save games')
        save.geometry("300x150")

        save_label = tk.Label(save, text='Please enter the path\nthat you want to save:')
        save_label.pack(anchor=tk.CENTER)

        save_path = tk.StringVar()
        save_entry = tk.Entry(save, textvariable=save_path)
        save_entry.pack(anchor=tk.CENTER)

        def save_function():
            saving = open(save_path.get()+'/save_file.txt', 'w')
            saving.write(str(mapping)+'\n')#mapping
            saving.write(str(inventory)+'\n')#inventory
            saving.write(str(timer_min)+'\n')
            saving.write(str(timer_sec)+'\n')#Timer
            saving.write(str(move))#move steps
            saving.close()
            save.destroy()
            #game continue
            self._root.after(1000, lambda: self._step(game))

        save_button = tk.Button(save, text='Save', command=save_function)
        save_button.pack()

        save.mainloop()

    def load_file(self):
        """
        loading the game from the txt save file
        """
        #stop current game
        self._root.after_cancel(self._after_id)
        
        #pop up window
        load = tk.Toplevel()
        load.title('Load games')
        load.geometry("300x150")

        load_label = tk.Label(load, text='Please enter the path\nthat you want to load:')
        load_label.pack(anchor=tk.CENTER)

        load_path = tk.StringVar()
        load_entry = tk.Entry(load, textvariable=load_path)
        load_entry.pack(anchor=tk.CENTER)

        def load_function():

            loading = open(load_path.get()+'/save_file.txt', 'r')
            load_list = list(enumerate(loading))

            #load game data
            mapping = load_list[0][1][:-1]
            inventory = load_list[1][1]
            self._min = int(load_list[2][1][0])
            self._sec = int(load_list[3][1][0])
            self._move_count = int(load_list[4][1])

            #loading the timer and move counter
            self._status_bar._timer.config(text = 'Timer\n{0} mins {1} seconds'.format(self._min, self._sec))
            self._status_bar._moves_counter.config(text = 'Moves made\n{0} moves'.format(self._move_count))
            
            #recreating the entity wit position in game
            mapping = mapping[1:-1]
            mapping = mapping.split('), ')
            temp_entity = None
            temp_position = None
            grid = Grid(self._size)

            for entity in mapping:
                entity_display = entity[16]
                if entity_display == HOSPITAL:
                    if len(entity[16:]) == 9:
                        temp_entity = Hospital()
                        temp_position = Position(int(entity[9]), int(entity[12]))
                    else:
                        temp_entity = HoldingPlayer()
                        temp_position = Position(int(entity[9]), int(entity[12]))
                elif entity_display == ZOMBIE:
                    temp_entity = Zombie()
                    temp_position = Position(int(entity[9]), int(entity[12]))
                elif entity_display == TRACKING_ZOMBIE:
                    temp_entity = TrackingZombie()
                    temp_position = Position(int(entity[9]), int(entity[12]))
                elif entity_display == CROSSBOW:
                    temp_entity = Crossbow()
                    temp_position = Position(int(entity[9]), int(entity[12]))
                elif entity_display == GARLIC:
                    temp_entity = Garlic()
                    temp_position = Position(int(entity[9]), int(entity[12]))
                
                grid.add_entity(temp_position, temp_entity)

            #create the game
            game = AdvancedGame(grid)

            #recreate the inventory of loading game
            inventory = inventory[1:-1]
            inventory = inventory.split(',')
            player_position = game.get_grid().find_player()
            player = game.get_grid().get_entity(player_position)
            inv = player.get_inventory()
            temp_item = None
            temp_step = None

            for item in inventory:
                temp_step = int(item.split('(')[1].split(')')[0])
                if item[0] == CROSSBOW:
                    temp_item = Crossbow()
                    temp_item.toggle_active()
                    for i in range(5-temp_step):
                        temp_item.hold()
                    temp_item.toggle_active()
                    inv._items.append(temp_item)
                elif item[0] == GARLIC:
                    temp_item = Garlic()
                    temp_item.toggle_active()
                    for i in range(10-temp_step):
                        temp_item.hold()
                    temp_item.toggle_active()
                    inv._items.append(temp_item)

            loading.close()
            load.destroy()
            # start the new game
            self.play(game)
                    
        load_button = tk.Button(load, text='Load', command=load_function)
        load_button.pack()

        load.mainloop()

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
        
        if self._play_flag == False:
            self._filemenu.add_command(label="Save File", command=lambda: self.save_file(game))
            self._filemenu.add_command(label="Load File", command=self.load_file)
            self._filemenu.add_command(label="High Scores", command=lambda: self.show_high_score(game))

        self._play_flag = True
        
        self._step(game)

        self._root.mainloop()

    


def main():
    
    root = tk.Tk()
    root.title(TITLE)
    game = advanced_game(MAP_FILE)
    gui = ImageGraphicalInterface(root, game.get_grid().get_size())
    gui.play(game)

    root.mainloop()

if __name__ == "__main__":
    main()
