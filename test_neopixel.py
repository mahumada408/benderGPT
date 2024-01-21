import board
import neopixel
import time

# Configuration for the NeoPixel strip
PIN = board.D18  # The pin that the NeoPixel is connected to
NUM_PIXELS = 112  # Number of pixels (7 rows x 16 columns)
ROWS = 8
COLUMNS = 16
BRIGHTNESS = 0.5  # Brightness level, range from 0.0 to 1.0

# Create the NeoPixel object
pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, auto_write=False, brightness=0.01)

def set_pixel(row, col, color):
    """
    Calculate the LED index for the given row and column.

    Args:
    row (int): The row number (0-indexed).
    col (int): The column number (0-indexed).

    Returns:
    int: The index of the LED in the strip.
    """
    if col % 2 == 0:
        # For even columns, the index increases from top to bottom
        index = col * ROWS + row
    else:
        # For odd columns, the index increases from bottom to top
        index = col * ROWS + (ROWS - 1 - row)
    
    print(index)
    pixels[index] = color

def show():
    """Update the display with the data from the pixel buffer."""
    pixels.show()

def clear():
    """Clear the display."""
    pixels.fill((0, 0, 0))
    show()

try:
    while True:
        # Example: Set the whole display to red
        set_pixel(3, 2, (255, 255, 0))
        show()
        time.sleep(1)

        # Clear the display
        clear()
        time.sleep(1)

except KeyboardInterrupt:
    # Clear display on exit
    clear()