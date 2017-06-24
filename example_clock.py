"""File with demo displaying clock on LCD screen."""
from st7565 import Glcd
from soft_display import Glcd as GlcdSoft
import xglcd_font as font
import math
from time import sleep, strftime
from os import path, getcwd
from sys import argv

neato = font.XglcdFont(path.join(getcwd(),'fonts/Neato5x7.c'), 5, 7)
x0, y0 = 63, 31

def get_face_xy(angle, radius):
    """Get x,y coordinates on face at specified angle and radius."""
    theta = math.radians(angle)
    x = int(x0 + radius * math.cos(theta))
    y = int(y0 + radius * math.sin(theta))
    return x, y

def draw_face(glcd):
    """Draw the face of the clock."""
    # Outline
    glcd.draw_circle(x0, y0, 31)
    # Ticks
    for angle in range(30, 331, 30):
        glcd.draw_line(x0, y0, *get_face_xy(angle, 29))
    # Clear center of circle
    glcd.fill_circle(x0, y0, 25, color=0)
    # Numbers
    glcd.draw_string("12", neato, x0 - 5, y0 - 29, spacing=0)
    glcd.draw_letter("3", neato, x0 + 25, y0 - 3)
    glcd.draw_letter("6", neato, x0 - 2, y0 + 23)
    glcd.draw_letter("9", neato, x0 - 29, y0 - 3)
    # Date
    glcd.draw_string(strftime("%b").upper(), neato, 0,0)
    glcd.draw_string(strftime(" %d"), neato, 0, 8)

def run(runOnPi):
    """Run the demo."""
    if(runOnPi):
        glcd = Glcd(rgb=[21, 20, 16])
    else:
        glcd = GlcdSoft(rgb=[21, 20, 16])
    glcd.init()

    while 1:
        glcd.clear_back_buffer()
        draw_face(glcd)
        minute = int(strftime("%M"))
        hour = int(strftime("%H"))
        glcd.draw_line(x0, y0, *get_face_xy(minute * 6 + 270, 29))
        glcd.draw_line(x0, y0, *get_face_xy(hour * 30 - 90, 20))
        glcd.flip()
        while minute == int(strftime("%M")):
            sleep(1)

if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == 'soft':
            run(False)
        else:
            run(True)
    else:
        print("Assuming running on Pi")
        run(True)
