import pygame
import gui
import level
import file_manager

# ------------------------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------------------------

pygame.init()

# Create the window. flags=16 is pygame.RESIZABLE, allowing the user to resize.
flags = pygame.RESIZABLE | pygame.SCALED

screen = pygame.display.set_mode((960, 480), flags=flags)
pygame.display.set_caption('level_editor_v1')
file_manager.load_default_tileset()
# Load all GUI assets (tileset, toolbar, cursors).
# Must happen after pygame.init() and before draw_canvas(), because load_assets()
# sets gui.canvas_offset_y to toolbar_height — needed for correct canvas placement.
tileset_width, tileset_height = gui.load_assets()

# The minimum window size is twice the tileset dimensions so the tileset panel
# and canvas area are always both visible after a resize.
max_screen_width = tileset_width * 2
max_screen_height = tileset_height * 3

# Build the canvas grid surface once. It is a static surface that gets blitted
# every frame at (canvas_offset_x, canvas_offset_y) to create the panning effect.
level.populate_empty_canv_dict(gui.empty_tile)
dup_dict = {}

canvas_surface = gui.draw_canvas()


clock = pygame.time.Clock()


# ------------------------------------------------------------------------------
# Per-frame state
# These variables carry information between the event, update, and draw phases.
# ------------------------------------------------------------------------------

tileset_selection_img = None    # The subsurface image cut from the tileset selection
ts_selection_rect = None           # The pygame.Rect describing the current tileset selection
cv_selection_rect = None        # The pygame.Rect describing the current canvas selection
subsurface_x, subsurface_y = 0, 0  # Tile-index origin of the tileset selection (unused directly in draw but returned by get_selection)
ts_snapped_x, ts_snapped_y = 0, 0    # Snapped pixel position of the cursor on the tileset
cv_ind_x = 0          # Canvas tile col index under the cursor
cv_ind_y = 0          # Canvas tile row index under the cursor


# ------------------------------------------------------------------------------
# Main loop
# Each iteration: process events → update state → draw everything.
# ------------------------------------------------------------------------------

arrow_icon_x, ts_label_x, layer_icon_x, layer_eye_x, select_active_layer_icon_x, select_ts_dir_icon_y = gui.update_screen_layout(screen)

running = True
while running:

    # --------------------------------------------------------------------------
    # EVENTS
    # Handle discrete input events (button presses, window events).
    # Continuous input (held buttons, mouse position) is handled in UPDATE.
    # --------------------------------------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # On resize, enforce the minimum window size so both panels remain visible
        if event.type == pygame.WINDOWRESIZED:
            width = max(event.x, max_screen_width)//level.tile_size*level.tile_size
            height = max(event.y, max_screen_height)//level.tile_size*level.tile_size
            screen = pygame.display.set_mode((width, height), flags=16)
            # update screen layout here to return icon positions
            arrow_icon_x, ts_label_x, layer_icon_x, layer_eye_x, select_active_layer_icon_x, select_ts_dir_icon_y = gui.update_screen_layout(screen)

        # Left-click drag on the tileset to make a tile selection
        gui.left_click_on_tileset(event, screen, ts_snapped_x, ts_snapped_y)

        # Middle-click to start/stop canvas panning.
        # Only sets scroll_canvas True/False — the actual offset update is in UPDATE.
        gui.mouse_scroll_pressed_over_canvas(event)

        gui.right_click_on_canvas(event, cv_ind_x, cv_ind_y)

        gui.left_click_on_canvas(event)

        gui.get_clicks_on_icons(event)




    # --------------------------------------------------------------------------
    # UPDATE
    # Update all state that depends on the current mouse position or held buttons.
    # These run every frame regardless of whether an event fired.
    # --------------------------------------------------------------------------

    # Apply canvas panning based on middle-click drag, then clamp to valid bounds
    gui.update_canvas_pan(screen)

    # Get the snapped cursor position on the tileset panel
    ts_snapped_x, ts_snapped_y = gui.get_snapped_tileset_pos(screen)

    # Get the tile indices under the cursor on the canvas.
    # Returns None if the cursor is over the tileset or toolbar, so we guard before unpacking.
    canvas_indices_output = gui.get_canvas_indices(screen)
    if canvas_indices_output is not None:
        cv_ind_x, cv_ind_y = canvas_indices_output

    # Track where the tileset drag ends (used to build the selection rect)
    gui.update_tileset_drag_end(screen, ts_snapped_x, ts_snapped_y)
    result = gui.update_canvas_drag_end(cv_ind_x, cv_ind_y)
    if result is not None:
        dup_dict = result
    # Recalculate the selection rect from drag start/end each frame
    ts_selection_rect = gui.update_tileset_selection_cursor(screen)
    cv_selection_rect = gui.update_canvas_selection_cursor(screen, cv_ind_x, cv_ind_y)


    # If there is a valid selection rect, extract the corresponding image from the tileset
    if ts_selection_rect is not None:
        tileset_selection_img, subsurface_x, subsurface_y = gui.get_ts_selection(screen, ts_selection_rect)
    elif cv_selection_rect is not None and not gui.cv_selection_captured and not gui.canvas_drag:
        tileset_selection_img, subsurface_x, subsurface_y = gui.get_cv_selection(screen, cv_selection_rect, dup_dict)

    # Left-click on the canvas to paint the current selection at the cursor position
    if pygame.mouse.get_pressed()[0] and gui.cursor_over_canvas and tileset_selection_img is not None and not gui.canvas_drag:
        level.write_tileset_selecton(cv_ind_x, cv_ind_y, tileset_selection_img, gui.clicking_on_icons, gui.tileset_drag)

    gui.update_flag_mouse_over_toolbar(screen)
    gui.update_toolbar_flags(arrow_icon_x, layer_icon_x, layer_eye_x, select_active_layer_icon_x, select_ts_dir_icon_y)

    gui.update_current_tileset()
    # --------------------------------------------------------------------------
    # DRAW
    # Clear the screen, then draw everything in back-to-front order.
    # --------------------------------------------------------------------------
    
    screen.fill((0, 0, 0))

    # Canvas grid — drawn first so everything else appears on top of it

    screen.blit(canvas_surface, (gui.canvas_offset_x, gui.canvas_offset_y))


    gui.draw_from_dict(screen)         # All previously placed tiles 

    gui.draw_tileset(screen)           # Tileset panel on the right
    gui.draw_toolbar(screen)    
    gui.draw_toolbar_icons(screen, arrow_icon_x, ts_label_x, layer_icon_x, layer_eye_x, select_active_layer_icon_x, select_ts_dir_icon_y)       # Toolbar across the top (drawn after canvas so it covers the canvas edge)   
    gui.draw_hovering_tile_cursor(screen, ts_snapped_x, ts_snapped_y)              # Single-tile highlight on the tileset
    gui.draw_tileset_selection_cursor(screen, ts_selection_rect)        # Selection rect on the tileset
    
    mutable_ts_selection_rect = gui.draw_subsurface_tileset(screen, tileset_selection_img, cv_ind_x, cv_ind_y)  # Tile preview on canvas
    
    

    gui.draw_canvas_cursor(screen, mutable_ts_selection_rect, cv_ind_x, cv_ind_y) # Snapped cursor rect on the canvas sized to the selection (mutable because grid limits change its dimensions)
    cv_selection_result = gui.draw_canvas_selection_cursor(screen, cv_selection_rect, cv_ind_x, cv_ind_y)
    if cv_selection_result is not None:
        tileset_selection_img = cv_selection_result


    clock.tick(120)          # Cap at 120 FPS
    pygame.display.flip()   # Push the completed frame to the display