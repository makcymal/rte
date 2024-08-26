import logging


logger = logging.getLogger(__name__)


class CpuSpecif:
    __slots__ = ("cores_phys", "cores_logic", "min_freq", "max_freq")
    
    
