import os
import json
import logging
from copy import deepcopy as cp
from utils import Publisher, Singleton
import config


logger = logging.getLogger(__name__)


class Query(Publisher, metaclass=Singleton):

  __slots__ = (
    "_qry",
    "_default_qry",
    "_subs",
    "qryfile",
    "logfile",
    "loglevel",
  )

  def __init__(self):
    super().__init__()

    if not config.DEBUG:
      self.logfile = "rte-sensor.log"
      # self.logfile = "/var/log/rte/rte-sensor.log"
      self.loglevel = logging.INFO
    else:
      self.logfile = "rte-sensor.log"
      self.loglevel = logging.DEBUG

    with open(self.logfile, "w"):
      pass

    self.qryfile = os.path.join(
      os.path.dirname(__file__), "query.fallback.json"
    )
    with open(self.qryfile, "r") as qryfile:
      self._default_qry = json.load(qryfile)
      self._qry = cp(self._default_qry)

    logger.info(f"Query initialized with debug = {config.DEBUG}")

  def update(self, qry_str: str):
    self._qry = json.loads(qry_str)
    logger.info("Updating query: ok")
    self.notify_subs()

  def __getitem__(self, key: str):
    try:
      return self._qry[key]
    except Exception as err:
      logger.error(f"Invalid query: {str(err)}")
      logger.warning("Default query will be used")
      self._qry = cp(self._default_qry)
