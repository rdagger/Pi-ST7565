from time import sleep
import os
root = os.path.dirname(os.path.realpath(__file__))

from xglcd_font import XglcdFont

if os.environ.get('MOCK_RPI') == 'true':
    from soft_display import mock_gpio, Glcd
    mock_gpio()
else:
    from st7565 import Glcd

glcd = Glcd(rgb=[21, 20, 16])
glcd.init()
glcd.set_backlight_color(0, 100, 0)
x0, y0 = 40, 31
rout, rmid, rin = 30, 20, 10
incr = 2
wendy = XglcdFont(root + '/fonts/Wendy7x8.c', 7, 8)
ship = glcd.load_bitmap(root + '/images/ship_38x29.raw',
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

while True:
    sleep(1)
