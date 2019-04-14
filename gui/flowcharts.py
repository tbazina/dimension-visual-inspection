import pyqtgraph as pg
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

# Itertools
import itertools

# Plot Widget
from gui.visualize import FlowchartPlotWidget

# Custom nodes
from processing.nodes import (
    FlowchartPlotNode, GaussianConvolutionNode, ThresholdNode,
    RangeThresholdNode, OpeningNode, ClosingNode, DilationNode, ErosionNode,
    EdgeObjectsRemoveNode, ConvertNode, InvertNode, CannyNode, GradientNode,
    GradientMagnitudeNode, GradientDirectionNode, WatershedNode,
    SeededWatershedNode, MinimaNode, MaximaNode, ApplyMaskNode, CreateMaskNode,
    FillNode, BinaryPropagationNode, FillHolesNode, LabelNode, MeasureNode,
    MeasurementDisplayNode, WorkingDistanceCorrectionNode, CalibDisplayNode,
    SegmentORingNode, ORingMeasurementDisplayNode, SetPixelSizeNode,
    KuwaharaNode, BilateralFilterNode, BinaryAreaClosingNode,
    BinaryAreaOpeningNode, BinaryClosingNode, BinaryOpeningNode,
    BinaryDilationNode, BinaryErosionNode, OperatorPlusNode,
    CombineMeasurementNode
)


class FlowchartCalibrateWindow:
    def __init__(self):
        """
        Flowchart inside new window for system calibration
        """
        # Graphics window
        self.win = QtGui.QMainWindow()
        self.win.setWindowTitle('System Calibration Flowchart')
        # Dock Area
        dockArea = DockArea()
        # Central widget
        self.win.setCentralWidget(dockArea)

        # Window Docks
        fcWidgetDock = Dock(
            'Flowchart Widget', size=(1, 1), hideTitle=True)
        displayDock = Dock('Measurement and Calibration', size=(1, 1))
        plotDocks = [
            Dock('Plot {}'.format(i), size=(1, 1)) for i in range(4)
        ]
        dockArea.addDock(fcWidgetDock, 'left')
        dockArea.addDock(displayDock, 'right', fcWidgetDock)
        dockArea.addDock(plotDocks[0], 'top', displayDock)
        dockArea.addDock(plotDocks[1], 'right', plotDocks[0])
        dockArea.addDock(plotDocks[2], 'top', displayDock)
        dockArea.addDock(plotDocks[3], 'right', plotDocks[2])

        # Window size
        self.win.resize(800, 600)

        # Flowchart
        self.fc = Flowchart(
            terminals={
                'dipImgIn': {'io': 'in'},
                'CalibConstOut': {'io': 'out'},
            }
        )
        # row, column, rowspan, colspan
        fcWidgetDock.addWidget(self.fc.widget())

        # Plot widgets
        self.plt_widg = [FlowchartPlotWidget() for _ in range(len(plotDocks))]
        [plotDocks[i].addWidget(
            self.plt_widg[i]) for i in range(len(plotDocks))]

        # Graphics layout for displays
        displayLayout = pg.GraphicsLayoutWidget(border='w')
        displayDock.addWidget(displayLayout)

        # Display widgets
        self.disp_widg = []
        self.disp_widg.append(displayLayout.addLabel(
            '', colspan=2, justify='left'))
        displayLayout.nextRow()
        self.disp_widg.append(displayLayout.addLabel(
            '', colspan=2, justify='left'))

        # Flowchart library copy - custom nodes available to user
        self.fc_library = fclib.LIBRARY.copy()
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Display')]) for nd in (
            FlowchartPlotNode, MeasurementDisplayNode, CalibDisplayNode,
            ORingMeasurementDisplayNode
        )]
        # Filter nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Filters')]) for nd in (
            GaussianConvolutionNode, GradientNode, GradientMagnitudeNode,
            GradientDirectionNode, EdgeObjectsRemoveNode, KuwaharaNode,
            BilateralFilterNode
        )]
        # Binary Filter nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Binary')]) for nd in (
            BinaryClosingNode, BinaryOpeningNode, BinaryErosionNode,
            BinaryDilationNode, BinaryAreaClosingNode, BinaryAreaOpeningNode,
            BinaryPropagationNode, FillHolesNode
        )]
        # Segmentation nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Segmentation')]) for nd in (
            ThresholdNode, RangeThresholdNode, MinimaNode, MaximaNode,
            WatershedNode, SeededWatershedNode, CannyNode, SegmentORingNode
        )]
        # Morphological nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Morphological')]) for nd in (
            DilationNode, ErosionNode, OpeningNode, ClosingNode)]
        # Image nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Image')]) for nd in (
            ConvertNode, FillNode, LabelNode, SetPixelSizeNode
        )]
        # Arithmetics nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Arithmetics')]) for nd in (
            InvertNode, ApplyMaskNode, CreateMaskNode, OperatorPlusNode
        )]
        # Measurement nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Measurement')]) for nd in (
            MeasureNode, WorkingDistanceCorrectionNode, CombineMeasurementNode
        )]
        self.fc.setLibrary(self.fc_library)

        # Plot nodes and Widget connection
        plt_nodes_x = (-20+x*120 for x in range(len(self.plt_widg)))
        plt_nodes = [self.fc.createNode(
            'FlowchartPlot', pos=(x, -60)) for x in plt_nodes_x]
        [nd.set_fcPlotWidget(
            widg) for nd, widg in zip(plt_nodes, self.plt_widg)]

        # Connecting plot and display widgets with nodes
        self.fc.sigFileLoaded.connect(self.setFlowchartPlotWidgets)
        self.fc.sigFileLoaded.connect(self.setDisplayWidgets)
        self.fc.sigChartChanged.connect(self.setFlowchartPlotWidgets)
        self.fc.sigChartChanged.connect(self.setDisplayWidgets)

    def setFlowchartPlotWidgets(self):
        """
        Connect Flowchart plot widgets with nodes after loading fc file
        """
        nd_list = []
        for name, node in self.fc.nodes().items():
            if isinstance(node, FlowchartPlotNode):
                nd_list.append(node)
        [nd.set_fcPlotWidget(widg) for nd, widg in zip(nd_list, self.plt_widg)]

    def setDisplayWidgets(self):
        """
        Connect Display widgets with nodes
        """
        for name, node in self.fc.nodes().items():
            if isinstance(node, MeasurementDisplayNode):
                node.setDisplayWidget(self.disp_widg[0])
            if isinstance(node, CalibDisplayNode):
                node.setDisplayWidget(self.disp_widg[1])

    def setInput(self, dip_img):
        """
        Set Flowchart input
        """
        self.fc.setInput(dipImgIn=dip_img)

    def fc_process(self, dip_img):
        """
        Process data with display=False (speed increase)
        """
        return self.fc.process(dipImgIn=dip_img)['CalibConstOut']

    def output(self):
        """
        Process data through flowchart with display=True and return output
        """
        return self.fc.output()['CalibConstOut']

    def show(self):
        self.win.show()

    def close(self):
        self.win.hide()


class FlowchartMeasureWindow:
    def __init__(self):
        """
        Flowchart inside new window for measuring objects
        """
        # Initial mm/px ratio
        self.mmPxRatio = 1
        # Graphics window
        self.win = QtGui.QMainWindow()
        self.win.setWindowTitle('Object Measurement Flowchart')
        # Dock Area
        dockArea = DockArea()
        # Central widget
        self.win.setCentralWidget(dockArea)

        # Window Docks
        fcWidgetDock = Dock(
            'Flowchart Widget', size=(1, 1), hideTitle=True)
        displayDock = Dock('Measurement and Calibration', size=(1, 1))
        plotDocks = [
            Dock('Plot {}'.format(i), size=(1, 1)) for i in range(4)
        ]
        dockArea.addDock(fcWidgetDock, 'left')
        dockArea.addDock(displayDock, 'right', fcWidgetDock)
        dockArea.addDock(plotDocks[0], 'top', displayDock)
        dockArea.addDock(plotDocks[1], 'right', plotDocks[0])
        dockArea.addDock(plotDocks[2], 'top', displayDock)
        dockArea.addDock(plotDocks[3], 'right', plotDocks[2])

        # Window size
        self.win.resize(800, 600)

        # Flowchart
        self.fc = Flowchart(
            terminals={
                'dipImgIn': {'io': 'in'},
                'mmPxRatio': {'io': 'in'},
                'dipMeasurementOut': {'io': 'out'},
            }
        )
        # row, column, rowspan, colspan
        fcWidgetDock.addWidget(self.fc.widget())

        # Plot widgets
        self.plt_widg = [FlowchartPlotWidget() for _ in range(len(plotDocks))]
        [plotDocks[i].addWidget(
            self.plt_widg[i]) for i in range(len(plotDocks))]

        # Graphics layout for displays
        displayLayout = pg.GraphicsLayoutWidget(border='w')
        displayDock.addWidget(displayLayout)

        # Display widgets
        self.disp_widg = []
        self.disp_widg.append(displayLayout.addLabel(
            '', colspan=2, justify='left'))
        displayLayout.nextRow()
        self.disp_widg.append(displayLayout.addLabel(
            '', colspan=2, justify='left'))

        # Flowchart library copy - custom nodes available to user
        self.fc_library = fclib.LIBRARY.copy()
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Display')]) for nd in (
            FlowchartPlotNode, MeasurementDisplayNode, CalibDisplayNode,
            ORingMeasurementDisplayNode
        )]
        # Filter nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Filters')]) for nd in (
            GaussianConvolutionNode, GradientNode, GradientMagnitudeNode,
            GradientDirectionNode, EdgeObjectsRemoveNode, KuwaharaNode,
            BilateralFilterNode
        )]
        # Binary Filter nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Binary')]) for nd in (
            BinaryClosingNode, BinaryOpeningNode, BinaryErosionNode,
            BinaryDilationNode, BinaryAreaClosingNode, BinaryAreaOpeningNode,
            BinaryPropagationNode, FillHolesNode
        )]
        # Segmentation nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Segmentation')]) for nd in (
            ThresholdNode, RangeThresholdNode, MinimaNode, MaximaNode,
            WatershedNode, SeededWatershedNode, CannyNode, SegmentORingNode
        )]
        # Morphological nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Morphological')]) for nd in (
            DilationNode, ErosionNode, OpeningNode, ClosingNode)]
        # Image nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Image')]) for nd in (
            ConvertNode, FillNode, LabelNode, SetPixelSizeNode
        )]
        # Arithmetics nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Arithmetics')]) for nd in (
            InvertNode, ApplyMaskNode, CreateMaskNode, OperatorPlusNode
        )]
        # Measurement nodes
        [self.fc_library.addNodeType(
            nd, [('dipImage', 'Measurement')]) for nd in (
            MeasureNode, WorkingDistanceCorrectionNode, CombineMeasurementNode
        )]
        self.fc.setLibrary(self.fc_library)

        # Plot nodes and Widget connection
        plt_nodes_x = (-20+x*120 for x in range(len(self.plt_widg)))
        plt_nodes = [self.fc.createNode(
            'FlowchartPlot', pos=(x, -60)) for x in plt_nodes_x]
        [nd.set_fcPlotWidget(
            widg) for nd, widg in zip(plt_nodes, self.plt_widg)]

        # Connecting plot and display widgets with nodes
        self.fc.sigFileLoaded.connect(self.setFlowchartPlotWidgets)
        self.fc.sigFileLoaded.connect(self.setDisplayWidgets)
        self.fc.sigChartChanged.connect(self.setFlowchartPlotWidgets)
        self.fc.sigChartChanged.connect(self.setDisplayWidgets)

    def __getstate__(self):
        """
        When pickling retain only Flowchart related attributes
        Flowchart objects can't be pickled

        :return: self.__dict__
        """
        state = self.__dict__.copy()
        flowchart_state = {
            key:value for key, value in state.items() if
            key in ['fc', 'fc_process', 'mmPxRatio']
        }
        return flowchart_state

    def setFlowchartPlotWidgets(self):
        """
        Connect Flowchart plot widgets with nodes after loading fc file
        """
        nd_list = []
        for name, node in self.fc.nodes().items():
            if isinstance(node, FlowchartPlotNode):
                nd_list.append(node)
        [nd.set_fcPlotWidget(widg) for nd, widg in zip(nd_list, self.plt_widg)]

    def setDisplayWidgets(self):
        """
        Connect Display widgets with nodes
        """
        for name, node in self.fc.nodes().items():
            if isinstance(node, ORingMeasurementDisplayNode):
                node.setDisplayWidgetList(self.disp_widg)

    def setInput(self, dip_img, mmPxRatio):
        """
        Set Flowchart input
        """
        self.mmPxRatio = mmPxRatio
        self.fc.setInput(dipImgIn=dip_img, mmPxRatio=mmPxRatio)

    def fc_process(self, dip_img):
        """
        Process data with display=False (speed increase) and return output
        """
        return self.fc.process(
            dipImgIn=dip_img, mmPxRatio=self.mmPxRatio)['dipMeasurementOut']

    def output(self):
        """
        Process data through flowchart with display=True
        """
        return self.fc.output()['dipMeasurementOut']

    def show(self):
        self.win.show()

    def close(self):
        self.win.hide()

