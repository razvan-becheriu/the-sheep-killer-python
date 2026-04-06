import logging
import sys

# Initialize the logger for the application
log = logging.getLogger("TheSheepKiller")
log.setLevel(logging.DEBUG)

# Professional format: Timestamp [Level] Message
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

# Console Handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

# File Handler (Appends to game.log like the Pascal logger.pas)
file_handler = logging.FileHandler("game.log", mode='a')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

log.info("Logger initialized.")