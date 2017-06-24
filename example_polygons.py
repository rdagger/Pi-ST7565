"""File contining demo displaying polygons on LCD screen."""
from st7565 import Glcd
from soft_display import Glcd as GlcdSoft
import xglcd_font as font
from time import sleep
from os import path, getcwd
from sys import argv

x0, y0 = 40, 31
rout, rmid, rin = 30, 20, 10
incr = 2
wendy = font.XglcdFont(path.join(getcwd(),'fonts/Wendy7x8.c'), 7, 8)


def run(runOnPi):
    """Run the demo."""
    if runOnPi:
        glcd = Glcd(rgb=[21, 20, 16])
    else:
        glcd = GlcdSoft(rgb=[21, 20, 16])
    glcd.init()
    glcd.set_backlight_color(0, 100, 0)
    ship = glcd.load_bitmap(path.join(getcwd(),'images/ship_38x29.raw'),
                            width=38, height=29, invert=True)

    for angle in range(0, 360, incr):
        glcd.clear_back_buffer()
        glcd.draw_rectangle(0, 0, 128, 64)
        glcd.draw_string("Angle: {0}".format(angle), wendy, 85, 2,spacing=0)
        glcd.draw_bitmap(ship, 87, 32)

        glcd.draw_polygon(6, x0, y0, rout, rotate=angle-180, color=1)
        glcd.draw_polygon(5, x0, y0, rmid, rotate=-angle, color=1)
        glcd.fill_polygon(3, x0, y0, rin, rotate=angle, color=1)

        glcd.draw_polygon(6, x0, y0, rout, rotate=angle-180 + incr, color=1)
        glcd.draw_polygon(5, x0, y0, rmid, rotate=-angle - incr, color=1)
        glcd.fill_polygon(3, x0, y0, rin, rotate=angle + incr, color=1)

        glcd.flip()
        sleep(.01)

    glcd.cleanup()
    glcd.flip()
    while(True):
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
