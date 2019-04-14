import sys

# Visualize frames
from gui.visualize import FrameWindow, FlowchartPrepWindow,\
    MeasureRealtimeWindow, SignalChange

# Flowchart frames
from gui.flowcharts import FlowchartCalibrateWindow, FlowchartMeasureWindow

# PyQtGraph
import pyqtgraph as pg
from gui.ptrees import CameraParams, CalibrationParams
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock
from pyqtgraph import ptime

# Numpy
import numpy as np

# DIPlib
import PyDIP as dip

# Camera object
from cam.cam import CamObject
from cam.event_handlers import FrameGrabEventHandler, FrameMeasureEventHandler
from pypylon import pylon

# Parallel processing
from processing.process import ProcessParallel

# Queue module
import queue


class MeasuringApp(CamObject, QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        CamObject.__init__(self)
        QtGui.QMainWindow.__init__(self)
        self.resize(700, 150)
        self.setWindowTitle('Workpiece Dimensional Control')
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # Window Docks
        self.camMenuDock = Dock('Camera Menu', size=(1, 1))
        self.procMenuDock = Dock('Analysis Menu', size=(1, 1))
        self.paramDock = Dock('Parameter Tree', size=(250, 150))
        self.area.addDock(self.camMenuDock, 'right')
        self.area.addDock(self.procMenuDock, 'right')
        self.area.addDock(self.paramDock, 'left')

        # Parameter Tree
        self._parameter_tree = ParameterTree()
        self._parameter_tree.setWindowTitle('Parameter Tree')
        self.paramDock.addWidget(self._parameter_tree)

        # Camera Menu
        self._cam_menu = pg.LayoutWidget(parent=self.camMenuDock)
        self._cam_buttons = self.cam_buttons()
        [btn.resize(btn.minimumSizeHint()) for btn in self._cam_buttons]
        [self._cam_menu.addWidget(btn, row=i, col=0) for btn, i in zip(
            self._cam_buttons, range(len(self._cam_buttons)))]
        self.camMenuDock.addWidget(self._cam_menu)

        # Analysis menu
        self._proc_menu = pg.LayoutWidget(parent=self.procMenuDock)
        self._proc_buttons = self.process_buttons()
        [btn.resize(btn.minimumSizeHint()) for btn in self._proc_buttons]
        [self._proc_menu.addWidget(btn, row=i, col=1) for btn, i in zip(
            self._proc_buttons, range(len(self._proc_buttons)))]
        self.procMenuDock.addWidget(self._proc_menu)

        # Original frames window
        self._orig_frame = FrameWindow("Original")

        # Flowchart input preparation window
        self._prep_flow = FlowchartPrepWindow('Flowchart Input preparation')

        # Calibrate system window
        self._calib_window = FlowchartCalibrateWindow()
        # Calibration Parameters
        self._calib_params = None

        # Measurement preparation window
        self._measure_prep_window = FlowchartMeasureWindow()

        # Realtime measurement window
        self._realtime_measure_window = MeasureRealtimeWindow()

        # Show Main Window
        self.show()

        # Result Queue init
        self.preproc_queue = queue.Queue()

        # FPS display count
        self.fps_display_count = 0

    def cam_buttons(self):
        """
        Menu buttons as list
        """
        # Camera create button
        cam_create = QtGui.QPushButton('Find Camera', parent=self._cam_menu)
        cam_create.clicked.connect(self.create)
        # Camera open button
        cam_open = QtGui.QPushButton('Open Camera', parent=self._cam_menu)
        cam_open.clicked.connect(self.open)
        # Camera print info
        cam_print_info = QtGui.QPushButton('Print Info', parent=self._cam_menu)
        cam_print_info.clicked.connect(self.print_info)
        # Camera start grabbing
        cam_start_grab = QtGui.QPushButton(
            'Start Grabbing', parent=self._cam_menu)
        cam_start_grab.clicked.connect(self.start_grabbing)
        # Camera stop grabbing
        cam_stop_grab = QtGui.QPushButton(
            'Stop Grabbing', parent=self._cam_menu)
        cam_stop_grab.clicked.connect(self.stop_grabbing)
        # Camera close
        cam_close = QtGui.QPushButton('Close Camera', parent=self._cam_menu)
        cam_close.clicked.connect(self.close)
        return [
            cam_create, cam_open, cam_print_info, cam_start_grab,
            cam_stop_grab, cam_close
        ]

    def process_buttons(self):
        """
        Process buttons as list
        """
        # Grab single frame button
        proc_grab_frame = QtGui.QPushButton(
            'Grab Frame', parent=self._proc_menu)
        proc_grab_frame.clicked.connect(self.grab_single_frame)
        proc_discard_frame = QtGui.QPushButton(
            'Discard Frame', parent=self._proc_menu)
        proc_discard_frame.clicked.connect(self.discard_frame)
        proc_calib_sys = QtGui.QPushButton(
            'Calibrate System', parent=self._proc_menu)
        proc_calib_sys.clicked.connect(self.calibrate_system)
        proc_set_calib_const = QtGui.QPushButton(
            'Set Calibration Constants', parent=self._proc_menu)
        proc_set_calib_const.clicked.connect(self.set_calib_const)
        proc_measure_prep = QtGui.QPushButton(
            'Measurement Preparation', parent=self._proc_menu)
        proc_measure_prep.clicked.connect(self.measurement_preparation)
        proc_realtime_start = QtGui.QPushButton(
            'Start Measurement', parent=self._proc_menu)
        proc_realtime_start.clicked.connect(self.start_realtime_measurement)
        proc_realtime_stop = QtGui.QPushButton(
            'Stop Measurement', parent=self._proc_menu)
        proc_realtime_stop.clicked.connect(self.stop_realtime_measurement)
        return [
            proc_grab_frame, proc_discard_frame, proc_calib_sys,
            proc_set_calib_const, proc_measure_prep, proc_realtime_start,
            proc_realtime_stop
        ]

    def open(self):
        """
        Reimplementation of open function to update GUI numbers and sliders
        """
        super().open()
        self._parameter_tree.clear()
        self._parameter_tree.addParameters(
            CameraParams(name='Camera Parameters', cam_obj=self), showTop=True)

    def close(self):
        """
        Reimplementation of close function to update GUI numbers and sliders
        """
        super().close()
        self._parameter_tree.clear()

    def set_default_params(self):
        """
        Reimplementation of set_default_params function to update GUI
        """
        super().set_default_params()
        self._cam_gain.value = self.cam.Gain()
        self._cam_exposure.value = self.cam.ExposureTime()
        self._cam_width.value = self.cam.Width.GetValue()
        self._cam_height.value = self.cam.Height.GetValue()
        self._cam_offsetx.value = self.cam.OffsetX.GetValue()
        self._cam_offsety.value = self.cam.OffsetY.GetValue()

    def start_grabbing(self, strategy=pylon.GrabStrategy_LatestImageOnly):
        """
        Reimplementation of start_grabbing to show new window
        """
        if not self.cam.IsGrabbing():
            self._orig_frame.show()
            self.frame_queue = queue.Queue()
            fg_hndl = FrameGrabEventHandler(self.frame_queue)
            # Frame grab event registering
            self.cam.RegisterImageEventHandler(
                fg_hndl,
                pylon.RegistrationMode_ReplaceAll,
                pylon.Cleanup_Delete
            )
            super().start_grabbing(strategy)
            self.frame_burst(graphicsObject=self._orig_frame)

    def stop_grabbing(self):
        """
        Reimplementation of stop_grabbing to close new window
        """
        if self.cam.IsGrabbing():
            super().stop_grabbing()
            self._orig_frame.close()

    def frame_burst(self, graphicsObject, updateFrame=True, updateFPS=True,
                    updateMeasurementResult=False, numProc=1, fps_display=5):
        """
        Grab frames from camera using software trigger, scheduling and event
        handler.
        frame_burst reimplementation for FPS, frame and measurement result
        update.

        :param graphicsObject: object which methods are called and graphics updated
        :param updateFrame: bool
        :param updateFPS: bool
        :param updateMeasurementResult: bool
        :param numProc: 1
        :param fps_display: int
        """
        if self.fps_count == 0:
            if updateFPS:
                # Update graphicsObject FPS label
                graphicsObject.update_fps(self.fps)
            self.fps_start = pg.ptime.time()
        if self.cam.IsGrabbing():
            for _ in range(numProc):
                if self.cam.WaitForFrameTriggerReady(
                        300, pylon.TimeoutHandling_ThrowException):
                    self.cam.ExecuteSoftwareTrigger()
            frames = [self.frame_queue.get() for _ in range(numProc)]
            self.fps_display_count += 1
            # print('FPS_display_count: {}'.format(self.fps_display_count))
            if updateFrame and not (self.fps_display_count % fps_display):
                self.fps_display_count = 0
                # Update graphicsObject ImageItem
                [graphicsObject.update_frame(frame) for frame in frames]
                self.fps_count += numProc
            if updateMeasurementResult:
                while not self.preproc_queue.empty():
                    graphicsObject.update_measurement_result(
                        self._measure_prep_window.fc_process(
                            dip.Image(self.preproc_queue.get())
                        ))
            # Average FPS on number of frames
            if self.fps_count >= 10:
                fps_time = pg.ptime.time() - self.fps_start
                self.fps = self.fps_count / fps_time
                print("Camera FPS: {:.2f}".format(
                    self.cam.ResultingFrameRate.GetValue()))
                print("FPS: {:.2f}".format(self.fps))
                self.fps_count = 0
            QtCore.QTimer.singleShot(
                1, lambda : self.frame_burst(graphicsObject,
                                             updateFrame,
                                             updateFPS,
                                             numProc,
                                             ))

    def grab_single_frame(self):
        self._prep_flow.set_frame(self._orig_frame.grab_single_frame())
        self._prep_flow.show()

    def discard_frame(self):
        self._prep_flow.close()

    def calibrate_system(self):
        """
        Show Calibration flowchart and set input frame
        """
        self._calib_window.setInput(self._prep_flow.get_dip_slice())
        self._calib_window.show()

    def set_calib_const(self):
        """
        Set and show calibration parameters in parameterTree
        """
        standard_dict = self._calib_window.output()
        self._calib_params = CalibrationParams(
            name='Calibration Parameters', standard_dict=standard_dict)
        self._parameter_tree.clear()
        self._parameter_tree.addParameters(self._calib_params, showTop=True)

    def measurement_preparation(self):
        """
        Show Measurement preparation flowchart and set input frame
        """
        self._measure_prep_window.setInput(
            self._prep_flow.get_dip_slice(),
            self._calib_params.obj_mm_px.value()
        )
        self._measure_prep_window.show()

    def start_realtime_measurement(
            self, strategy=pylon.GrabStrategy_LatestImageOnly):
        """
        Show window for realtime measurement and start grabbing frames from cam
        """
        if not self.cam.IsGrabbing():
            self._realtime_measure_window.show()
            procParallel = ProcessParallel(
                self._measure_prep_window, numberProc=3
            )
            # Queue for storing frames
            self.frame_queue = queue.Queue()
            # Queue for storing measurement result list
            self.preproc_queue = queue.Queue()
            self.fm_hndl = FrameMeasureEventHandler(
                self.frame_queue, self.preproc_queue, procParallel
            )
            # Frame grab event registering
            self.cam.RegisterImageEventHandler(
                self.fm_hndl,
                pylon.RegistrationMode_ReplaceAll,
                pylon.Cleanup_Delete
            )
            super().start_grabbing(strategy)
            self.frame_burst(
                graphicsObject=self._realtime_measure_window,
                updateFPS=False, updateMeasurementResult=True,
                fps_display=10,
                # numProc=procParallel.getNumProc()
            )

    def stop_realtime_measurement(self):
        """
        Close window for realtime measurement and stop grabbing frames from cam
        """
        if self.cam.IsGrabbing():
            super().stop_grabbing()
            self._realtime_measure_window.close()
            self.cam.DeregisterImageEventHandler(self.fm_hndl)
