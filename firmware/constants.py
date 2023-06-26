# Debug Flags
DEBUG = False
LED_TESTING = True
HR_TESTING = True

# Board Configuration
SDA_PIN = 16
SCL_PIN = 17
OX_LED_PIN = 19
DEOX_LED_PIN = 18
PICO_LED_PIN = 25

# LED Constants
LED_INTENSITY = 255
BLINK_DELAY = 0.075 # Was 0.05
TROB_RATE  = 0.005
TROB_DELAY = 3
ERROR_DELAY = 3
LED_OFF = tuple([0, 0, 0])
LED_COUNT = 7
HEART_PATTERN = [0.1, 1, 0.1]
HEART_LED_INTENSITY = 255
CEREAL_DELAY = 0.075

# HR Constants
I2C_FREQ = 100000

# Cereal Interface Constants
CEREAL_COLOR_SCHEMES = {
  'cinnamontoastcrunch': ['ce9958', '724705', 'd8d09f', 'b8732d', '9f633b'],
  'fruitypebbles': ['f0aa37', 'ffd52b', '00ffd7', '2edfb4', '10b990'],
  'luckycharms': ['216209', '8fac06', 'bdd9a3', '56a20d', '91d521'],
  'fruitloops': ['ff0000', 'ffe700', '7cff00', 'c900ff', '00dfff'],
  'applejacks': ['ffc360', 'fff4a3', 'e4a95d', '5caf4c', 'ff6254'],
  'trix': ['58e3ff', '87a2ff', 'af7ffc', 'da4e7d', 'f14848'], 
  'rainbow': ['ee82ee', '4b0082', '0000ff', '008000', 'ffff00', 'ffa500', 'ff0000']
}

# Old Junk Constants
HEART_RATE_SPAN = [10,250] # max span of heart rate
PTS = 1800 # points used for peak finding (400 Hz, I recommend at least 4s (1600 pts)
SMOOTHING_SIZE = 20 # convolution smoothing size
OFFSET = 0