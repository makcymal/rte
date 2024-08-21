import typing as tp
import logging
from abc import abstractmethod, ABC


logger = logging.getLogger(__name__)


class Subscriber(ABC):

  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def get_update(self):
    pass


class Publisher:
  __slots__ = ("_subs",)
  _subs: tp.Set[Subscriber]

  def __init__(self):
    self._subs = set()

  def subscribe(self, sub: Subscriber):
    self._subs.add(sub)
    logger.debug(f"{str(sub)} subscribed")

  def unsubscribers(self, sub: Subscriber):
    self._subs.remove(sub)
    logger.debug(f"{str(sub)} unsubscribed")

  def notify_subs(self):
    for sub in self._subs:
      sub.get_update()
    logger.debug("Notifying subscribers: ok")


class Singleton(type):
  _instance = None

  def __call__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super().__call__(*args, **kwargs)
      logger.debug(f"Singleton {cls} instantiated")
    return cls._instance
