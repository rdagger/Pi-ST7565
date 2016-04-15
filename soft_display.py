""" This Module allows to test the programm and display output without running it on the Raspberry Pi.
It uses pygame to render the display. The display is only updated on each flip(), just like the st7565.Glcd
class. Therefor it might be unresponsive until the next flip() is called.


Usage:
    use soft_display.Glcd() instead of st7565.Glcd()

"""


def mock_gpio():
    try:
        import RPi.GPIO as GPIO
    except:
        from mock import MagicMock, patch
        import sys

        mymodule = MagicMock()
        modules = {
            'spidev': mymodule,
            'RPi': mymodule,
            'RPi.GPIO': mymodule
        }
        patcher = patch.dict('sys.modules', modules)
        patcher.start()


import pygame
import st7565


class Glcd(st7565.Glcd):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    ZOOM = 2

    def __init__(self, a0=24, cs=8, rst=25, rgb=None):
        mock_gpio()
        super(Glcd, self).__init__(None, None, None, None)

        # Initialize the game engine
        pygame.init()

        # Set the height and width of the screen
        size = [st7565.Glcd.LCD_WIDTH * Glcd.ZOOM, st7565.Glcd.LCD_HEIGHT * Glcd.ZOOM]
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption("ST7565")
        self.clock = pygame.time.Clock()

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)

    def send_data(self, data):
        pass

    def send_command(self, cmd):
        pass

    def flip(self):
        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                raise KeyboardInterrupt()

        self.screen.fill(Glcd.WHITE)

        for y in range(0, 64):
            for x in range(0, 128):
                pixel = self.back_buffer[y, x]
                if pixel:
                    color = Glcd.BLACK
                else:
                    color = Glcd.WHITE
                pygame.draw.rect(self.screen, color, [x * Glcd.ZOOM, y * Glcd.ZOOM, Glcd.ZOOM, Glcd.ZOOM], 0)

        pygame.display.flip()

        return Glcd()
