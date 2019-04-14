# Pylon
from pypylon import pylon

# Numpy
import numpy as np

#PyDIP
import PyDIP as dip

from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph.widgets.RemoteGraphicsView
import pyqtgraph as pg
pg.setConfigOptions(imageAxisOrder='row-major')

# Math
import math


class FrameWindow:
    def __init__(self, title):
        """
        Window for showing grabbed frames
        """
        # Graphics window
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.win.resize(600, 400)
        # View Box
        self.view = pg.ViewBox(invertY=True, lockAspect=1)
        # Image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # Plot for axes
        self.win.addPlot(
            row=1, col=1, title='Original Frames', viewBox=self.view)
        # FPS label
        self.fpsLabel = self.win.addLabel(
            'FPS', row=2, col=1, justify='right')
        # Image histogram
        self.hist = pg.HistogramLUTItem(image=self.img, fillHistogram=False)
        self.hist.setLevels(0, 255)
        self.win.addItem(self.hist, row=1, col=2, rowspan=2)

    def update_frame(self, frame):
        self.img.setImage(frame)

    def update_fps(self, fps_value):
        self.fpsLabel.setText(
            text="FPS: {:.2f}".format(fps_value), bold=True)

    def grab_single_frame(self):
        return self.img.image

    def show(self):
        self.win.show()

    def close(self):
        self.win.hide()


class FlowchartPrepWindow:
    """
    Window for preparing image for flowchart
    """
    def __init__(self, title):
        # Empty objects
        self.frame = None
        self.frame_dip = None
        self.frame_dip_roi = None
        # Graphics window
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.win.resize(600, 600)
        self.win.centralWidget.setBorder({'color': (255, 255, 255, 100),
                                          'width': 2})
        # View Box
        self.view = pg.ViewBox(invertY=True, lockAspect=1)
        # Image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # Plot for axes
        self.plot = self.win.addPlot(
            row=1, col=1, rowspan=2, title='Flowchart Input preparation',
            viewBox=self.view
        )
        self.plot.showGrid(x=True, y=True, alpha=0.8)
        # Empty label for proper layout
        self.win.addLabel(row=2, col=1)
        # Crosshair
        self.vline = pg.InfiniteLine(
            angle=90, pen={'color': 'g', 'width': 1}, movable=False)
        self.hline = pg.InfiniteLine(
            angle=0, pen={'color': 'g', 'width': 1}, movable=False)
        self.plot.addItem(self.vline, ignoreBounds=True)
        self.plot.addItem(self.hline, ignoreBounds=True)
        self.proxy = pg.SignalProxy(
            self.plot.scene().sigMouseMoved, rateLimit=60,
            slot=self.on_mouse_move
        )
        #  Pixel intensity label
        self.px_lbl = self.win.addLabel(
            'Pixel Intensity: ', row=3, col=1, bold=True, justify='right')
        # Image histogram
        self.hist = pg.HistogramLUTItem(
            image=self.img, fillHistogram=True)
        self.hist.setLevels(0, 255)
        self.win.addItem(self.hist, row=1, col=2, rowspan=4)
        # ROI selection
        self.roi = pg.ROI(
            pos=(0, 0),
            pen={'color': 'b', 'width': 2},
        )
        # ROI Scaling Handles
        self.roi.addScaleHandle(pos=(0, 0), center=(1, 1))
        self.roi.addScaleHandle(pos=(0, 1), center=(1, 0))
        self.roi.addScaleHandle(pos=(1, 0), center=(0, 1))
        self.roi.addScaleHandle(pos=(1, 1), center=(0, 0))
        self.roi.addScaleHandle(pos=(0, 0.5), center=(1, 0.5))
        self.roi.addScaleHandle(pos=(0.5, 0), center=(0.5, 1))
        self.roi.addScaleHandle(pos=(0.5, 1), center=(0.5, 0))
        self.roi.addScaleHandle(pos=(1, 0.5), center=(0, 0.5))
        self.plot.addItem(self.roi)
        self.roi.setZValue(10)
        # Connect histogram plotting function to ROI change
        self.roi.sigRegionChangeFinished.connect(self.plot_hist_roi)
        # Histogram plot
        self.hist_plot = self.win.addPlot(
            row=4, col=1, title='ROI Histogram')
        self.hist_plot.showGrid(x=True, y=True, alpha=0.8)

    def set_frame(self, frame):
        """
        Set current frame and ROI in ViewBox
        """
        # Frame object
        self.frame = frame
        # DIP Image object
        self.frame_dip = dip.Image(self.frame)
        # Set frame to ImageItem
        self.img.setImage(self.frame)
        # Set ROI size according to frame
        self.roi.setPos((0, 0))
        self.roi.setSize((self.frame.shape[1], self.frame.shape[0]))
        self.roi.maxBounds = QtCore.QRectF(
            0, 0, self.frame.shape[1], self.frame.shape[0])

    def plot_hist_roi(self):
        """
        Update ROI histogram according to ROI size
        """
        # Slicing compatible with dip Image
        slice_tup = self.roi.getArraySlice(
            self.frame, self.img, axes=(0, 1), returnSlice=False)
        slice_tup = [
            slice(tup[0], tup[1]-self.roi.pen.width()) for tup in slice_tup[0]
        ][::-1]
        # print("Slice: {}".format(slice_tup))
        # print("DIP Image: {}".format(self.frame_dip))
        self.frame_dip_roi = self.frame_dip[slice_tup]
        self.hist_plot.clear()
        # self.frame_dip[slice_tup].Show()
        frame_hist_y, frame_hist_x = dip.Histogram(self.frame_dip_roi)
        # Plot Histogram
        self.hist_plot.plot(
            np.asarray(frame_hist_x[0]), np.asarray(frame_hist_y),
            stepMode=False, fillLevel=0, fillBrush=(255, 165, 0, 150))

    def on_mouse_move(self, event):
        pos = event[0]
        if self.plot.sceneBoundingRect().contains(pos):
            coord = self.plot.vb.mapSceneToView(pos)
            if (0 < coord.x() < self.frame_dip.Sizes()[0]) and (
                    0 < coord.y() < self.frame_dip.Sizes()[1]):
                self.px_lbl.setText('Pixel Intensity: {}'.format(
                    self.frame_dip[int(coord.x()), int(coord.y())]))
            self.vline.setPos(coord.x())
            self.hline.setPos(coord.y())

    def get_dip_slice(self):
        return self.frame_dip_roi.Copy()

    def show(self):
        self.win.show()

    def close(self):
        self.win.hide()


class FlowchartPlotWidget(pg.GraphicsLayoutWidget):
    """
    PlotWidget displaying for dip.Image
    """
    def __init__(self, title=None):
        super().__init__()
        # View Box
        self.view = pg.ViewBox(invertY=True, lockAspect=1)
        # Image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # Plot for axes
        self.plot = self.addPlot(
            row=1, col=1, rowspan=1, title=title,
            viewBox=self.view
        )
        self.plot.showGrid(x=True, y=True, alpha=0.8)

    def setImage(self, dip_img):
        """
        Convenience function for displaying dip.Image inside plot
        """
        self.img.setImage(np.asarray(dip_img, dtype=np.uint32))

    def setTitle(self, title):
        """
        Convenience function for setting plot title
        """
        self.plot.setTitle(title)


class MeasureRealtimeWindow:
    def __init__(self):
        """
        Window for real-time measurement
        """
        # Graphics window
        self.win = QtGui.QMainWindow()
        self.win.setWindowTitle('Real-Time Object Measurement')
        # Dock Area
        dockArea = DockArea()
        # Central widget
        self.win.setCentralWidget(dockArea)

        # Window Docks
        origFramesDock = Dock('Original Frames', size=(100, 100))
        # preprocFramesDock = Dock('Preprocessed Frames', size=(100, 100))
        measureResultDocks = Dock('Measurement Result', size=(100, 60))
        dockArea.addDock(measureResultDocks, 'left')
        dockArea.addDock(origFramesDock, 'top', measureResultDocks)
        # dockArea.addDock(preprocFramesDock, 'right', origFramesDock)

        # Window size
        self.win.resize(900, 600)

        # Graphics View
        viewOrig = pg.GraphicsView()
        # viewPreproc = pg.GraphicsView()
        origFramesDock.addWidget(viewOrig)
        # preprocFramesDock.addWidget(viewPreproc)

        """
Measurement result table
data2 = {
    'FeretMin': [12.3, 17.5],
    'FeretMax': [20.7, 21.9],
}
data2 = pd.DataFrame(data=data2)
w.setData(data2.values)
w.setHorizontalHeaderLabels(data2.columns)
w.appendRow([11, 11])
        """

        # PlotItems
        plotOrig = pg.PlotItem()
        # plotPreproc = pg.PlotItem()
        plotOrig.invertY(True)
        # plotPreproc.invertY(True)
        plotOrig.setAspectLocked(True)
        # plotPreproc.setAspectLocked(True)
        viewOrig.setCentralItem(plotOrig)
        # viewPreproc.setCentralItem(plotPreproc)

        # ImageItems
        self.imgOrig = pg.ImageItem(border='w')
        # Auto Downsampling
        # self.imgOrig.setAutoDownsample(True)
        # self.imgPreproc = pg.ImageItem(border='w')
        plotOrig.addItem(self.imgOrig)
        # plotPreproc.addItem(self.imgPreproc)

        # X-axis center line
        self.xAxisCenter = None
        self.vLine = plotOrig.addLine(x=0, pen={'color': 'g', 'width': 2})

        # TableWidget for displaying measurement result
        self.resultTable = pg.TableWidget(sortable=False)
        # Formating for decimal numbers in table
        self.resultTable.setFormat('%.4f')
        measureResultDocks.addWidget(self.resultTable)

        # Column labels for result table
        self.columnLabels = None
        # Row labels for result table
        self.rowLabels = []

        # Number of measured objects
        self.numMeasured = 0

    def update_frame(self, frame):
        """
        Update frame inside ImageItem with np.array

        :param frame: np.array frame
        """
        self.imgOrig.setImage(frame)
        xAxisCenter = frame.shape[1] // 2
        if xAxisCenter != self.xAxisCenter:
            self.vLine.setValue(xAxisCenter)
            self.xAxisCenter = xAxisCenter

    def update_measurement_result(self, resultList):
        """
        Update table with measurement results. Column labels are set only on
        first call

        :param resultList: list of dip.Measurement objects
        """
        # Number of measured objects
        self.numMeasured += 1
        # Measured features
        features = [feat.name for feat in resultList[0].Features()]
        # Outer and inner diameter mark
        whichDiam = ['out', 'in'] * math.ceil(len(resultList) / 2)

        # Set column labels if not already set
        if self.columnLabels is None:
            # Number of values for each measured feature
            num_val = [feat.numberValues for feat in resultList[0].Features()]
            feat_num = [[feat] * num for feat, num in zip(features, num_val)]
            # Flatten list of features
            feat_num = [feat for sublist in feat_num for feat in sublist]
            # List of feature values
            values = [
                ' '.join((val.name, ''.join(('[', str(val.units), ']'))))
                for val in resultList[0].Values()
            ]
            self.columnLabels = [
                ' '.join((feat, val)) for feat, val in zip(feat_num, values)
            ]
            # self.resultTable.setHorizontalHeaderLabels(self.columnLabels)

        # Append rows at the end of table
        for dipMsr, i in zip(resultList, range(len(resultList))):
            # For every dip.Measurement object
            for obj in dipMsr.Objects():
                # For every measured object inside dip.Measurement object
                combinedList = [dipMsr[feat][obj] for feat in features]
                # Flatten combined list
                combinedList = [
                    comb for sublist in combinedList for comb in sublist
                ]
                self.resultTable.appendRow(combinedList)
                # Append row Labels
                self.rowLabels.append(
                    '_'.join((str(self.numMeasured), whichDiam[i]))
                )

        # Set Row labels in table
        self.resultTable.setVerticalHeaderLabels(self.rowLabels)
        self.resultTable.verticalHeadersSet = True
        self.resultTable.setHorizontalHeaderLabels(self.columnLabels)
        self.resultTable.horizontalHeadersSet = True
        self.resultTable.resizeColumnsToContents()

    def setTableColumnLabels(self, headerLabels):
        """
        Set result table column labels with list of strings

        :param headerLabels: list of column headers
        """
        self.resultTable.setHorizontalHeaderLabels(headerLabels)

    def appendResultRow(self, measurementResult):
        """
        Append measurement results at the end of table

        :param measurementResult: list or np.ndarray of measurement results
        """
        self.resultTable.appendRow(measurementResult)


    # def update_preproc_frame(self, frame):
    #     self.imgPreproc.setImage(frame)

    def show(self):
        self.win.show()

    def close(self):
        self.win.hide()


class SignalChange(QtCore.QObject):
    """
    Signal for communication between threads
    """
    updateGraphics = QtCore.pyqtSignal()
    updateFPS = QtCore.pyqtSignal()

