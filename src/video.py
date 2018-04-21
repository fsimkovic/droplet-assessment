
__author__ = "Felix Simkovic"
__date__ = "16 Apr 2018"
__version__ = "0.1"

from skvideo.io import LibAVWriter, vreader

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class Video(object):
    def __init__(self, path):
        self.path = path


class VideoInSk(Video):
    def __init__(self, path):
        logger.info("Instantiated Skimage video reader")
        super(VideoInSk, self).__init__(path)

    @property
    def frames(self):
        for frame in vreader(self.path):
            yield frame


class VideoOutSk(Video):
    def __init__(self, path):
        super(VideoOutSk, self).__init__(path)
        self._container = LibAVWriter(path)
        self._lock = False

    def add(self, frame):
        if self._lock:
            raise RuntimeError("Video is locked!")
        self._container.writeFrame(frame)

    def save(self):
        self._container.close()
        self._lock = True
