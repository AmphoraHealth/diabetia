# This is a library to standardize the data logging messages
import logging

# custom class to format the logging messages
class CustomFormatter(logging.Formatter):
  # Define color codes
  grey = "\x1b[38;20m"
  yellow = "\x1b[33;20m"
  red = "\x1b[31;20m"
  bold_red = "\x1b[31;1m"
  reset = "\x1b[0m"
  # Define log format
  format = "%(asctime)s|%(name)s|%(levelname)s: %(message)s"
  datefmt = "%y-%m-%d %H:%M:%S"

  # Define log formats for each level
  FORMATS = {
    logging.DEBUG: grey + format + reset,
    logging.INFO: grey + format + reset,
    logging.WARNING: yellow + format + reset,
    logging.ERROR: red + format + reset,
    logging.CRITICAL: bold_red + format + reset
  }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt,self.datefmt)
    return formatter.format(record)
  

# set the custom formatter applying the new date format
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.root.handlers = [handler]
