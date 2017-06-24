"""File with a demo on displaying a string on LCD."""
from st7565 import Glcd
import xglcd_font as font
from sys import argv
from soft_display import Glcd as GlcdSoft
from os import path, getcwd

robotron = font.XglcdFont(path.join(getcwd(),'fonts/Robotron7x11.c'), 7, 11) #/home/pi/Pi-ST7565/
x0, y0 = 2, 2

def run(runOnPi, displayString):
    """Run the demo."""
    if runOnPi:
        glcd = Glcd(rgb=[21, 20, 16])
    else:
        glcd = GlcdSoft(rgb=[21, 20, 16])
    glcd.init()

        # letters
    if len(displayString.split()) > 1:
        for substr in displayString:
            glcd.draw_string(displayString, robotron, x0, y0, spacing=0)

    else:
        glcd.draw_string(displayString, robotron, x0, y0, spacing=0)
    glcd.flip()
    while(1):
        continue

if __name__ == '__main__':
    if len(argv) > 2:
        if argv[1] == 'soft':
            run(False, argv[2])
        else:
            run(True, argv[2])
    else:
        print("Assuming running on Pi")
        run(True, argv[1])
