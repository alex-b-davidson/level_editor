import os
import pygame
from tkinter import filedialog

def get_ts_path():
    """Function that allows the user to choose a directory containing tilesets then updates the tileset_list"""
    global tileset_list, tileset, tileset_height, tileset_width, ts_dir_icon_pressed, tileset_index
    ts_path = filedialog.askdirectory(title= 'select directory')
    tileset_list = [pygame.image.load(rf'{ts_path}/{tileset}').convert_alpha().copy() for tileset in os.listdir(ts_path) if tileset.endswith('.png')]
    tileset_index = 0
    tileset = tileset_list[tileset_index]
    tileset_width = tileset.get_width()
    tileset_height = tileset.get_height()
    ts_dir_icon_pressed = False
    print((tileset_list))

