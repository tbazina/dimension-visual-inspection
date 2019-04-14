import PyDIP as dip
import numpy as np

# Multiprocessing
# import multiprocessing
import multiprocess as multiprocessing

class ProcessParallel:
    def __init__(self, measureFlowchart, numberProc=1):
        """
        Object for parallel processing and preprocessing of image frames
        """
        # Flowchart object, queues and processes
        self.measureFlowchart = measureFlowchart
        self.input_queue = multiprocessing.JoinableQueue(1)
        self.output_queue = multiprocessing.Queue()
        self.numberProc = numberProc
        self.processes = [
            ProcessQueue(self.input_queue, self.output_queue)
            for _ in range(self.numberProc)
        ]

    @staticmethod
    def preprocess_frame(frame):
        """
        Hardcoded function for real-time frame preprocessing. Returns image
        for measurement of None

        :param frame: 2D array
        :return: np.array or None
        """
        img = dip.Image(frame)
        img_center_x = img.Sizes()[0]//2
        # Range Thresholding
        thr = dip.RangeThreshold(
            img, lowerBound=30, upperBound=240,
            foreground=1.0, background=0.0
        )
        # Fill holes
        fill = dip.FillHoles(thr)
        # Label and measure
        lbl = dip.Label(fill, connectivity=1, minSize=10000)
        if dip.GetObjectLabels(lbl):
            msr = dip.MeasurementTool.Measure(
                lbl, img, ['Center', 'Minimum', 'Maximum', 'PodczeckShapes'])
            for obj in msr.Objects():
                # Ellipse Podczeck
                if 0.98 <= msr['PodczeckShapes'][obj][3] <= 1.02:
                    # Object location near x-axis center
                    if (img_center_x-150 <= msr['Center'][obj][0] <=
                            img_center_x+150):
                        # Expand box around object for measurement
                        min_x = int(msr['Minimum'][obj][0] - 50)
                        min_y = int(msr['Minimum'][obj][1] - 50)
                        max_x = int(msr['Maximum'][obj][0] + 50)
                        max_y = int(msr['Maximum'][obj][1] + 50)
                        # Only one object can be measured
                        return np.asarray(
                            img[min_x:max_x, min_y:max_y], np.uint32
                        )
        # Return None if no object is near x-axis center
        return None

    def start(self):
        """
        Start parallel execution
        """
        [proc.start() for proc in self.processes]

    def addInput(self, frame):
        """
        Add frame to input Queue
        """
        self.input_queue.put((self.preprocess_frame, frame))

    def addMeasurementInput(self, measured_object):
        """
        Add image of measured object to input Queue for measuring
        :param measured_object: np.ndarray
        """
        mes_obj = dip.Image(measured_object)
        self.input_queue.put((self.measureFlowchart.fc_process, mes_obj))

    def getOutput(self):
        """
        Retrieve Queue output
        """
        return self.output_queue.get()

    def getNumProc(self):
        """
        Return number of processes
        """
        return self.numberProc

    def ifInputQueueFull(self):
        """
        Check if input queue is full

        :return: True or False
        """
        return self.input_queue.full()

    def ifOutputQueueFull(self):
        """
        Check if output queue is full

        :return: True or False
        """
        return self.output_queue.full()

    def ifOutputQueueEmpty(self):
        """
        Check if output queue is empty

        :return: True or False
        """
        return self.output_queue.empty()

    def join(self):
        """
        Wait for processing to finish
        """
        self.input_queue.join()

    def stop(self):
        """
        Stop parallel execution
        """
        [self.input_queue.put(None) for _ in range(self.numberProc)]


class ProcessQueue(multiprocessing.Process):
    def __init__(self, input_queue, output_queue):
        """
        Process for taking data from input_queue and writing into output_queue.
        Exit with poison pill (None)
        """
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        """
        Infinite loop with poison pill exit
        """
        while True:
            input_tup = self.input_queue.get()
            if input_tup is None:
                self.input_queue.task_done()
                break
            func, args = input_tup
            res = func(args)
            self.input_queue.task_done()
            self.output_queue.put(res)
