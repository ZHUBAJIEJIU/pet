import functools
import logging
 
def create_logger():
  logger = logging.getLogger("test_log")
  logger.setLevel(logging.INFO)
  fh = logging.FileHandler("test.log")
  fmt = "\n[%(asctime)s-%(name)s-%(levelname)s]: %(message)s"
  formatter = logging.Formatter(fmt)
  fh.setFormatter(formatter)
  logger.addHandler(fh) 
  return logger
 
def log_exception(fn):
  @functools.wraps(fn)
  def wrapper(*args, **kwargs):
 
    logger = create_logger()
    try:
      fn(*args, **kwargs)
    except Exception as e:
      logger.exception("[Error in {}] msg: {}".format(__name__, str(e)))
      raise
  return wrapper