"""File with demo on displaying a set of images."""
from st7565 import Glcd
from soft_display import Glcd as GlcdSoft
from pygame import time
from os import path, getcwd
from sys import argv

clock = time.Clock()

def run(runOnPi):
    """Run the demo."""
    if runOnPi:
        glcd = Glcd(rgb=[21, 20, 16])
    else:
        glcd = GlcdSoft(rgb=[21, 20, 16])

    glcd.init()
    glcd.set_backlight_color(0, 0, 100)

    # Use List comprehension to load raw bitmaps to list
    paths = []
    for i in range(1, 8):
        suffix = "images/dog{0}.raw".format(i)
        fullpath = path.join(getcwd(), suffix)
        paths.append(fullpath)
    dogs = [glcd.load_bitmap(p) for p in paths]

    while 1:
        for dog in dogs:
            glcd.draw_bitmap(dog)
            glcd.flip()
            clock.tick(4)

if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == 'soft':
            run(False)
        else:
            run(True)
    else:
        print("Assuming running on Pi")
        run(True)
