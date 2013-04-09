#!/usr/bin/python

import logging
import inspect
import sys

logger = logging.getLogger(__name__)

def initLogging(options):
  format="%(asctime)s %(levelname)s:%(message)s"
  level = logging.INFO
  if(options.Quiet):
    level = logging.WARN
  elif(options.Verbose):
    level = logging.DEBUG

  if(options.LogFile):
    logging.basicConfig(format=format, filename=options.LogFile, filemode='w', level=level)
  else:
    logging.basicConfig(format=format, level=level)
  logging.captureWarnings(True)

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
