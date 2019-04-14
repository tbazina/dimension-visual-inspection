# Pypylon
from pypylon import pylon

# Numpy
import numpy as np

# Time
import time

# Pyqtgraph
import pyqtgraph as pg
from pyqtgraph import QtCore

from gui.visualize import SignalChange


class FrameGrabEventHandler(pylon.ImageEventHandler):
    def __init__(self, frame_queue):
        """
        Image event handler for showing grabbed frame and FPS in FramePlotter
        """
        super().__init__()
        self.frame_queue = frame_queue

    def OnImageGrabbed(self, cam, grabResult):
        if grabResult.GrabSucceeded():
            imgArray = grabResult.GetArray()
            self.frame_queue.put(imgArray)


class FrameMeasureEventHandler(pylon.ImageEventHandler):
    def __init__(self, frame_queue, preproc_queue, procParallel):
        """
        Image event handler for Real-Time measurement window

        :param frame_queue: Queue for displaying frames in window

        :param procParallel: Object for parallel processing
        """
        super().__init__()
        self.frame_queue = frame_queue
        self.preproc_queue = preproc_queue
        self.procParallel = procParallel
        self.numProc = procParallel.getNumProc()
        self.frame_num = 0
        # Time delay in seconds between measurement
        self.timeDelay = 10

    def checkTimeDelay(self):
        """
        Convenience function for measuring time between frames for measuring

        :return: True of False
        """
        if self.startTime:
            if (pg.ptime.time() - self.timeDelay) > self.startTime:
                # self.startTime = pg.ptime.time()
                return True
            else:
                return False
        return True

    def OnImageEventHandlerRegistered(self, cam):
        """
        Start parallel processing when event handler is registered
        """
        self.procParallel.start()
        # self.startTime = pg.ptime.time()
        self.startTime = None

    def OnImageGrabbed(self, cam, grabResult):
        """
        Called in internal thread on every image grabbed from camera
        """
        if grabResult.GrabSucceeded():
            imgArray = grabResult.GetArray()
            # Put frame in queue for displaying
            self.frame_queue.put(imgArray)
            # print('Put {} frame for display'.format(self.frame_num))
            # self.frame_num += 1
            if not self.procParallel.ifInputQueueFull():
                # Add frame to preprocessing if queue not full
                self.procParallel.addInput(imgArray)
                # print('Parallel addInput')
            # Grab all results
            while not self.procParallel.ifOutputQueueEmpty():
                # print('Acquiring Parallel Output')
                res = self.procParallel.getOutput()
                # Preprocessing outputs None if object is not centered
                if res is not None:
                    # Preprocessing outputs np.ndarray if object is centered
                    if isinstance(res, np.ndarray):
                        # print('Parallel Output is frame')
                        # Do not put frames for preprocessing if the same object
                        if self.checkTimeDelay():
                            # Put centered object in queue for measurement
                            self.preproc_queue.put(res)
                            self.startTime = pg.ptime.time()
                # print('Parallel Output None')

            # self.frame_num += 1
            # if self.frame_num >= self.numProc:
            #     self.procParallel.join()
            #     # now = time.time()
            #     preprocImgArrays = [
            #         self.procParallel.getOutput() for _ in range(self.numProc)
            #     ]
            #     # print(time.time() - now)
            #     [self.frame_queue.put(preprocImgArray)
            #      for preprocImgArray in preprocImgArrays]
            #     self.frame_num = 0

    def OnImageEventHandlerDeregistered(self, cam):
        """
        Stop parallel processing when event handler is deregistered
        """
        self.procParallel.stop()
        self.procParallel.join()
