from __future__ import print_function
from time import sleep
import math
import numpy as np


class Glcd(object):
    """ST7565 graphics lcd module object
    Note:  All coordinates are zero based.
    """
    # LCD commands from datasheet
    CMD_DISPLAY_OFF = 0xAE
    CMD_DISPLAY_ON = 0xAF
    CMD_SET_DISP_START_LINE = 0x40
    CMD_SET_PAGE = 0xB0
    CMD_SET_COLUMN_UPPER = 0x10
    CMD_SET_COLUMN_LOWER = 0x00
    CMD_SET_ADC_NORMAL = 0xA0
    CMD_SET_ADC_REVERSE = 0xA1
    CMD_SET_DISP_NORMAL = 0xA6
    CMD_SET_DISP_REVERSE = 0xA7
    CMD_SET_ALLPTS_NORMAL = 0xA4
    CMD_SET_ALLPTS_ON = 0xA5
    CMD_SET_BIAS_9 = 0xA2
    CMD_SET_BIAS_7 = 0xA3
    CMD_INTERNAL_RESET = 0xE2
    CMD_SET_COM_NORMAL = 0xC0
    CMD_SET_COM_REVERSE = 0xC8
    CMD_SET_POWER_CONTROL = 0x28
    CMD_SET_RESISTOR_RATIO = 0x20
    CMD_SET_VOLUME_FIRST = 0x81
    CMD_SET_VOLUME_SECOND = 0x00
    CMD_SET_STATIC_OFF = 0xAC
    CMD_SET_STATIC_ON = 0xAD
    CMD_SET_STATIC_REG = 0x00

    # LCD Parameters
    LCD_WIDTH = 128
    LCD_HEIGHT = 64
    LCD_PAGE_COUNT = 8
    LCD_CONTRAST = 0x19

    BACKLIGHT_PWM_FREQUENCY = 100

    # LCD Page Order
    __pagemap = (3, 2, 1, 0, 7, 6, 5, 4)

    def __init__(self, a0=24, cs=8, rst=25, rgb=None):
        """Constructor for ST7565.
        Args:
            a0 (int):  Register select address GPIO pin
            cs (int):  Chip select GPIO pin
            rst (int): Reset GPIO pin
            rgb (Optional [int]): RGB backlight GPIO pin list. Default is None.
        """
        import RPi.GPIO as GPIO

        # Set BCM GPIO numbering
        GPIO.setmode(GPIO.BCM)

        # Disable GPIO warnings
        GPIO.setwarnings(False)

        # Initialize SPI
        import spidev
        self.__spi = spidev.SpiDev()
        self.__spi.open(0, 0)
        self.__spi.max_speed_hz = 250000

        # Initialize back_buffer
        self.back_buffer = np.zeros((Glcd.LCD_HEIGHT, Glcd.LCD_WIDTH), dtype='uint8')

        # LCD Pins
        self.a0 = a0
        self.cs = cs
        self.rst = rst
        # Set pin directions (output)
        GPIO.setup(a0, GPIO.OUT)
        GPIO.setup(cs, GPIO.OUT)
        GPIO.setup(rst, GPIO.OUT)
        # RGB backlight pins
        # Enable PWM for RGB GPIO pins if specified
        if rgb is not None:
            GPIO.setup(rgb[0], GPIO.OUT)
            GPIO.setup(rgb[1], GPIO.OUT)
            GPIO.setup(rgb[2], GPIO.OUT)
            self.red = GPIO.PWM(rgb[0], self.BACKLIGHT_PWM_FREQUENCY)
            self.green = GPIO.PWM(rgb[1], self.BACKLIGHT_PWM_FREQUENCY)
            self.blue = GPIO.PWM(rgb[2], self.BACKLIGHT_PWM_FREQUENCY)
            # Set backlight to full white (GPIO set up as cathodes)
            self.red.start(0)
            self.green.start(0)
            self.blue.start(0)
        else:
            self.red, self.green, self.blue = None, None, None

    def send_command(self, cmd):
        """Send commands to ST7565
        Args:
            cmd ([int]):  commands to send
        """
        import RPi.GPIO as GPIO
        # Set command mode
        GPIO.output(self.a0, GPIO.LOW)
        self.__spi.xfer(cmd)

    def send_data(self, data):
        """Send data to ST7565
        Args:
            data ([int]):  data to send
        """
        import RPi.GPIO as GPIO
        # Set data mode 
        GPIO.output(self.a0, GPIO.HIGH)
        self.__spi.xfer(data)

    def move_cursor(self, x, page):
        """Move cursor to specified display position
        Args:
            x (int):  x column coordinate
            page (int): page
        Note:
            X coordinates are 1 based on Adafruit ST7565
        """
        # Confirm valid horizontal position
        if x >= self.LCD_WIDTH | x < 0:
            return
        # Confirm valid vertal page
        if page > self.LCD_PAGE_COUNT - 1 | page < 0:
            return
        # Set page
        self.send_command([self.CMD_SET_PAGE | self.__pagemap[page]])
        # Set lower bits of column
        self.send_command([self.CMD_SET_COLUMN_LOWER | (x & 0xf)])
        # Set upper bits of column
        self.send_command([self.CMD_SET_COLUMN_UPPER | ((x >> 4) & 0xf)])

    def clear_display(self):
        """Clear ST7565 display"""
        for page in self.__pagemap:
            # Move to zero position on specified page
            self.move_cursor(1, page)
            # Send list of zeros to clear page
            self.send_data([0] * self.LCD_WIDTH)

    def reset(self):
        """Reset ST7565 display"""
        import RPi.GPIO as GPIO
        # Toggle reset pin
        GPIO.output(self.rst, GPIO.LOW)
        sleep(.5)
        GPIO.output(self.rst, GPIO.HIGH)

    def set_backlight_color(self, r, g, b):
        """Set LED backlight color
        Args:
            r (int): red duty cycle 0 - 100 (0 = off, 100 = full on)
            g (int): green duty cycle 0 - 100 (0 = off, 100 = full on)
            b (int): blue duty cycle 0 - 100 (0 = off, 100 = full on)
        """
        if self.red is None:
            print("Backlight RGB GPIO pins not initialized.")
            return
        if 0 <= r <= 100 and 0 <= g <= 100 and 0 <= b <= 100:
            # GPIO pins sink cathodes so percentage needs to be reversed
            self.red.ChangeDutyCycle(100 - r)
            self.green.ChangeDutyCycle(100 - g)
            self.blue.ChangeDutyCycle(100 - b)
        else:
            print("Invalid range.  Colors must be between 0 and 100.")

    def set_contrast(self, level):
        """Set contrast
        Args:
            level (int): contrast level  0 - 255
        """
        self.send_command([self.CMD_SET_VOLUME_FIRST])
        self.send_command([self.CMD_SET_VOLUME_SECOND | (level & 0x3f)])

    def clear_back_buffer(self):
        """Clear back buffer only"""
        self.back_buffer = np.zeros((self.LCD_HEIGHT, self.LCD_WIDTH), dtype='uint8')

    def init(self):
        import RPi.GPIO as GPIO
        # CS Chip Select low
        GPIO.output(self.cs, GPIO.LOW)
        # Reset
        self.reset()
        # LCD bias select
        self.send_command([self.CMD_SET_BIAS_7])
        # ADC select
        self.send_command([self.CMD_SET_ADC_NORMAL])
        # SHL select
        self.send_command([self.CMD_SET_COM_NORMAL])
        # Initial display line
        self.send_command([self.CMD_SET_DISP_START_LINE])
        # Turn on voltage converter (VC=1, VR=0, VF=0)
        self.send_command([self.CMD_SET_POWER_CONTROL | 0x4])
        sleep(.05)
        # Turn on voltage regulator (VC=1, VR=1, VF=0)
        self.send_command([self.CMD_SET_POWER_CONTROL | 0x6])
        sleep(.05)
        # Turn on voltage follower (VC=1, VR=1, VF=1)
        self.send_command([self.CMD_SET_POWER_CONTROL | 0x7])
        sleep(.01)
        # Set lcd operating voltage (regulator resistor, ref voltage resistor)
        self.send_command([self.CMD_SET_RESISTOR_RATIO | 0x7])
        # Turn on display
        self.send_command([self.CMD_DISPLAY_ON])
        # Display all points
        self.send_command([self.CMD_SET_ALLPTS_NORMAL])
        # Contrast
        self.set_contrast(self.LCD_CONTRAST)
        # Clear display
        self.clear_display()

    def reverse_display(self, reverse=True):
        """Reverses the display status on LCD panel without rewriting
        the contents of the display data RAM.
        Args:
            reverse (Optional boolean): True is reverse.  False is normal.
        Note:
            Causes unwanted artifacts
        """
        if reverse:
            self.send_command([self.CMD_SET_DISP_REVERSE])
        else:
            self.send_command([self.CMD_SET_DISP_NORMAL])

    def sleep(self):
        """Put ST7565 display in sleep mode"""
        self.send_command([self.CMD_SET_STATIC_OFF])
        self.send_command([self.CMD_DISPLAY_OFF])
        self.send_command([self.CMD_SET_ALLPTS_ON])

    def wake(self):
        """Wake up ST7565 display from sleed mode"""
        self.send_command([self.CMD_INTERNAL_RESET])
        self.send_command([self.CMD_SET_ALLPTS_NORMAL])
        self.send_command([self.CMD_DISPLAY_ON])
        self.send_command([self.CMD_SET_STATIC_ON])
        self.send_command([self.CMD_SET_STATIC_REG | 0x03])

    def standby(self, exit=False):
        """Put ST7565 in standby mode
        Args:
            exit (Optional boolean): True to exit standby, Default is false and enters standby.
        """
        if exit:
            # Exit standby mode
            self.send_command([self.CMD_SET_ALLPTS_NORMAL])
            self.send_command([self.CMD_DISPLAY_ON])
        else:
            # Enter standby mode
            self.send_command([self.CMD_SET_STATIC_ON])
            self.send_command([self.CMD_SET_STATIC_REG | 0x03])
            self.send_command([self.CMD_DISPLAY_OFF])
            self.send_command([self.CMD_SET_ALLPTS_ON])

    def flip(self):
        """Send back buffer to ST7565 display"""
        for idx in range(0, self.LCD_PAGE_COUNT):
            # Home cursor on the page
            self.move_cursor(1, idx)
            # Page start row
            row_start = idx << 3
            # Page stop row
            row_stop = (idx + 1) << 3
            # slice page from buffer and pack bits to bytes then send to display
            self.send_data(np.packbits(self.back_buffer[row_start:row_stop], axis=0).flatten().tolist())

    def cleanup(self):
        """Clean up SPI and GPIO"""
        self.clear_display()
        self.sleep()
        self.__spi.close()
        import RPi.GPIO as GPIO
        GPIO.cleanup()

    def is_off_grid(self, xmin, ymin, xmax, ymax):
        """Checks if drawing coordinates extends past LCD display boundaries
        Args:
            xmin (int): Minimum horizontal pixel.
            ymin (int): Minimum vertical pixel.
            xmax (int): Maximum horizontal pixel.
            ymax (int): Maximum vertical pixel.
        Returns:
            boolean: False = Coordinates OK, True = Error.
        """
        if xmin < 0:
            print('x-coordinate: {0} below minimum of 0.'.format(xmin))
            return True
        if ymin < 0:
            print('y-coordinate: {0} below minimum of 0.'.format(ymin))
            return True
        if xmax >= self.LCD_WIDTH:
            print('x-coordinate: {0} above maximum of {1}.'.format(xmax, self.LCD_WIDTH - 1))
            return True
        if ymax >= self.LCD_HEIGHT:
            print('y-coordinate: {0} above maximum of {1}.'.format(ymax, self.LCD_HEIGHT - 1))
            return True
        return False

    def is_point(self, x, y):
        """Determines if coordinates on back buffer has a drawn point
        Args:
            x, y (int): Coordinates of point
        Returns boolean: True if pixel is drawn.  False is blank.
        """
        # Confirm coordinates in boundary
        if self.is_off_grid(x, y, x, y):
            return False
        return self.back_buffer[y, x] == 1

    def draw_point(self, x, y, color=1, invert=False):
        """Draws a single point on the back buffer
        Args:
            x, y (int): Coordinates of point
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        """
        if not 0 <= x < self.LCD_WIDTH:
            print('x-coordinate: {0} outside display range of 0 to {1} .').format(x, self.LCD_WIDTH - 1)
            return
        if not 0 <= y < self.LCD_HEIGHT:
            print('y-coordinate: {0} outside display range of 0 to {1} .').format(x, self.LCD_HEIGHT - 1)
            return
        if invert:
            self.back_buffer[y, x] ^= 1
        else:
            self.back_buffer[y, x] = color

    def draw_line(self, x1, y1, x2, y2, color=1, invert=False):
        """Draws a line on the back buffer using Bresenham's algorithm
        Args:
            x1, y1 (int): Starting coordinates of the line
            x2, y2 (int): Ending coordinates of the line
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        """
        # Confirm coordinates in boundary
        if self.is_off_grid(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)):
            return
        # Check for horizontal line
        if y1 == y2:
            if x1 > x2:
                x1, x2 = x2, x1
            if invert:
                self.back_buffer[y1, x1:x2 + 1] ^= 1
            else:
                self.back_buffer[y1, x1:x2 + 1] = color
            return
        # Check for vertical line
        if x1 == x2:
            if y1 > y2:
                y1, y2 = y2, y1
            if invert:
                self.back_buffer[y1:y2 + 1, x1] ^= 1
            else:
                self.back_buffer[y1:y2 + 1, x1] = color
            return
        # Changes in x, y
        dx = x2 - x1
        dy = y2 - y1
        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)
        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        # Swap start and end points if necessary
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1
        # Calculate error
        error = dx >> 1
        ystep = 1 if y1 < y2 else -1
        y = y1
        for x in range(x1, x2 + 1):
            if invert:
                if is_steep:
                    self.back_buffer[x, y] ^= 1
                else:
                    self.back_buffer[y, x] ^= 1
            else:
                if is_steep:
                    self.back_buffer[x, y] = color
                else:
                    self.back_buffer[y, x] = color
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

    def draw_lines(self, coords, color=1, invert=False):
        """Draws multiple lines on the back buffer
        Args:
            coords (Numpy 2D array dtype=Uint8): Line coordinate x,y pairs per row
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        """
        # Expects numpy array with (n, 2) shape
        if coords.shape[1] != 2:
            return
        # Starting point
        x1, y1 = coords[0]
        # Iterate through coordinates
        for row in coords[1:]:
            x2, y2 = row
            self.draw_line(x1, y1, x2, y2, color, invert)
            x1, y1 = x2, y2

    def draw_rectangle(self, x1, y1, w, h, color=1, invert=False):
        """Draws a rectangle on the back buffer
        Args:
            x1, y1 (int): Top left coordinates of rectangle
            w, h (int): Width & height in pixels of rectangle
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        """
        # Determine x2, y2
        x2 = x1 + w - 1
        y2 = y1 + h - 1

        if self.is_off_grid(x1, y1, x2, y2):
            return
        if invert:
            # Top
            self.back_buffer[y1, x1 + 1:x2] ^= 1
            # Bottom
            self.back_buffer[y2, x1:x2 + 1] ^= 1
            # Left
            self.back_buffer[y1:y2, x1] ^= 1
            # Right
            self.back_buffer[y1:y2, x2] ^= 1
        else:
            # Top
            self.back_buffer[y1, x1:x2] = color
            # Bottom
            self.back_buffer[y2, x1:x2 + 1] = color
            # Left
            self.back_buffer[y1:y2, x1] = color
            # Right
            self.back_buffer[y1:y2, x2] = color

    def fill_rectangle(self, x1, y1, w, h, color=1, invert=False):
        """Draws a filled rectangle on the back buffer
        Args:
            x1, y1 (int): Top left coordinates of rectangle
            w, h (int): Width & height in pixels of rectangle
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        """
        if self.is_off_grid(x1, y1, x1 + w - 1, y1 + h - 1):
            return
        # Draw filled rectangle
        if invert:
            self.back_buffer[y1:y1 + h, x1:x1 + w] ^= 1
        else:
            self.back_buffer[y1:y1 + h, x1:x1 + w] = color

    def draw_circle(self, x0, y0, r, color=1):
        """Draws a circle on the back buffer
        Args:
            x0, y0 (int): Pixel coordinates of center point
            r (int): Radius
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        if self.is_off_grid(x0 - r, y0 - r, x0 + r, y0 + r):
            return
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.back_buffer[y0 + r, x0] = color
        self.back_buffer[y0 - r, x0] = color
        self.back_buffer[y0, x0 + r] = color
        self.back_buffer[y0, x0 - r] = color
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.back_buffer[y0 + y, x0 + x] = color
            self.back_buffer[y0 + y, x0 - x] = color
            self.back_buffer[y0 - y, x0 + x] = color
            self.back_buffer[y0 - y, x0 - x] = color
            self.back_buffer[y0 + x, x0 + y] = color
            self.back_buffer[y0 + x, x0 - y] = color
            self.back_buffer[y0 - x, x0 + y] = color
            self.back_buffer[y0 - x, x0 - y] = color

    def fill_circle(self, x0, y0, r, color=1):
        """Draws a filled circle on the back buffer
        Args:
            x0, y0 (int): Center point coordinates
            r (int): Radius
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        if self.is_off_grid(x0 - r, y0 - r, x0 + r, y0 + r):
            return
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.back_buffer[y0 - r: y0 + r + 1, x0] = color
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.back_buffer[y0 - y: y0 + y + 1, x0 + x] = color
            self.back_buffer[y0 - y: y0 + y + 1, x0 - x] = color
            self.back_buffer[y0 - x: y0 + x + 1, x0 - y] = color
            self.back_buffer[y0 - x: y0 + x + 1, x0 + y] = color

    def draw_ellipse(self, x0, y0, a, b, color=1):
        """Draws an ellipse on the back buffer
        Args:
            x0, y0 (int): Pixel coordinates of center point
            a (int): Semi axis horizontal
            b (int): Semi axis vertical
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        if self.is_off_grid(x0 - a, y0 - b, x0 + a, y0 + b):
            return
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.back_buffer[y0 + y, x0 + x] = color
        self.back_buffer[y0 + y, x0 - x] = color
        self.back_buffer[y0 - y, x0 + x] = color
        self.back_buffer[y0 - y, x0 - x] = color
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.back_buffer[y0 + y, x0 + x] = color
            self.back_buffer[y0 + y, x0 - x] = color
            self.back_buffer[y0 - y, x0 + x] = color
            self.back_buffer[y0 - y, x0 - x] = color
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) + a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.back_buffer[y0 + y, x0 + x] = color
            self.back_buffer[y0 + y, x0 - x] = color
            self.back_buffer[y0 - y, x0 + x] = color
            self.back_buffer[y0 - y, x0 - x] = color

    def fill_ellipse(self, x0, y0, a, b, color=1):
        """Draws a filled ellipse on the back buffer
        Args:
            x0, y0 (int): Pixel coordinates of center point
            a (int): Semi axis horizontal
            b (int): Semi axis vertical
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        if self.is_off_grid(x0 - a, y0 - b, x0 + a, y0 + b):
            return
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.draw_line(x0, y0 - y, x0, y0 + y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.draw_line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.draw_line(x0 - x, y0 - y, x0 - x, y0 + y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) + a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.draw_line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.draw_line(x0 - x, y0 - y, x0 - x, y0 + y, color)

    def draw_polygon(self, sides, x0, y0, r, rotate=0, color=1):
        """Draws an n-sided regular polygon on the back buffer
        Args:
            sides (int): Number of polygon sides
            x0, y0 (int): Center point coordinates
            r (int): Radius
            rotate (Optional float): Rotation in degrees relative to origin. Default is 0.
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        coords = np.empty(shape=[sides + 1, 2], dtype="float64")
        n = np.arange(sides, dtype="float64")
        theta = math.radians(rotate)
        for s in n:
            t = 2.0 * math.pi * s / sides + theta
            coords[int(s), 0] = r * math.cos(t) + x0
            coords[int(s), 1] = r * math.sin(t) + y0
        coords[sides] = coords[0]
        # Cast to python float first to fix rounding errors
        self.draw_lines(coords.astype("float32").astype("int32"), color=color)

    def fill_polygon(self, sides, x0, y0, r, rotate=0, color=1, invert=False):
        """Draws a filled n-sided regular polygon on the back buffer
        Args:
            sides (int): Number of polygon sides
            x0, y0 (int): Center point coordinates
            r (int): Radius
            rotate (Optional float): Rotation in degrees relative to origin. Default is 0.
            color (Optional int): 0 = pixel off, 1 = pixel on (default)
            invert (Optional boolean): Inverts target pixel (overrides color)
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        if self.is_off_grid(x0 - r, y0 - r, x0 + r, y0 + r):
            return
        coords = np.empty(shape=[sides + 1, 2], dtype="float64")
        n = np.arange(sides, dtype="float64")
        theta = math.radians(rotate)
        # Determine polygon coordinates
        for s in n:
            t = 2.0 * math.pi * s / sides + theta
            coords[int(s), 0] = r * math.cos(t) + x0
            coords[int(s), 1] = r * math.sin(t) + y0
        coords[sides] = coords[0]
        # Cast to python float first to fix rounding errors
        coords = coords.astype("float32").astype("int32")
        # Starting point
        x1, y1 = coords[0]
        # Minimum Maximum X dict
        xdict = {y1: [x1, x1]}
        # Iterate through coordinates
        for row in coords[1:]:
            x2, y2 = row
            xprev, yprev = x2, y2
            # Calculate perimeter
            # Check for horizontal side
            if y1 == y2:
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 in xdict:
                    xdict[y1] = [min(x1, xdict[y1][0]), max(x2, xdict[y1][1])]
                else:
                    xdict[y1] = [x1, x2]
                x1, y1 = xprev, yprev
                continue
            # Non horizontal side
            # Changes in x, y
            dx = x2 - x1
            dy = y2 - y1
            # Determine how steep the line is
            is_steep = abs(dy) > abs(dx)
            # Rotate line
            if is_steep:
                x1, y1 = y1, x1
                x2, y2 = y2, x2
            # Swap start and end points if necessary
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            # Recalculate differentials
            dx = x2 - x1
            dy = y2 - y1
            # Calculate error
            error = dx >> 1
            ystep = 1 if y1 < y2 else -1
            y = y1
            # Calcualte minimum and maximum x values
            for x in range(x1, x2 + 1):
                if is_steep:
                    if x in xdict:
                        xdict[x] = [min(y, xdict[x][0]), max(y, xdict[x][1])]
                    else:
                        xdict[x] = [y, y]
                else:
                    if y in xdict:
                        xdict[y] = [min(x, xdict[y][0]), max(x, xdict[y][1])]
                    else:
                        xdict[y] = [x, x]
                error -= abs(dy)
                if error < 0:
                    y += ystep
                    error += dx
            x1, y1 = xprev, yprev
        # Fill polygon
        for y, x in xdict.items():
            if invert:
                self.back_buffer[y, x[0]:x[1] + 1] ^= 1
            else:
                self.back_buffer[y, x[0]:x[1] + 1] = color

    def draw_letter(self, letter, font, x, y, invert=False, landscape=True):
        """Draws a single letter on the back buffer
        Args:
            letter (string): Letter
            font (XglcdFont object): Font
            x, y (int): Top left coordinates to place font
            invert (Optional boolean): If True inverts font monochrome color. Default is False
            landscape (Optional boolean): Rotates letter 90 degrees.  Default is true.
        Returns:
            int, int: Width and height of the letter in pixels (0,0 if error)
        """
        # Get 2D Numpy array of specified letter
        letter_array = font.get_letter(letter, landscape)
        # Get height and width  of letter
        h, w = letter_array.shape
        if self.is_off_grid(x, y, x + w - 1, y + h - 1):
            return 0, 0
        # Draw letter on self.back_buffer (check if inverted)
        if invert:
            self.back_buffer[y:y + h, x:x + w] = letter_array ^ 1
        else:
            self.back_buffer[y:y + h, x:x + w] = letter_array
        # return letter width and height
        return w, h

    def draw_string(self, text, font, x, y, spacing=1, invert=False, landscape=True):
        """Draws a string of text on the back buffer
        Args:
            text (string): Text
            font (XglcdFont object): Font
            x, y (int): Top left coordinates to place font
            spacing (optonal int): Pixel spacing between letters. Default is 1.
            invert (optional boolean): If True inverts font monochrome color. Default is False
            landscape (optional boolean): Rotates text 90 degrees.  Default is true.
        """
        for letter in text:
            # Get letter array and letter dimensions
            w, h = self.draw_letter(letter, font, x, y, invert, landscape)
            # Stop on error
            if w == 0 & h == 0:
                return
            # Position cursor for next character depending on orientation
            if landscape:
                # Draw vertical spacing if inverted
                if invert and spacing:
                    self.back_buffer[y: y + h, x + w: x + w + spacing] = 1
                # Position x for next letter
                x += w + spacing
            else:
                # Draw horizontal spacing if inverted
                if invert and spacing:
                    self.back_buffer[y + h: y + h + spacing, x: x + w] = 1
                # Position y for next letter
                y += h + spacing

    def draw_bitmap(self, bitmap, x=0, y=0):
        """Draws a raw bitmap to the back buffer
        Args:
            bitmap (Numpy array): 2D array of monochrome pixels
            x, y (int): Top left coordinates to place bitmap
        """
        height, width = bitmap.shape
        self.back_buffer[y:y + height, x:x + width] = bitmap

    def load_bitmap(self, path, width=LCD_WIDTH, height=LCD_HEIGHT, invert=False):
        """Loads a monochrome bitmap (raw format only)
        Args:
            path (string): full source path of raw bitmap file.
            width (Optional int): Pixel width of bitmap. Default is LCD width.
            height (Optional int): Pixel height of bitmap. Default is LCD height.
            invert (Optional boolan): True inverts monochrome color. Default is false.
        Returns:
            Numpy 2D array
        Note:
            You can use the open-source IrfanView graphics program to convert images
            to 1 bpp raw bitmaps.
        """
        bmp = np.fromfile(path, dtype='uint8', sep='')
        # Convert non black colors to 1.
        bmp[bmp > 0] = 1
        if invert:
            return bmp.reshape(height, width)
        else:
            return bmp.reshape(height, width) ^ 1

    def save_bitmap(self, path, x1=0, y1=0, width=LCD_WIDTH, height=LCD_HEIGHT):
        """Saves buffer or a portion of the buffer to a raw bitmap
        Args:
            path (string): full target path for raw bitmap file.
            x1, y1 (Optional int): Top left corner of bitmap.  Default is 0, 0.
            width (Optional int): Pixel width of bitmap. Default is LCD width.
            height (Optional int): Pixel height of bitmap. Default is LCD height.
        Note:
            You can use the open-source IrfanView graphics program to open raw bitmaps.
            You must know the width & height and the bpp which is 8
        """
        # Determine x2, y2
        x2 = x1 + width
        y2 = y1 + height

        if self.is_off_grid(x1, y1, x2 - 1, y2 - 1):
            return

        bmp = self.back_buffer[y1:y2, x1:x2]
        bmp[bmp > 0] = 255
        bmp.tofile(path)
