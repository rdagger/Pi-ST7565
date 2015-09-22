import st7565
from pygame import time
clock = time.Clock()

glcd = st7565.Glcd(rgb=[17,27,22])
glcd.init()
glcd.set_backlight_color(0, 0, 100)

path = "/home/pi/Pi-ST7565/images/"
# Use List comprehension to load raw bitmaps to list
dogs = [glcd.load_bitmap(path + "dog{0}.raw".format(i)) for i in range(1,8)]

while 1:
    for dog in dogs:
        glcd.draw_bitmap(dog)
        glcd.flip()
        clock.tick(4)
        



