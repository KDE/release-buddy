#!/usr/bin/python

import logging
import inspect
import sys

logger = logging.getLogger()

def initLogging(options):
  format="%(asctime)s %(levelname)s:%(message)s"
  formatter = logging.Formatter(format)

  logging.captureWarnings(True)

  level = logging.INFO
  try:
    if(options.Quiet):
      level = logging.WARN
    elif(options.Verbose):
      level = logging.DEBUG
  except AttributeError:
    pass

  logger.setLevel(level)
  try:
    if(options.LogFile):
      fh = logging.FileHandler(filename=options.LogFile, mode='w')
      fh.setLevel(level)
      fh.setFormatter(formatter)
      logger.addHandler(fh)
  except AttributeError:
    pass

  ch = logging.StreamHandler()
  ch.setLevel(level)
  ch.setFormatter(formatter)
  logger.addHandler(ch)

def _getIndentaion():
  return 0
  frame,filename,line_number,function_name,lines,index=inspect.getouterframes(
          inspect.currentframe())[2]
  line=lines[0]
  indentation_level=line.find(line.lstrip())
  return indentation_level


def debug(msg, options = None):
  if options is None or not options.Quiet:
    indentation_level = _getIndentaion();
    logger.debug('{i}{m}'.format(i=' '*indentation_level, m=msg))

def info(msg, options = None):
  if options is None or not options.Quiet:
    indentation_level = _getIndentaion();
    logger.info('{i}{m}'.format(i=' '*indentation_level, m=msg))

def warn(msg, options = None):
  indentation_level = _getIndentaion();
  logger.warn('{i}{m}'.format(i=' '*indentation_level, m=msg))

def error(msg, options = None):
  indentation_level = _getIndentaion();
  logger.error('{i}{m}'.format(i=' '*indentation_level, m=msg))

def fail(message, options = None):
  logger.error("Failure: " + message)
  sys.exit(1)
