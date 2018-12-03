# -*- coding: utf-8 -*-
import numpy as np

class XglcdFont(object):
    """Font data in X-GLCD format
    Attributes:
        letters: A 2D Numpy array of letters (rows are letters, cols are bytes)
        width: Maximum pixel width of font
        height: Pixel height of font
        start_letter: ASCII number of first letter
        height_bytes: How many bytes comprises letter height
        
    Note: 
        Font files can be generated with the free version of MikroElektronika 
        GLCD Font Creator:  www.mikroe.com/glcd-font-creator  
        The font file must be in X-GLCD 'C' format.
        To save text files from this font creator program in Win7 or higher 
        you must use XP compatibility mode or you can just use the clipboard.
    """

    def __init__(self, path, width, height, start_letter = 32):
        """Constructor for X-GLCD Font object.
        Args:
            path (string): Full path of font file
            width (int): Maximum width in pixels of each letter
            height (int): Height in pixels of each letter
            start_letter (int): First ACII letter.  Default is 32.
        """
         
        self.width = width
        self.height = height
        self.start_letter = start_letter
        self.letters = self.__load_xglcd_font(path)
        self.height_bytes = int((self.letters.shape[1] - 1) / width)

                      
    def __load_xglcd_font(self, path):
        """Loads X-GLCD font data from text file
        Args:
            path (string): Full path of font file
        Returns: 
            Numpy Array(Uint8): 2D - rows=letters, cols=letter bytes
        """
        data = []
        with open(path, 'rb') as f:
            for line in f:
                # Remove comments
                cpos = line.find(b'//')
                if cpos != -1:
                    line = line[0:cpos]
                # Skip lines that do not start with hex values
                line = line.decode()
                line = line.strip()
                if len(line) == 0 or line[0:2] != '0x':
                    continue
                # Remove trailing commas
                if line.endswith(','):
                    line = line[0:len(line) - 1]
                # Convert hex strings to integers and append     
                data.append([int(x, 16) for x in line.split(',')])
        return np.array(data).astype('uint8')       


    def get_letter(self, letter, landscape=True):
        """Converts 1D letter byte data to 2D bit array
        Args:
            letter (string): Letter to return.
            landscape (boolean): Rotates letter 90 degrees.  Default is true.
        Returns:
            Numpy Array(Uint8): 2D bit representation of letter
        """
        # Get index of letter
        letter_ord = ord(letter) - self.start_letter 
        # Get width of letter (specified by first byte)
        letter_width = self.letters[letter_ord, 0]
        # Get 1D byte array of the letter
        letter_array = self.letters[letter_ord,1:]
        # Remove font byte width padding
        letter_array = letter_array[:(letter_width * self.height_bytes) + self.height_bytes]
        # Reorder bytes if height is comprised of more than 1 byte
        if self.height_bytes > 1:
            letter_array = np.fliplr(letter_array.reshape(-1, self.height_bytes)).ravel()
        # Unpack bytes to bits that comprise font columns
        letter = np.unpackbits(letter_array).reshape(-1, self.height_bytes << 3)
        if landscape:
            # Rotate font and remove font byte height padding.  Then return letter array
            return np.rot90(letter)[: self.height]
        else:
            # Remove font byte height padding and return letter array
            return letter[: , -self.height :]
            
            
    def measure_text(self, text, spacing=1):
        """Measure length of text string in pixels
        Args:
            text (string): Text string to measure
            spacing (optional int): Pixel spacing between letters.  Default is 1.
        Returns:
            int: length of text
        """
        length = 0
        for letter in text:
            # Get index of letter
            letter_ord = ord(letter) - self.start_letter
            # Add length of letter and spacing
            length += self.letters[letter_ord, 0] + spacing
        return length
            
            
            
