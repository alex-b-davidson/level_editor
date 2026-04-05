import pygame
import tkinter.filedialog

# TODO create function that allows choosing directory in new module file_manager.py. get a click on the icon from gui, set a flag as True then call the function.
# function will need to update global tileset_list

# ── Global state ──────────────────────────────────────────────────────────────

tile_size = 16
canv_x, canv_y = 100, 100 # 100, 48
current_layer = 0 # starting from 0 because user will scroll through using modulo. Also present in gui.get_cv_selection()
max_layer = 4
terrain_type = None

# create dict for canvas
canv_dict = {}

def populate_empty_canv_dict(empty: pygame.Surface):
    global canv_dict
    for layer in range(current_layer, max_layer+1, 1):
        for col in range(canv_x):
         for row in range(canv_y):
            canv_dict[(col, row, layer)] = (empty, None) 


def write_tileset_selecton(col_index: int, row_index: int, selection: pygame.Surface, clicking_on_icons, tileset_drag):
    """Make entry into canvas dictionary with img data, and type data"""

    if not clicking_on_icons and not tileset_drag: # flag for cursor over toolbar and tileset drag so it doesn't auto draw to canvas when mouse > tileset bounds
        for tiles_in_x in range(0, selection.get_width()//tile_size):
            for tiles_in_y in range(0, selection.get_height()//tile_size):

                single_tile = selection.subsurface((tiles_in_x*tile_size, tiles_in_y*tile_size, tile_size, tile_size)).convert_alpha()
                single_tile = single_tile.copy().convert_alpha()
                if col_index >= 0 and col_index < canv_x + 1 and row_index >= 0 and row_index < canv_y + 1:
                    if col_index + tiles_in_x < canv_x + 1 and row_index + tiles_in_y < canv_y + 1: # ensure selection is only written if within canvas bounds
                        canv_dict[(col_index+tiles_in_x, row_index+tiles_in_y, current_layer)] = (single_tile, terrain_type)


