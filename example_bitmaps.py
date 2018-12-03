import st7565
from pygame import time
clock = time.Clock()

glcd = st7565.Glcd(rgb=[21, 20, 16])
glcd.init()
glcd.set_backlight_color(0, 0, 100)

path = "/home/pi/Pi-ST7565/images/"
# Use List comprehension to load raw bitmaps to list
dogs = [glcd.load_bitmap(path + "dog{0}.raw".format(i)) for i in range(1,8)]

try:
    while True:
        for dog in dogs:
            glcd.draw_bitmap(dog)
            glcd.flip()
            clock.tick(4)
except KeyboardInterrupt:
    print('\nCtrl-C pressed.  Cleaning up and exiting...')
finally:
    glcd.cleanup()          



