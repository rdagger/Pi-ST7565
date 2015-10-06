import st7565
import xglcd_font as font
import math
import time

neato = font.XglcdFont('/home/pi/Pi-ST7565/fonts/Neato5x7.c', 5, 7)
glcd = st7565.Glcd(rgb=[21, 20, 16])
glcd.init()
x0, y0 = 63, 31

def get_face_xy(angle, radius):
    """
    Get x,y coordinates on face at specified angle and radius 
    """
    theta = math.radians(angle)
    x = int(x0 + radius * math.cos(theta))
    y = int(y0 + radius * math.sin(theta))
    return x, y

def draw_face():
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
    glcd.draw_string(time.strftime("%b").upper(), neato, 0,0)
    glcd.draw_string(time.strftime(" %d"), neato, 0, 8)

while 1:
    glcd.clear_back_buffer()
    draw_face()
    minute = int(time.strftime("%M"))
    hour = int(time.strftime("%H"))
    glcd.draw_line(x0, y0, *get_face_xy(minute * 6 + 270, 29))
    glcd.draw_line(x0, y0, *get_face_xy(hour * 30 - 90, 20))
    glcd.flip()
    while minute == int(time.strftime("%M")):
        time.sleep(1)
        
    
