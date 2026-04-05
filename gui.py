import pygame
import level
import file_manager
import math
import os
import sfx
import time

time.sleep(0.5)

# ------------------------------------------------------------------------------
# Global state
# These variables are shared across functions and updated each frame.
# They are declared here at module level so functions can modify them via
# 'global' declarations without accidentally creating local copies.
# ------------------------------------------------------------------------------

#file_manager.tileset_list = []
#file_manager.tileset = None              # The loaded file_manager.tileset image surface
tileset_index = 0           # will cycle based on click in get_clicks_on_icons()
ts_active_index = 0
empty_tile = None
#file_manager.tileset_width = 0           # Width of the file_manager.tileset in pixels
#file_manager.tileset_height = 0          # Height of the file_manager.tileset in pixels
cursor_tile = None          # Cursor image displayed when hovering over the file_manager.tileset
toolbar_on_right = None          # Toolbar image displayed at the top of the screen

cursor_over_tileset = False # True when the mouse is over the file_manager.tileset panel
cursor_over_canvas = False  # True when the mouse is over the canvas area

tileset_drag = False        # True while the user is dragging to make a selection on the file_manager.tileset
tileset_drag_start = (0, 0)         # Tile index (col, row) where the drag started
tileset_drag_end = (0, 0)   # Tile index (col, row) where the drag currently ends
has_ts_selection = False       # True once the user has completed at least one file_manager.tileset selection

canvas_drag = False # True while user is right-click dragging on canvas
canvas_drag_start = (0, 0) # canvas index where the drag starts
canvas_drag_end = (0, 0) # canvas indec where drag currently ends
has_cv_selection = False # True once the use has at least one canvas tile selectionvia dragging
cv_selection_captured = False # becomes true only when selection (mouseup) is made, then drawn and set to false again



# Canvas pan state.
# canvas_offset_x/y are the pixel position at which the canvas surface is blitted.
# They are updated by update_canvas_pan() each frame.
canvas_offset_x = 0        # Horizontal pixel offset for canvas panning
canvas_offset_y = 0        # Vertical pixel offset for canvas panning (set to toolbar height in load_assets)
scroll_canvas = False         # True while the user is panning the canvas with middle-click
scroll_canvas_origin = None   # Mouse position at the start of the current pan gesture
canvas_width = 0            # Canvas surface width in pixels (set in draw_canvas)
canvas_height = 0           # Canvas surface height in pixels (set in draw_canvas)

# Accumulates raw vertical mouse delta during panning.
# canvas_offset_y only advances in tile_size steps, so we need to track
# sub-tile mouse movement here until it exceeds one full tile.
canvas_pan_accumulator_y = 0
canvas_pan_accumulator_x = 0

drawing = False # active when left clicking over the canvas

# toolbar icon flags
cursor_over_left_arrow = False
cursor_over_right_arrow = False
cursor_over_layer_icon = False
cursor_over_layer_eye = False
layer_eye_pressed = False
cursor_over_select_active_layer = False
select_active_layer = False
cursor_over_ts_dir_icon = False
ts_dir_icon_pressed = False

# numbers
all_nums = None
num_list = []

clicking_on_icons = False # need flag to not draw when clicking

# ------------------------------------------------------------------------------
# Asset loading
# ------------------------------------------------------------------------------

def load_assets():
    """Load all images used by the GUI. Call once after pygame.init().
    Sets canvas_offset_y to toolbar height so the canvas starts below the toolbar.
    Returns (file_manager.tileset_width, file_manager.tileset_height)."""
    global cursor_tile, toolbar_on_right, toolbar_corner, top_right_corner, bottom_left_corner, bottom_right_corner 
    global toolbar_dark_line, toolbar_light_line, canvas_offset_y, toolbar_top_line, toolbar_bottom_line, toolbar_left_line, toolbar_right_line
    global empty_tile, arrows_whole, arrow_inactive_left, arrow_inactive_right, arrow_active_left, arrow_active_right, arrow_pressed_left, arrow_pressed_right
    global ts_label, layer_active, layer_inactive, all_nums, num_list, eye_inactive, eye_active, eye_pressed, select_active_layer_active
    global select_active_layer_inactive, select_active_layer_clicked, select_ts_dir_inactive, select_ts_dir_active


    # file_manager.tileset_list = [pygame.image.load(rf'assets\tilesets\{file_manager.tileset}').convert_alpha().copy() for file_manager.tileset in os.listdir(r'assets\tilesets')]
    # #file_manager.tileset = pygame.image.load(r'assets\tilesets\tileset_2.png').convert_alpha()
    # file_manager.tileset = file_manager.tileset_list[0]
    # file_manager.tileset_width = file_manager.tileset.get_width()
    # file_manager.tileset_height = file_manager.tileset.get_height()
    empty_tile = pygame.image.load(r'assets\empty.png').convert()
    empty_tile.set_colorkey((253, 77, 211))

    toolbar_on_right = pygame.image.load(r'assets\toolbar_1.png')

    _toolbar_corners_and_sides = pygame.image.load(r'assets\toolbar_shading.png').convert_alpha()
    # get the three single tiles ready to blit .copy() not necessary here
    toolbar_corner = _toolbar_corners_and_sides.subsurface((0, 0, level.tile_size, level.tile_size))
    top_right_corner = pygame.transform.flip(toolbar_corner, flip_x=True, flip_y=False)
    bottom_left_corner = pygame.transform.flip(toolbar_corner, flip_x=False, flip_y=True)
    bottom_right_corner = pygame.transform.flip(toolbar_corner, flip_x=True, flip_y=True)

    toolbar_dark_line = _toolbar_corners_and_sides.subsurface((level.tile_size, 0, level.tile_size, level.tile_size))
    toolbar_light_line = _toolbar_corners_and_sides.subsurface((level.tile_size*2, 0, level.tile_size, level.tile_size))
    
    toolbar_top_line = pygame.transform.scale(toolbar_dark_line, (file_manager.tileset_width - level.tile_size*2, level.tile_size))
    toolbar_bottom_line = pygame.transform.scale(pygame.transform.flip(toolbar_dark_line, False, True), (file_manager.tileset_width - level.tile_size*2, level.tile_size))
    toolbar_left_line = toolbar_light_line
    toolbar_right_line = pygame.transform.flip(toolbar_light_line, True, False)

    # load arrow icons for the toolbar
    arrows_whole = pygame.image.load(r'assets\arrows.png').convert_alpha()
    arrow_inactive_left = arrows_whole.subsurface((0, 0, level.tile_size*2, level.tile_size*2))
    arrow_inactive_right = arrows_whole.subsurface((level.tile_size*2, 0, level.tile_size*2, level.tile_size*2))
    arrow_active_left = arrows_whole.subsurface((level.tile_size*4, 0, level.tile_size*2, level.tile_size*2))
    arrow_active_right = arrows_whole.subsurface((level.tile_size*6, 0, level.tile_size*2, level.tile_size*2))
    arrow_pressed_left = arrows_whole.subsurface((level.tile_size*8, 0, level.tile_size*2, level.tile_size*2))
    arrow_pressed_right = arrows_whole.subsurface((level.tile_size*10, 0, level.tile_size*2, level.tile_size*2))
    ts_label = pygame.image.load(r'assets\ts_label.png')

    # load layer icons
    layer_inactive = pygame.image.load(r'assets\layer_inactive.png').convert_alpha()
    layer_active = pygame.image.load(r'assets\layer_active.png')
    eye_inactive = pygame.image.load(r'assets\eye_inactive.png').convert_alpha()
    eye_active = pygame.image.load(r'assets\eye_active.png').convert_alpha()
    eye_pressed = pygame.image.load(r'assets\eye_clicked.png').convert_alpha()
    select_active_layer_inactive = pygame.image.load(r'assets\select_active_layer_inactive.png').convert_alpha()
    select_active_layer_active = pygame.image.load(r'assets\select_active_layer_active.png').convert_alpha()
    select_active_layer_clicked = pygame.image.load(r'assets\select_active_layer_clicked.png').convert_alpha()

    # load select_ts_dir icons
    select_ts_dir_inactive = pygame.image.load(r'assets\load_tilesets_inactive.png').convert_alpha()
    select_ts_dir_active = pygame.image.load(r'assets\load_tilesets_active.png').convert_alpha()

    all_nums = pygame.image.load(r'assets\numbers.png').convert_alpha()
    num_list = [all_nums.subsurface(x, 0, 32, 32) for x in range(0, all_nums.get_width(), 32)]


    return file_manager.tileset_width, file_manager.tileset_height


# ------------------------------------------------------------------------------
# Update functions
# These are called every frame in main.py's UPDATE section.
# ------------------------------------------------------------------------------

def get_snapped_tileset_pos(screen: pygame.Surface):
    """Return the snapped (x, y) pixel position of the tile under the cursor on the file_manager.tileset.
    'Snapped' means locked to the nearest tile boundary.
    Also updates cursor_over_tileset.
    Returns (0, 0) if the cursor is not over the file_manager.tileset."""
    global cursor_over_tileset

    cursor = pygame.mouse.get_pos()
    cv_snapped_x = 0
    cv_snapped_y = 0

    # The file_manager.tileset panel is pinned to the right edge of the screen
    tileset_x = screen.get_width() - file_manager.tileset_width
    cursor_over_tileset = (cursor[0] >= tileset_x and cursor[1] < file_manager.tileset_height)

    if cursor_over_tileset:
        # Convert pixel position to tile index, then back to snapped pixel position
        col = (cursor[0] - tileset_x) // level.tile_size
        row = cursor[1] // level.tile_size
        cv_snapped_x = col * level.tile_size + tileset_x
        cv_snapped_y = row * level.tile_size

    return cv_snapped_x, cv_snapped_y


def get_canvas_indices(screen: pygame.Surface):
    """Return the (col, row) tile indices under the mouse cursor on the canvas.
    Also updates cursor_over_canvas.
    Returns None if the cursor is over the file_manager.tileset or toolbar."""
    global cursor_over_canvas

    cursor = pygame.mouse.get_pos()
    cursor_over_canvas = not cursor_over_tileset

    # Ignore the toolbar area — the canvas only starts below it
    if cursor_over_canvas and cursor[0] < screen.get_width() - file_manager.tileset_width:
        # Subtract the canvas offset to account for panning, then convert to tile indices
        col = (cursor[0] - canvas_offset_x) // level.tile_size
        row = (cursor[1] - canvas_offset_y) // level.tile_size
        return int(col), int(row)


def update_tileset_drag_end(screen: pygame.Surface, cv_snapped_x, cv_snapped_y):
    """While a file_manager.tileset drag is active, update the tile index of the drag's current end point.
    Called every frame so the selection rect tracks the cursor in real time."""
    global tileset_drag_end

    tileset_x = screen.get_width() - file_manager.tileset_width

    if tileset_drag and cursor_over_tileset:
        # Convert snapped pixel position back to tile indices
        tileset_drag_end = ((cv_snapped_x - tileset_x) // level.tile_size, cv_snapped_y // level.tile_size)

def update_canvas_drag_end(cv_ind_x: int, cv_ind_y: int):
    """While a canvas drag is active, update the tile index of the drag's current end point.
    Called every frame so the selection rect tracks the cursor in real time."""
    global canvas_drag_end

    if canvas_drag and cursor_over_canvas:
        canvas_drag_end = (cv_ind_x, cv_ind_y)


def update_tileset_selection_cursor(screen: pygame.Surface):
    """Calculate and return a pygame.Rect representing the current selection on the file_manager.tileset.
    Handles dragging in any direction (up-left, down-right, etc.) using min/max.
    Clips the result to the file_manager.tileset panel bounds.
    Returns None if no drag or selection is active."""

    tileset_x = screen.get_width() - file_manager.tileset_width

    if tileset_drag or has_ts_selection:
        # Use min/max so the rect is always correctly oriented regardless of drag direction
        x = min(tileset_drag_start[0], tileset_drag_end[0]) * level.tile_size + tileset_x
        y = min(tileset_drag_start[1], tileset_drag_end[1]) * level.tile_size
        width = abs(tileset_drag_end[0] - tileset_drag_start[0]) * level.tile_size + level.tile_size
        height = abs(tileset_drag_end[1] - tileset_drag_start[1]) * level.tile_size + level.tile_size

        bounds_rect = pygame.Rect((screen.get_width() - file_manager.tileset_width, 0, file_manager.tileset_width, file_manager.tileset_height))
        selection_rect = pygame.Rect((x, y, width, height))
        clipped_rect = selection_rect.clip(bounds_rect)
        return clipped_rect

def update_canvas_selection_cursor(screen:pygame.Surface, cv_ind_x, cv_ind_y):
    """Update the selection rect from the canvas"""
    if canvas_drag or has_cv_selection:
        tileset_drag = False
        x = int(min((canvas_drag_start[0], canvas_drag_end[0]))*level.tile_size)
        y = int(min((canvas_drag_start[1], canvas_drag_end[1]))*level.tile_size)
        width = abs(canvas_drag_end[0] - canvas_drag_start[0]) * level.tile_size + level.tile_size
        height = abs(canvas_drag_end[1] - canvas_drag_start[1]) * level.tile_size + level.tile_size

        
        # here get the tiles in selection for x and y !! try after using simply cv_ind
        tiles_in_x = list(range(x//level.tile_size, (x+width)//level.tile_size, 1))
        tiles_in_y = list(range(y//level.tile_size, (y+height)//level.tile_size, 1))

        # check if hard limits is smaller and set that to clipped x and y (don't need soft because of clip below)
        hard_limited_x = [i for i in tiles_in_x if i < level.canv_x + 1]
        hard_limited_y = [i for i in tiles_in_y if i < level.canv_y + 1]

        clipped_x = len(hard_limited_x)
        clipped_y = len(hard_limited_y)

        # get bounds rect
        bounds_rect = pygame.Rect((0, 0, screen.get_width()-file_manager.tileset_width, screen.get_height()))

        # set selection rect
        selection_rect = pygame.Rect((x+canvas_offset_x, y+canvas_offset_y, clipped_x*level.tile_size, clipped_y*level.tile_size))

        # clip selection to bounds
        clipped_rect = selection_rect.clip(bounds_rect)
        return clipped_rect
    

def update_canvas_pan(screen: pygame.Surface):
    """Update canvas_offset_x/y based on middle-click mouse dragging.
    Vertical panning moves in tile_size steps using an accumulator so the
    canvas grid always stays aligned with the toolbar edge.
    Clamps both offsets so the canvas cannot be panned beyond its boundaries."""
    global canvas_offset_x, canvas_offset_y, scroll_canvas_origin, canvas_pan_accumulator_y, canvas_pan_accumulator_x

    if scroll_canvas and scroll_canvas_origin is not None:
        current_mouse_pos = pygame.mouse.get_pos()

        # Horizontal panning: free pixel movement (no snapping needed)
        canvas_pan_accumulator_x += current_mouse_pos[0] - scroll_canvas_origin[0]
        while abs(canvas_pan_accumulator_x) >= level.tile_size:

            canvas_offset_x += math.copysign(level.tile_size, current_mouse_pos[0] - scroll_canvas_origin[0])
            canvas_pan_accumulator_x -= math.copysign(level.tile_size, current_mouse_pos[0] - scroll_canvas_origin[0])
        # Vertical panning: accumulate raw delta, then advance by whole tiles only.
        # This keeps the canvas grid aligned with the toolbar at all times.
        canvas_pan_accumulator_y += current_mouse_pos[1] - scroll_canvas_origin[1]
        while abs(canvas_pan_accumulator_y) >= level.tile_size:
            # Move one tile in the direction of travel, then reduce the accumulator
            canvas_offset_y += math.copysign(level.tile_size, current_mouse_pos[1] - scroll_canvas_origin[1])
            canvas_pan_accumulator_y -= math.copysign(level.tile_size, current_mouse_pos[1] - scroll_canvas_origin[1])

        scroll_canvas_origin = current_mouse_pos

    # Clamp horizontal offset.
    # Only restrict if the canvas is wider than the available area (screen minus file_manager.tileset panel).
    if canvas_width > screen.get_width() - file_manager.tileset_width:
        neg_raw_x = -(canvas_width - screen.get_width())
        neg_clamp_x = -(-(neg_raw_x) // level.tile_size * level.tile_size)
        canvas_offset_x = pygame.math.clamp(canvas_offset_x, neg_clamp_x-level.tile_size - file_manager.tileset_width, 0)
    else:
        canvas_offset_x = 0

    # Clamp vertical offset.
    # Only restrict if the canvas is taller than the available area (screen minus toolbar).
    # The maximum is toolbar_height (canvas flush with toolbar bottom).
    # The minimum is calculated so the last row of tiles is still visible at the screen bottom.
    # Because tile-snapped panning requires the minimum to also be a tile boundary,
    # we round it up (toward zero) to the nearest tile using double-negation floor division.
    
    if canvas_height > screen.get_height():
        neg_raw_y = -(canvas_height - (screen.get_height()))
        neg_clamp_y = -((-neg_raw_y) // level.tile_size * level.tile_size)
        canvas_offset_y = pygame.math.clamp(canvas_offset_y, neg_clamp_y-level.tile_size, 0)
    else:
        canvas_offset_y = 0

def update_screen_layout(screen: pygame.Surface):
    """sets the x for icons in toolbar after screen resize"""

    arrow_icon_x = screen.get_width() - file_manager.tileset_width + level.tile_size*2
    ts_label_x = screen.get_width() - file_manager.tileset_width + file_manager.tileset_width//2
    layer_icon_x = screen.get_width() - file_manager.tileset_width + file_manager.tileset_width//2 - layer_inactive.get_width()//2
    layer_eye_x = layer_icon_x + (layer_inactive.get_width())
    select_active_layer_icon_x = layer_icon_x - level.tile_size*2
    select_ts_dir_icon_y = screen.get_height() - level.tile_size*3

    screen.blit(layer_active, (layer_icon_x, file_manager.tileset_height + level.tile_size)) # TODO should be moved to DRAW?
    return(arrow_icon_x, ts_label_x, layer_icon_x, layer_eye_x, select_active_layer_icon_x, select_ts_dir_icon_y) 




def update_toolbar_flags(arrow_icon_x, layer_icon_x, layer_eye_x, sal_icon_x, ts_dir_icon_y): # parameters from update_screen_layout()
    """updates global flags for cursor over toolbal icons"""
    global cursor_over_left_arrow, cursor_over_right_arrow, cursor_over_layer_icon, cursor_over_layer_eye, cursor_over_select_active_layer, cursor_over_ts_dir_icon

    left_arrow_rect = pygame.Rect((arrow_icon_x, file_manager.tileset_height+level.tile_size, arrow_active_left.get_width(), arrow_active_left.get_height()))
    right_arrow_rect = pygame.Rect((arrow_icon_x+file_manager.tileset_width- level.tile_size*6, file_manager.tileset_height+level.tile_size, arrow_active_left.get_width(), arrow_active_left.get_height()))

    layer_icon_rect = pygame.Rect((layer_icon_x, file_manager.tileset_height+level.tile_size*4, layer_inactive.get_width(), layer_inactive.get_height()))
    layer_eye_rect = pygame.Rect((layer_eye_x, file_manager.tileset_height+level.tile_size*4, eye_inactive.get_width(), eye_inactive.get_height()))
    select_active_layer_rect = pygame.Rect((sal_icon_x, file_manager.tileset_height+level.tile_size*4, select_active_layer_active.get_width(), select_active_layer_active.get_height()))

    ts_dir_rect = pygame.Rect((arrow_icon_x-level.tile_size, ts_dir_icon_y, select_ts_dir_inactive.get_width(), select_ts_dir_inactive.get_height()))


    if left_arrow_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_left_arrow = True
    else:
        cursor_over_left_arrow = False
    
    if right_arrow_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_right_arrow = True
    else:
        cursor_over_right_arrow = False
    
    if layer_icon_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_layer_icon = True
    else:
        cursor_over_layer_icon = False

    if layer_eye_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_layer_eye = True
    else:
        cursor_over_layer_eye = False

    if select_active_layer_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_select_active_layer = True
    else:
        cursor_over_select_active_layer = False

    if ts_dir_rect.collidepoint(pygame.mouse.get_pos()):
        cursor_over_ts_dir_icon = True
    else:
        cursor_over_ts_dir_icon  =False


def update_current_tileset():
    """Change the file_manager.tileset when arrows are clicked in the toolbar"""
    #global file_manager.tileset

    file_manager.tileset = file_manager.tileset_list[tileset_index] # TODO call this after event choose file_manager.tileset

def update_flag_mouse_over_toolbar(screen: pygame.Surface):
    """update the clicking_on_icons bool if mouse x is over toolbar"""
    global clicking_on_icons

    if pygame.mouse.get_pos()[0] > screen.get_width() - file_manager.tileset_width and not cursor_over_tileset:
        clicking_on_icons = True
    else:
        clicking_on_icons = False

# ------------------------------------------------------------------------------
# Drawing functions
# These are called every frame in main.py's DRAW section.
# ------------------------------------------------------------------------------

def draw_tileset(screen: pygame.Surface):
    """Blit the file_manager.tileset to the right edge of the screen.
    The magenta rect behind it acts as a background/debug fill."""
    pygame.draw.rect(screen, (150, 0, 200), (screen.get_width() - file_manager.tileset_width, 0, file_manager.tileset_width, file_manager.tileset_height))
    screen.blit(file_manager.tileset, (screen.get_width() - file_manager.tileset_width, 0))


def draw_canvas():
    """Build and return the canvas grid surface.
    Draws a grid of lines at tile_size intervals.
    Also updates the canvas_width and canvas_height globals used for clamping."""
    global canvas_width, canvas_height

    canvas = pygame.Surface((
        level.canv_x * level.tile_size + level.tile_size + 1,
        level.canv_y * level.tile_size + level.tile_size + 1
    ))

    # Vertical grid lines
    for row in range(0, level.canv_x * level.tile_size + level.tile_size + 1, level.tile_size):
        pygame.draw.line(canvas, (50, 50, 50), (row, 0), (row, canvas.get_height()))
    # Horizontal grid lines
    for col in range(0, level.canv_y * level.tile_size + level.tile_size + 1, level.tile_size):
        pygame.draw.line(canvas, (50, 50, 50), (0, col), (canvas.get_width(), col))

    canvas_width = canvas.get_width()
    canvas_height = canvas.get_height()
    return canvas


def draw_hovering_tile_cursor(screen: pygame.Surface, cv_snapped_x, cv_snapped_y):
    """Draw a single-tile highlight under the cursor when hovering over the file_manager.tileset.
    Hidden while actively dragging a selection."""
    if not tileset_drag and cursor_over_tileset:
        pygame.draw.rect(screen, (0, 255, 255),
                         (cv_snapped_x, cv_snapped_y, level.tile_size, level.tile_size), 1)


def draw_tileset_selection_cursor(screen: pygame.Surface, selection_rect):
    """Draw the selection rectangle during and after a drag on the file_manager.tileset.
    Clips the rect to the file_manager.tileset panel so it never draws outside the panel."""
    if selection_rect is not None:
        bounds_rect = pygame.Rect(screen.get_width() - file_manager.tileset_width, 0, file_manager.tileset_width, file_manager.tileset_height)
        clipped_cursor = selection_rect.clip(bounds_rect)
        pygame.draw.rect(screen, (255, 255, 255), clipped_cursor, 1)


def draw_canvas_cursor(screen: pygame.Surface, selection: pygame.Rect, ind_x, ind_y):
    """Draw a snapped cursor rect on the canvas sized to match the current selection.
    Shows a single-tile rect if no selection exists, otherwise matches the selection dimensions.
    Hidden while panning (scroll_canvas) or when the cursor is over the toolbar."""
    current_pos = pygame.mouse.get_pos()
    cv_snapped_x = 0
    cv_snapped_y = toolbar_on_right.get_height()

    # Only draw when: over the canvas, below the toolbar, and not currently panning
    if not canvas_drag and not cursor_over_tileset and current_pos[0] < screen.get_width() - file_manager.tileset_width and not scroll_canvas and ind_x < level.canv_x + 1 and ind_y < level.canv_y + 1:
        # Convert screen position to tile index accounting for canvas pan offset,
        # then convert back to snapped screen position
        col = (current_pos[0] - canvas_offset_x) // level.tile_size
        row = (current_pos[1] - canvas_offset_y) // level.tile_size
        cv_snapped_x = col * level.tile_size + canvas_offset_x
        cv_snapped_y = row * level.tile_size + canvas_offset_y

        if selection is None:
            pygame.draw.rect(screen, (255, 0, 0), (cv_snapped_x, cv_snapped_y, level.tile_size, level.tile_size), 1)
        else:
            
            # restrict cursor when selection is bigger than canvas

            pygame.draw.rect(screen, (255, 0, 0), (cv_snapped_x, cv_snapped_y, selection.width, selection.height), 1)

def draw_canvas_selection_cursor(screen: pygame.Surface, selection_rect: pygame.Rect, cv_ind_x: int, cv_ind_y: int):
    """Draw a resizable cursor on the canvas while dragging on the canvas"""
    global has_ts_selection
    
    if canvas_drag:
        has_ts_selection = False
        pygame.draw.rect(screen, (0, 255, 0), selection_rect, 1)


def draw_subsurface_tileset(screen: pygame.Surface, selection: pygame.Surface, sub_x, sub_y):
    """Blit the current file_manager.tileset selection image onto the canvas at the given tile indices.
    Used to preview the tile placement before the user clicks.
    Hidden while panning so the preview doesn't drift out of sync with the grid."""
    if not canvas_drag and selection is not None and not cursor_over_tileset and not scroll_canvas and not tileset_drag and sub_x < level.canv_x + 1 and sub_y < level.canv_y + 1 and not pygame.mouse.get_pos()[0] > screen.get_width()-file_manager.tileset_width:

        # check if any of the selection falls outside the canvas
        col_coords_x = list(range(sub_x, sub_x+(selection.get_width()//level.tile_size), 1))
        col_coords_y = list(range(sub_y, sub_y+(selection.get_height()//level.tile_size), 1))

        # use list comprehension to build list of x, y coords under canv_x + 1 and canv_y + 1 (hard limit of drawing)
        hard_limited_coords_x = [i for i in col_coords_x if i < level.canv_x + 1]
        hard_limited_coords_y = [i for i in col_coords_y if i < level.canv_y + 1]

        # Do the same for x, y, under tileset_x and screen.get(height) (soft limit of drawing)
        soft_limited_coords_x = [i for i in col_coords_x if i*level.tile_size+canvas_offset_x < (screen.get_width() - file_manager.tileset_width)]
        soft_limited_coords_y = [i for i in col_coords_y if i*level.tile_size+canvas_offset_y < screen.get_height()]


        clipped_x = min(len(soft_limited_coords_x), len(hard_limited_coords_x))
        clipped_y = min(len(soft_limited_coords_y), len(hard_limited_coords_y))


        bounds_rect = pygame.Rect((0, 0, clipped_x*level.tile_size, clipped_y*level.tile_size)) # starts at 0, 0 because new surface not at sub_x, sub_y
        clipped_selection = selection.subsurface(bounds_rect)
        screen.blit(clipped_selection, (
        sub_x * level.tile_size + canvas_offset_x,
        sub_y * level.tile_size + canvas_offset_y))
        return(pygame.Rect(clipped_selection.get_rect()))

def draw_cv_subsurface(screen: pygame.Surface, selection: pygame.Surface, tiles_in_x, tiles_in_y):
    """draws the selection from the canvas"""
    selection_subsurface = selection.subsurface(selection)
    screen.blit(selection_subsurface, (min(tiles_in_x) * level.tile_size + canvas_offset_x, min(tiles_in_y) * level.tile_size + canvas_offset_y))

def draw_from_dict(screen: pygame.Surface):
    """Redraw all placed tiles (withing visible window) from canv_dict onto the screen every frame.
    Keys are (col, row, layer) tile indices; values are (surface, terrain_type) pairs.
    Tile positions are offset by canvas_offset_x/y to account for panning."""

    # get cols and rows in screen size
    tiles_in_x = list(range(int(0 - canvas_offset_x)//level.tile_size, int(screen.get_width() - file_manager.tileset_width - canvas_offset_x)//level.tile_size, 1))
    tiles_in_y = list(range(int(0 - canvas_offset_y)//level.tile_size, int(screen.get_height() - canvas_offset_y)//level.tile_size, 1))

    for layer in range(0, level.max_layer+1, 1):
            for col in tiles_in_x:
                for row in tiles_in_y:

                    key = (col, row, layer)

                    if key in level.canv_dict:

                        img, tile_type = level.canv_dict[key]
                        if layer_eye_pressed:
                            if level.current_layer != layer:
                                img.set_alpha(100)
                            else:
                                img.set_alpha(255) # ensures full alpha when selecting hidden layers
                        else:
                            img.set_alpha(255)

                        blit_x = col * level.tile_size +canvas_offset_x
                        blit_y = row * level.tile_size + canvas_offset_y
                        screen.blit(img.copy(), (blit_x, blit_y))

    


def draw_toolbar(screen: pygame.Surface):
    """Draw the toolbar across the top of the screen from x=0 to the file_manager.tileset panel edge.
    Scales the toolbar image horizontally to fill the available width."""
    
    x = screen.get_width() - file_manager.tileset_width
    y = file_manager.tileset_height
    width = file_manager.tileset_width
    height = screen.get_height() - file_manager.tileset_height
    toolbar = pygame.transform.scale(toolbar_on_right, (width, height))
    #screen.blit(toolbar, (screen.get_width() - file_manager.tileset_width, file_manager.tileset_height, toolbar.get_width(), toolbar.get_height()))
    screen.blit(toolbar, (x, y))

    # Decoration of toolbar
    # blit the rotated corners to the toolbar. They should go at +16 (not level.tilesize)

    # blit the dark/light lines to the toolbar

    screen.blit(toolbar_corner, (x, y))
    screen.blit(top_right_corner, (screen.get_width() - 16, y))
    screen.blit(bottom_left_corner, (x, screen.get_height() - 16))
    screen.blit(bottom_right_corner, (screen.get_width() - 16, screen.get_height() - 16))

    # draw the top and bottom lines at static file_manager.tileset coords
    screen.blit(toolbar_top_line, (x+level.tile_size, y))
    screen.blit(toolbar_bottom_line, (x+level.tile_size, screen.get_height()-level.tile_size))

    # for the side lines, I need to get the (screen height - tile size) - (file_manager.tileset height + tile size)
    line_length = (screen.get_height()-level.tile_size) - (y+level.tile_size)
    trans_l_line = pygame.transform.smoothscale(toolbar_left_line, (level.tile_size, line_length))
    trans_r_line = pygame.transform.smoothscale(toolbar_right_line, (level.tile_size, line_length))
    screen.blit(trans_l_line, (x, y+level.tile_size))
    screen.blit(trans_r_line, (screen.get_width()-level.tile_size, y+level.tile_size))

def draw_toolbar_icons(screen:pygame.Surface, arrow_icon_x, ts_label_x, layer_icon_x, layer_eye_x, sal_icon_x, ts_dir_icon_y):
    """Draw the icons on the toolbar"""

    ts_label_y = file_manager.tileset_height+level.tile_size
    screen.blit(ts_label, (ts_label_x-ts_label.get_width()//2, ts_label_y))

    if cursor_over_left_arrow:
        screen.blit(arrow_active_left, (arrow_icon_x, file_manager.tileset_height + level.tile_size))
    else:
        screen.blit(arrow_inactive_left, (arrow_icon_x, file_manager.tileset_height + level.tile_size))

    if cursor_over_right_arrow:
        screen.blit(arrow_active_right, (arrow_icon_x+file_manager.tileset_width-level.tile_size*6, file_manager.tileset_height+level.tile_size))
    else:
        screen.blit(arrow_inactive_right, (arrow_icon_x+file_manager.tileset_width-level.tile_size*6, file_manager.tileset_height+level.tile_size))


    if cursor_over_layer_icon:
        screen.blit(layer_active, (layer_icon_x, file_manager.tileset_height+level.tile_size*4))
    else:
        screen.blit(layer_inactive, (layer_icon_x, file_manager.tileset_height+level.tile_size*4))
    
    # draw layer number
    screen.blit(num_list[level.current_layer+1], (layer_icon_x+level.tile_size*5, file_manager.tileset_height+level.tile_size*4))

    if not layer_eye_pressed:
        if cursor_over_layer_eye:
            screen.blit(eye_active, (layer_eye_x, file_manager.tileset_height+level.tile_size*4))
        else:
            screen.blit(eye_inactive, (layer_eye_x, file_manager.tileset_height+level.tile_size*4))
    elif layer_eye_pressed:
        screen.blit(eye_pressed, (layer_eye_x, file_manager.tileset_height+level.tile_size*4))

    if not select_active_layer:
        if cursor_over_select_active_layer:
            screen.blit(select_active_layer_active, (sal_icon_x, file_manager.tileset_height+level.tile_size*4))
        else:
            screen.blit(select_active_layer_inactive, (sal_icon_x, file_manager.tileset_height+level.tile_size*4))
    elif select_active_layer:
        screen.blit(select_active_layer_clicked, (sal_icon_x, file_manager.tileset_height+level.tile_size*4))

    if cursor_over_ts_dir_icon:
        screen.blit(select_ts_dir_active, (arrow_icon_x-level.tile_size, ts_dir_icon_y))
    else:
        screen.blit(select_ts_dir_inactive, (arrow_icon_x-level.tile_size, ts_dir_icon_y))
    

# ------------------------------------------------------------------------------
# Input handling
# These are called inside the event loop in main.py.
# ------------------------------------------------------------------------------

def left_click_on_tileset(event: pygame.event.Event, screen: pygame.Surface, cv_snapped_x, cv_snapped_y):
    """Handle left-click drag on the file_manager.tileset to define a tile selection.
    Records tileset_drag_start on mouse down and finalises the selection on mouse up."""
    global tileset_drag, tileset_drag_start, has_ts_selection

    tileset_x = screen.get_width() - file_manager.tileset_width

    if cursor_over_tileset:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tileset_drag = True
            tileset_drag_start = ((cv_snapped_x - tileset_x) // level.tile_size, cv_snapped_y // level.tile_size)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            tileset_drag = False
            has_ts_selection = True    # Keep the selection rect visible after releasing

def right_click_on_canvas(event: pygame.event.Event, cv_ind_x: int, cv_ind_y:int):
    """Handle right click drag on the canvas to define a selection of the canvas
    to be drawn on the canvas"""
    global canvas_drag, canvas_drag_start, has_cv_selection, cv_selection_captured

    if cursor_over_canvas:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            canvas_drag = True
            canvas_drag_start = (cv_ind_x, cv_ind_y)
            cv_selection_captured = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            canvas_drag = False
            has_cv_selection = True

def left_click_on_canvas(event:pygame.event.Event):
    global drawing

    if cursor_over_canvas and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        drawing = True
    if cursor_over_canvas and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        drawing = False

def mouse_scroll_pressed_over_canvas(event: pygame.event.Event):
    """Handle middle-click to start and stop canvas panning.
    Sets scroll_canvas and records the origin position on button down.
    Hides the system cursor while panning for a cleaner feel.
    The actual offset update happens in update_canvas_pan() each frame."""
    global scroll_canvas, scroll_canvas_origin, canvas_offset_y

    # Cancel panning if the cursor strays over the file_manager.tileset panel
    if cursor_over_tileset:
        scroll_canvas = False

    if not cursor_over_tileset:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            scroll_canvas = True
            scroll_canvas_origin = pygame.mouse.get_pos()
            pygame.mouse.set_visible(False)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            scroll_canvas = False
            pygame.mouse.set_visible(True)

def get_clicks_on_icons(event:pygame.event.Event):
    """detect click on the icons in the toolbar"""
    global tileset_index, layer_eye_pressed, select_active_layer, ts_dir_icon_pressed

    # to cycle through need active % n_tilesets
    if cursor_over_right_arrow and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # cycle the value up
        tileset_index = (tileset_index+1) % len(file_manager.tileset_list)
        sfx.play_click_sound()
    if cursor_over_left_arrow and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # cycle the value down
        tileset_index = (tileset_index-1) % len(file_manager.tileset_list)
        sfx.play_click_sound()
    if cursor_over_layer_icon and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        level.current_layer = ((level.current_layer + 1) % level.max_layer)
        sfx.play_click_sound()
    if cursor_over_layer_eye and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        layer_eye_pressed = not layer_eye_pressed
        sfx.play_click_sound()
    if cursor_over_select_active_layer and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        select_active_layer = not select_active_layer
        sfx.play_click_sound()
    if cursor_over_ts_dir_icon and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        ts_dir_icon_pressed = True
        file_manager.get_ts_path()


# ------------------------------------------------------------------------------
# Painting to canvas
# ------------------------------------------------------------------------------

def get_ts_selection(screen: pygame.Surface, selection: pygame.Rect):
    """Extract and return the subsurface image from the file_manager.tileset matching the selection rect.
    Clips the selection to the file_manager.tileset bounds before extracting to avoid out-of-bounds errors.
    Also returns the tile-index origin (col, row) of the selection."""
    x = (selection.x - (screen.get_width() - file_manager.tileset_width)) // level.tile_size
    y = selection.y // level.tile_size

    # Clamp to file_manager.tileset bounds before subsurfacing
    bounds_rect = pygame.Rect((screen.get_width() - file_manager.tileset_width, 0, file_manager.tileset_width, file_manager.tileset_height))
    clipped_selection = selection.clip(bounds_rect)
    

    selection_img = file_manager.tileset.subsurface((
        x * level.tile_size,
        y * level.tile_size,
        clipped_selection.width,
        clipped_selection.height
    ))
    return selection_img, x, y

def get_cv_selection(screen:pygame.Surface, selection: pygame.Rect):
    global cv_selection_captured
    # make canvas selection surface size of selection
    cv_selection_surface = pygame.Surface((selection.width, selection.height), pygame.SRCALPHA)
    
    # get number of tiles in x (cols) and y (rows in selection)
    tiles_in_x = list(range(int(selection.x - canvas_offset_x)//level.tile_size, int(selection.x - canvas_offset_x + selection.width)//level.tile_size, 1))
    tiles_in_y = list(range(int(selection.y - canvas_offset_y)//level.tile_size, int(selection.y - canvas_offset_y + selection.height)//level.tile_size, 1))

    
    # loop through layers in canv_dict if 'select_active_layer' is false

    if not select_active_layer:

        for layer in range(0, level.max_layer+1, 1):
            for col in tiles_in_x:
                for row in tiles_in_y:

                    key = (col, row, layer)

                    if key in level.canv_dict:

                        img, tile_type = level.canv_dict[key]
                        img.set_alpha(255) # ensures full alpha when selecting hidden layers

                        blit_x = (col - min(tiles_in_x)) * level.tile_size
                        blit_y = (row - min(tiles_in_y)) * level.tile_size
                        cv_selection_surface.blit(img.copy(), (blit_x, blit_y))
        cv_selection_captured = True
    else:

        for col in tiles_in_x:
            for row in tiles_in_y:

                key = (col, row, level.current_layer)

                if key in level.canv_dict:

                    img, tile_type = level.canv_dict[key]
                    img.set_alpha(255) # ensures full alpha when selecting hidden layers

                    blit_x = (col - min(tiles_in_x)) * level.tile_size
                    blit_y = (row - min(tiles_in_y)) * level.tile_size
                    cv_selection_surface.blit(img.copy(), (blit_x, blit_y))
        cv_selection_captured = True

    return cv_selection_surface, min(tiles_in_x), min(tiles_in_y)