# Pi-ST7565

ST7565 Graphics LCD Display Python Library for Raspberry Pi.
Tested with Adafruit ST7565 module.
Full tutorial on my website [Rototron](http://www.rototron.info/raspberry-pi-graphics-lcd-display-tutorial/) or click picture below for a YouTube video:

[![ST7565 Tutorial](http://img.youtube.com/vi/Nn5u9xhHCTM/0.jpg)](https://youtu.be/Nn5u9xhHCTM)

### Examples

```bash
python example_polygons.py
```

When not running on an actual Raspberry Pi, use:

```bash
MOCK_RPI=true python example_polygons.py
```

### Soft display

To ease software development, you can use a software display, which uses pygame:

```python
if os.environ.get('MOCK_RPI'):
    from soft_display import mock_gpio, Glcd
    mock_gpio()
else:
    from st7565 import Glcd
```