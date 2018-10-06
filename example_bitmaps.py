from pygame import time
import os 
root = os.path.dirname(os.path.realpath(__file__))

from xglcd_font import XglcdFont

if os.environ.get('MOCK_RPI') == 'true':
    from soft_display import mock_gpio, Glcd
    mock_gpio()
else:
    from st7565 import Glcd

clock = time.Clock()

glcd = Glcd(rgb=[21, 20, 16])
glcd.init()
glcd.set_backlight_color(0, 0, 100)

path = root + "/images/"
# Use List comprehension to load raw bitmaps to list
dogs = [glcd.load_bitmap(path + "dog{0}.raw".format(i)) for i in range(1,8)]

while 1:
    for dog in dogs:
        glcd.draw_bitmap(dog)
        glcd.flip()
        clock.tick(4)
        



