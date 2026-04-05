from pygame import mixer as pgm

pgm.init()

# load sounds
click_1 = pgm.Sound(r'F:\level_editor\assets\sounds\click_1.mp3')
click_1.set_volume(0.2)


def play_click_sound():
    click_1.play()
