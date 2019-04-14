import pyqtgraph as pg
from pyqtgraph.flowchart import Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtCore, QtGui

# Numpy
import numpy as np

# PyDIP
import PyDIP as dip

# Operators
import operator


class FlowchartPlotNode(Node):
    """
    Node for displaying dip.Image in FlowchartPlotWidget
    """
    nodeName = 'FlowchartPlot'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in', 'optional': True}
        })
        self.fc_plot_widget = None

    def set_fcPlotWidget(self, fc_plot_widget):
        self.fc_plot_widget = fc_plot_widget

    def process(self, dipImgIn=None, display=True):
        """
        Node process function. If display=False, skip displaying img
        """
        if display and self.fc_plot_widget is not None:
            if dipImgIn is None:
                # Empty image
                self.fc_plot_widget.setImage(np.zeros((1, 1)))
            else:
                self.fc_plot_widget.setImage(dipImgIn)
                # Plot title from connected node
                title = ' '.join([n.name() for n in self.dependentNodes()])
                self.fc_plot_widget.setTitle(title)


class GaussianConvolutionNode(CtrlNode):
    """
    Node with control widget for convolution with Gaussian kernel
    """
    nodeName = 'GaussianConvolution'
    uiTemplate = [
        ('sigmas', 'spin', {'value': 1.0, 'step': 0.1, 'bounds': [0., 10.]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'smoothOut': {'io': 'out'}
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        sigmas = self.ctrls['sigmas'].value()
        return {'smoothOut': dip.Gauss(dipImgIn, [sigmas])}


class ThresholdNode(CtrlNode):
    """
    Node with control widget for thresholding with different methods
    """
    nodeName = 'Threshold'
    uiTemplate = [
        ('method', 'combo', {'values': [
            'background', 'volume', 'fixed', 'isodata', 'otsu', 'minerror',
            'triangle',
        ]}),
        ('parameter', 'spin', {
            'value': 8.0, 'step': 0.1, 'bounds': [0., 255.]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'thrImgOut': {'io': 'out'},
            'thrValOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        method = self.stateGroup.state()['method']
        parameter = self.ctrls['parameter'].value()
        thr = dip.Threshold(dipImgIn, method=method, parameter=parameter)
        return {'thrImgOut': thr[0], 'thrValOut': thr[1]}


class RangeThresholdNode(CtrlNode):
    """
    Node with control widget for range thresholding
    """
    nodeName = 'RangeThreshold'
    uiTemplate = [
        ('lowerBound', 'spin', {
            'value': 30, 'step': 1, 'bounds': [0, 255]
        }),
        ('upperBound', 'spin', {
            'value': 100, 'step': 1, 'bounds': [0, 255]
        }),
        ('foreground', 'spin', {
            'value': 1, 'step': 1, 'bounds': [0, 1]
        }),
        ('background', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, 1]
        }),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        lowerBound = self.ctrls['lowerBound'].value()
        upperBound = self.ctrls['upperBound'].value()
        foreground = self.ctrls['foreground'].value()
        background = self.ctrls['background'].value()
        thr = dip.RangeThreshold(
            dipImgIn, lowerBound=lowerBound, upperBound=upperBound,
            foreground=foreground, background=background
        )
        return {'dipImgOut': thr}


class OpeningNode(CtrlNode):
    """
    Node with control widget for opening with different shape and size
    """
    nodeName = 'Opening'
    uiTemplate = [
        ('shape', 'combo', {'values': [
            'elliptic', 'diamond', 'rectangular', 'octagonal', 'parabolic'
        ]}),
        ('size', 'spin', {
            'value': 11, 'step': 2, 'bounds': [1, 99]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        shape = self.stateGroup.state()['shape']
        size = self.ctrls['size'].value()
        struct_element = dip.SE(size, shape)
        img = dip.Opening(dipImgIn, se=struct_element)
        return {'dipImgOut': img}


class ClosingNode(CtrlNode):
    """
    Node with control widget for Closing with different shape and size
    """
    nodeName = 'Closing'
    uiTemplate = [
        ('shape', 'combo', {'values': [
            'elliptic', 'diamond', 'rectangular', 'octagonal', 'parabolic'
        ]}),
        ('size', 'spin', {
            'value': 11, 'step': 2, 'bounds': [1, 99]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        shape = self.stateGroup.state()['shape']
        size = self.ctrls['size'].value()
        struct_element = dip.SE(size, shape)
        img = dip.Closing(dipImgIn, se=struct_element)
        return {'dipImgOut': img}


class DilationNode(CtrlNode):
    """
    Node with control widget for Dilation with different shape and size
    """
    nodeName = 'Dilation'
    uiTemplate = [
        ('shape', 'combo', {'values': [
            'elliptic', 'diamond', 'rectangular', 'octagonal', 'parabolic'
        ]}),
        ('size', 'spin', {
            'value': 11, 'step': 2, 'bounds': [1, 99]
        }),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        shape = self.stateGroup.state()['shape']
        size = self.ctrls['size'].value()
        struct_element = dip.SE(size, shape)
        img = dip.Dilation(dipImgIn, se=struct_element)
        return {'dipImgOut': img}


class ErosionNode(CtrlNode):
    """
    Node with control widget for Erosion with different shape and size
    """
    nodeName = 'Erosion'
    uiTemplate = [
        ('shape', 'combo', {'values': [
            'elliptic', 'diamond', 'rectangular', 'octagonal', 'parabolic'
        ]}),
        ('size', 'spin', {
            'value': 11, 'step': 2, 'bounds': [1, 99]
        }),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        shape = self.stateGroup.state()['shape']
        size = self.ctrls['size'].value()
        struct_element = dip.SE(size, shape)
        img = dip.Erosion(dipImgIn, se=struct_element)
        return {'dipImgOut': img}


class EdgeObjectsRemoveNode(CtrlNode):
    """
    Node with control widget for removing edge objects from binary image with
    different connectivity
    """
    nodeName = 'EdgeObjectsRemove'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        img = dip.EdgeObjectsRemove(dipImgIn, connectivity=connectivity)
        return {'dipImgOut': img}


class ConvertNode(CtrlNode):
    """
    Node with control widget for converting image data type
    """
    nodeName = 'Convert'
    uiTemplate = [
        ('DataType', 'combo', {'values': [
            'BIN', 'UINT8', 'UINT16', 'UINT32', 'SINT8', 'SINT16', 'SINT32',
            'SFLOAT', 'DFLOAT', 'SCOMPLEX', 'DCOMPLEX'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        dtype = self.stateGroup.state()['DataType']
        img = dip.Convert(dipImgIn, dtype)
        return {'dipImgOut': img}


class InvertNode(Node):
    """
    Node for inverting pixel intensities
    """
    nodeName = 'Invert'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        img = dip.Invert(dipImgIn)
        return {'dipImgOut': img}


class CannyNode(CtrlNode):
    """
    Node with control widget for Canny edge detector
    """
    nodeName = 'Canny'
    uiTemplate = [
        ('sigmas', 'spin', {'value': 1.0, 'step': 0.1, 'bounds': [0., 10.]}),
        ('lower', 'spin', {'value': 0.5, 'step': 0.01, 'bounds': [0., 1.]}),
        ('upper', 'spin', {'value': 0.9, 'step': 0.01, 'bounds': [0., 1.]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        sigmas = [self.ctrls['sigmas'].value()]
        lower = self.ctrls['lower'].value()
        upper = self.ctrls['upper'].value()
        img = dip.Canny(dipImgIn, sigmas, lower, upper)
        return {'dipImgOut': img}


class GradientNode(CtrlNode):
    """
    Node with control widget for calculating image Gradient
    """
    nodeName = 'Gradient'
    uiTemplate = [
        ('sigmas', 'spin', {'value': 1.0, 'step': 0.1, 'bounds': [0., 10.]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        sigmas = [self.ctrls['sigmas'].value()]
        img = dip.Gradient(dipImgIn, sigmas)
        return {'dipImgOut': img}


class GradientMagnitudeNode(CtrlNode):
    """
    Node with control widget for computing Gradient Magnitude
    """
    nodeName = 'GradientMagnitude'
    uiTemplate = [
        ('sigmas', 'spin', {'value': 1.0, 'step': 0.1, 'bounds': [0., 10.]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        sigmas = [self.ctrls['sigmas'].value()]
        img = dip.GradientMagnitude(dipImgIn, sigmas)
        return {'dipImgOut': img}


class GradientDirectionNode(CtrlNode):
    """
    Node with control widget for computing Gradient Direction
    """
    nodeName = 'GradientDirection'
    uiTemplate = [
        ('sigmas', 'spin', {'value': 1.0, 'step': 0.1, 'bounds': [0., 10.]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        sigmas = [self.ctrls['sigmas'].value()]
        img = dip.GradientDirection(dipImgIn, sigmas)
        return {'dipImgOut': img}


class WatershedNode(CtrlNode):
    """
    Node with control widget for Watershed
    """
    nodeName = 'Watershed'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('maxDepth', 'spin', {
            'value': 1., 'step': 0.01, 'bounds': [0., 255.]
        }),
        ('maxSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('outType', 'combo', {'values': [
            'binary', 'labels'
        ]}),
        ('sortOrder', 'combo', {'values': [
            'low first', 'high first'
        ]}),
        ('algorithm', 'combo', {'values': [
            'correct', 'fast'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipMaskIn': {'io': 'in', 'optional': True},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, dipMaskIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        maxDepth = self.ctrls['maxDepth'].value()
        maxSize = int(self.ctrls['maxSize'].value())
        flags = {
            self.stateGroup.state()['outType'],
            self.stateGroup.state()['sortOrder'],
            self.stateGroup.state()['algorithm']
        }
        if dipMaskIn is None:
            img = dip.Watershed(
                dipImgIn, connectivity=connectivity,
                maxDepth=maxDepth, maxSize=maxSize, flags=flags
            )
        else:
            img = dip.Watershed(
                dipImgIn, mask=dipMaskIn, connectivity=connectivity,
                maxDepth=maxDepth, maxSize=maxSize, flags=flags
            )
        return {'dipImgOut': img}


class SeededWatershedNode(CtrlNode):
    """
    Node with control widget for Watershed starting at seeds
    """
    nodeName = 'SeededWatershed'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('maxDepth', 'spin', {
            'value': 1., 'step': 0.01, 'bounds': [0., 255.]
        }),
        ('maxSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('outType', 'combo', {'values': [
            'labels', 'binary'
        ]}),
        ('sortOrder', 'combo', {'values': [
            'low first', 'high first'
        ]}),
        ('no gaps', 'check', {'value': False}),
        ('uphill only', 'check', {'value': False}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipSeedsIn': {'io': 'in'},
            'dipMaskIn': {'io': 'in', 'optional': True},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, dipSeedsIn, dipMaskIn=None, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        maxDepth = self.ctrls['maxDepth'].value()
        maxSize = int(self.ctrls['maxSize'].value())
        flags = {
            self.stateGroup.state()['outType'],
            self.stateGroup.state()['sortOrder'],
        }
        if self.ctrls['no gaps'].isChecked():
            flags.add('no gaps')
        if self.ctrls['uphill only'].isChecked():
            flags.add('uphill only')
        if dipMaskIn is None:
            img = dip.SeededWatershed(
                dipImgIn, seeds=dipSeedsIn, connectivity=connectivity,
                maxDepth=maxDepth, maxSize=maxSize, flags=flags
            )
        else:
            img = dip.SeededWatershed(
                dipImgIn, seeds=dipSeedsIn, mask=dipMaskIn,
                connectivity=connectivity, maxDepth=maxDepth, maxSize=maxSize,
                flags=flags
            )
        return {'dipImgOut': img}


class MinimaNode(CtrlNode):
    """
    Node with control widget for local minima
    """
    nodeName = 'Minima'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('outType', 'combo', {'values': [
            'binary', 'labels'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        output = self.stateGroup.state()['outType']
        img = dip.Minima(dipImgIn, connectivity=connectivity, output=output)
        return {'dipImgOut': img}


class MaximaNode(CtrlNode):
    """
    Node with control widget for local minima
    """
    nodeName = 'Maxima'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('outType', 'combo', {'values': [
            'binary', 'labels'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        output = self.stateGroup.state()['outType']
        img = dip.Minima(dipImgIn, connectivity=connectivity, output=output)
        return {'dipImgOut': img}


class CreateMaskNode(CtrlNode):
    """
    Node with control widget for creating mask
    """
    nodeName = 'CreateMask'
    uiTemplate = [
        ('relation', 'combo', {'values': [
            '<=', '>=', '<', '>', '==', '!='
        ]}),
        ('intensity', 'spin', {
            'value': 1, 'step': 1, 'bounds': [0, 255]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })
        self.op = {
            '<=': operator.le, '>=': operator.ge, '<': operator.lt,
            '>': operator.gt, '==': operator.eq, '!=': operator.ne
        }

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        rel = self.stateGroup.state()['relation']
        intensity = self.ctrls['intensity'].value()
        img = self.op[rel](dipImgIn, intensity)
        return {'dipImgOut': img}


class ApplyMaskNode(Node):
    """
    Node for applying mask
    """
    nodeName = 'ApplyMask'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipMaskIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, dipMaskIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        img = dipImgIn * dipMaskIn
        return {'dipImgOut': img}


class FillNode(CtrlNode):
    """
    Node for filling pixels under mask (optional) with intensity
    """
    nodeName = 'Fill'
    uiTemplate = [
        ('intensity', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, 255]})
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipMaskIn': {'io': 'in', 'optional': True},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, dipMaskIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        intensity = self.ctrls['intensity'].value()
        if dipMaskIn is None:
            img = dipImgIn.Copy().Fill(intensity)
        else:
            img = dipImgIn.Copy()
            img[dipMaskIn] = intensity
        return {'dipImgOut': img}


class BinaryPropagationNode(CtrlNode):
    """
    Node with control widget for BinaryPropagation
    """
    nodeName = 'BinaryPropagation'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('iterations', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipMaskIn': {'io': 'in', 'optional': True},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, dipMaskIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        iterations = int(self.ctrls['iterations'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        if dipMaskIn is None:
            img = dip.BinaryPropagation(
                dipImgIn, connectivity=connectivity,
                iterations=iterations, edgeCondition=edgeCondition
            )
        else:
            img = dip.BinaryPropagation(
                dipImgIn, dipMaskIn, connectivity=connectivity,
                iterations=iterations, edgeCondition=edgeCondition
            )
        return {'dipImgOut': img}


class FillHolesNode(CtrlNode):
    """
    Node with control widget for FillHoles
    """
    nodeName = 'FillHoles'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        img = dip.FillHoles(dipImgIn, connectivity=connectivity)
        return {'dipImgOut': img}


class LabelNode(CtrlNode):
    """
    Node with control widget for Labeling connected regions in binary image
    """
    nodeName = 'Label'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('minSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('maxSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        minSize = int(self.ctrls['minSize'].value())
        maxSize = int(self.ctrls['maxSize'].value())
        img = dip.Label(
            dipImgIn, connectivity=connectivity,
            minSize=minSize, maxSize=maxSize
        )
        return {'dipImgOut': img}


class MeasureNode(CtrlNode):
    """
    Node with control widget for Measuring one or more features
    """
    nodeName = 'Measure'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('Perimeter', 'check', {'value': False}),
        ('Feret', 'check', {'value': True}),
        ('CartesianBox', 'check', {'value': False}),
        ('Minimum', 'check', {'value': False}),
        ('Maximum', 'check', {'value': False}),
        ('SolidArea', 'check', {'value': False}),
        ('ConvexArea', 'check', {'value': False}),
        ('ConvexPerimeter', 'check', {'value': False}),
        ('AspectRatioFeret', 'check', {'value': False}),
        ('Radius', 'check', {'value': False}),
        ('P2A', 'check', {'value': False}),
        ('Roundness', 'check', {'value': False}),
        ('Circularity', 'check', {'value': False}),
        ('PodczeckShapes', 'check', {'value': False}),
        ('Solidity', 'check', {'value': False}),
        ('Convexity', 'check', {'value': False}),
        ('EllipseVariance', 'check', {'value': False}),
        ('Eccentricity', 'check', {'value': False}),
        ('Center', 'check', {'value': False}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipLblIn': {'io': 'in'},
            'dipGreyIn': {'io': 'in'},
            'dipMsrOut': {'io': 'out'},
        })

    def process(self, dipLblIn, dipGreyIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        features = []
        for name, val in self.ctrls.items():
            if name != 'connectivity' and val.isChecked():
                features.append(name)
        msr = dip.MeasurementTool.Measure(
            dipLblIn, grey=dipGreyIn, features=features,
            connectivity=connectivity
        )
        return {'dipMsrOut': msr}


class MeasurementDisplayNode(Node):
    """
    Node for displaying dip.Measurement in FlowchartPlotWidget
    """
    nodeName = 'MeasurementDisplay'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipMsrIn': {'io': 'in'}
        })
        self.fc_display_widget = None

    def setDisplayWidget(self, display_widget):
        self.fc_display_widget = display_widget

    def process(self, dipMsrIn, display=True):
        """
        Node process function. If display=False, skip displaying text
        """
        if display and self.fc_display_widget is not None:
            if dipMsrIn is None:
                # Empty text
                self.fc_display_widget.setText('')
            else:
                # Measurement result as string
                disp_text = str(dipMsrIn).replace("\n", "<br>")
                disp_text = disp_text.replace(" ", "&nbsp;")
                disp_text = ''.join((
                    '<tt style=\"font-size:8pt\">', disp_text, '</tt>'))
                self.fc_display_widget.setText(disp_text)


class WorkingDistanceCorrectionNode(CtrlNode):
    """
    Node with control widget for correcting object distance from lens using
    thin lens equation
    """
    nodeName = 'WorkingDistanceCorrection'
    uiTemplate = [
        ('feature', 'combo', {'values': [
            'Feret Min', 'Feret Max'
        ]}),
        ('standard 1 height', 'spin', {
            'value': 0, 'step': 0.001, 'bounds': [0, None], 'suffix': 'mm',
            'siPrefix': True
        }),
        ('standard 1 measure', 'spin', {
            'value': 0, 'step': 0.001, 'bounds': [0, None], 'suffix': 'mm',
            'siPrefix': True
        }),
        ('standard 2 height', 'spin', {
            'value': 0, 'step': 0.001, 'bounds': [0, None], 'suffix': 'mm',
            'siPrefix': True
        }),
        ('standard 2 measure', 'spin', {
            'value': 0, 'step': 0.001, 'bounds': [0, None], 'suffix': 'mm',
            'siPrefix': True
        }),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipMsrIn': {'io': 'in'},
            'CalibConstOut': {'io': 'out'},
        })

    def process(self, dipMsrIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['feature'] == 'Feret Min':
            # Measured image size
            img_size_1, img_size_2 = (dipMsrIn['Feret'][1][1],
                                      dipMsrIn['Feret'][2][1])
        else:
            # Measured image size
            img_size_1, img_size_2 = (dipMsrIn['Feret'][1][0],
                                      dipMsrIn['Feret'][2][0])
        # print("Image sizes: {} - {}".format(img_size_1, img_size_2))
        # Standard height difference
        height_1 = self.ctrls['standard 1 height'].value()
        height_2 = self.ctrls['standard 2 height'].value()
        height_diff_12 = height_1 - height_2
        # print("Height difference: {}".format(height_diff_12))
        obj_size_1 = self.ctrls['standard 1 measure'].value()
        obj_size_2 = self.ctrls['standard 2 measure'].value()
        # print("Object sizes: {} - {}".format(obj_size_1, obj_size_2))
        # mm/px ratio
        mm_px_1 = obj_size_1 / img_size_1
        mm_px_2 = obj_size_2 / img_size_2
        # print("mm/px ratios: {} - {}".format(mm_px_1, mm_px_2))
        # Working distance
        work_dist_1 = height_diff_12 / (mm_px_2 / mm_px_1 - 1.)
        # print("Working distance 1: {}".format(work_dist_1))
        return {'CalibConstOut': {'std_height': height_1,
                                  'std_work_dist': work_dist_1,
                                  'std_mm_px': mm_px_1}}


class CalibDisplayNode(Node):
    """
    Node for displaying Calibration equation in FlowchartPlotWidget
    """
    nodeName = 'CalibDisplay'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'CalibConstIn': {'io': 'in'}
        })
        self.fc_display_widget = None

    def setDisplayWidget(self, display_widget):
        self.fc_display_widget = display_widget

    def process(self, CalibConstIn, display=True):
        """
        Node process function. If display=False, skip displaying text
        """
        if display and self.fc_display_widget is not None:
            if CalibConstIn is None:
                # Empty text
                self.fc_display_widget.setText('')
            else:
                # Measurement result as string
                disp_text = (
                    '<sup>mm</sup>&frasl;<sub>px</sub> = (1 + '
                    '<sup>{} - object_height</sup>&frasl;<sub>{}</sub>)'
                    '&times; {}').format(
                    CalibConstIn['std_height'], CalibConstIn['std_work_dist'],
                    CalibConstIn['std_mm_px']
                )
                # print(disp_text)
                disp_text = ''.join((
                    '<tt style=\"font-size:18pt\">', disp_text, '</tt>'))
                self.fc_display_widget.setText(disp_text)


class SegmentORingNode(CtrlNode):
    """
    Node with control widget for Segmenting O-ring outer and inner diameter
    """
    nodeName = 'SegmentORing'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipOuterOut': {'io': 'out'},
            'dipInnerOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        outer = dip.FillHoles(dipImgIn, connectivity=connectivity)
        inner = dip.EdgeObjectsRemove(
            dip.Invert(dipImgIn), connectivity=connectivity)
        return {'dipOuterOut': outer,
                'dipInnerOut': inner}


class ORingMeasurementDisplayNode(Node):
    """
    Node for displaying  O-Ring dip.Measurements in Flowchart Labels
    """
    nodeName = 'ORingMeasurementDisplay'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipMsrOutIn': {'io': 'in', 'optional': True},
            'dipMsrInIn': {'io': 'in', 'optional': True}
        })
        self.fc_display_widget_list = None

    def setDisplayWidgetList(self, display_widget_list):
        """
        Set list of two labels for displaying measurement results
        """
        self.fc_display_widget_list = display_widget_list

    def process(self, dipMsrOutIn, dipMsrInIn, display=True):
        """
        Node process function. If display=False, skip displaying text
        """
        if display and self.fc_display_widget_list is not None:
            if dipMsrOutIn is None and dipMsrInIn is None:
                # Empty text
                self.fc_display_widget_list[0].setText('')
                self.fc_display_widget_list[1].setText('')
            elif dipMsrOutIn is not None and dipMsrInIn is None:
                # Measurement result as string
                outer_disp = str(dipMsrOutIn).replace("\n", "<br>")
                outer_disp = outer_disp.replace(" ", "&nbsp;")
                outer_disp = ''.join((
                    '<tt style=\"font-size:8pt\"> <b>Outer Diameter:</b><br>',
                    outer_disp, '</tt>'))
                self.fc_display_widget_list[0].setText(outer_disp)
                # Empty text
                self.fc_display_widget_list[1].setText('')
            elif dipMsrOutIn is None and dipMsrInIn is not None:
                # Measurement result as string
                inner_disp = str(dipMsrInIn).replace("\n", "<br>")
                inner_disp = inner_disp.replace(" ", "&nbsp;")
                inner_disp = ''.join((
                    '<tt style=\"font-size:8pt\"> <b>Inner Diameter:</b><br>',
                    inner_disp, '</tt>'))
                # Empty text
                self.fc_display_widget_list[0].setText('')
                self.fc_display_widget_list[1].setText(inner_disp)
            else:
                # Measurement result as string
                outer_disp = str(dipMsrOutIn).replace("\n", "<br>")
                outer_disp = outer_disp.replace(" ", "&nbsp;")
                outer_disp = ''.join((
                    '<tt style=\"font-size:8pt\"> <b>Outer Diameter:</b><br>',
                    outer_disp, '</tt>'))
                inner_disp = str(dipMsrInIn).replace("\n", "<br>")
                inner_disp = inner_disp.replace(" ", "&nbsp;")
                inner_disp = ''.join((
                    '<tt style=\"font-size:8pt\"> <b>Inner Diameter:</b><br>',
                    inner_disp, '</tt>'))
                self.fc_display_widget_list[0].setText(outer_disp)
                self.fc_display_widget_list[1].setText(inner_disp)


class SetPixelSizeNode(CtrlNode):
    """
    Node with control widget for assigning physical quantity to pixels
    """
    nodeName = 'SetPixelSize'
    uiTemplate = [
        ('units', 'combo', {'values': [
            'mm', 'um'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'mmPxRatioIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, mmPxRatioIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        units = self.stateGroup.state()['units']
        img = dipImgIn.Copy()
        img.SetPixelSize(
            dip.PixelSize(dip.PhysicalQuantity(mmPxRatioIn, units)))
        return {'dipImgOut': img}


class KuwaharaNode(CtrlNode):
    """
    Node with control widget for Kuwahara-Nagao non-linear, edge-preserving
    smoothing filter
    """
    nodeName = 'Kuwahara'
    uiTemplate = [
        ('shape', 'combo', {'values': [
            'elliptic', 'rectangular', 'diamond', 'line'
        ]}),
        ('size', 'spin', {
            'value': 11, 'step': 2, 'bounds': [1, 99]}),
        ('threshold', 'spin', {
            'value': 0., 'step': 0.01, 'bounds': [0, None]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        shape = self.stateGroup.state()['shape']
        size = self.ctrls['size'].value()
        threshold = self.ctrls['threshold'].value()
        kernel = dip.Kernel(size, shape)
        img = dip.Kuwahara(dipImgIn, kernel=kernel, threshold=threshold)
        return {'dipImgOut': img}


class BilateralFilterNode(CtrlNode):
    """
    Node with control widget for Bilateral filtering (non-linear,
    edge-preserving smoothing)
    """
    nodeName = 'BilateralFilter'
    uiTemplate = [
        ('method', 'combo', {'values': [
            'xysep', 'full', 'pwlinear'
        ]}),
        ('spatialSigmas', 'spin', {
            'value': 2., 'step': 0.01, 'bounds': [0, None]}),
        ('tonalSigma', 'spin', {
            'value': 30., 'step': 0.1, 'bounds': [0, None]}),
        ('truncation', 'spin', {
            'value': 2., 'step': 0.01, 'bounds': [0, None]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        method = self.stateGroup.state()['method']
        spatialSigmas = [self.ctrls['spatialSigmas'].value()]
        tonalSigma = self.ctrls['tonalSigma'].value()
        truncation = self.ctrls['truncation'].value()
        img = dip.BilateralFilter(
            dipImgIn, method=method, spatialSigmas=spatialSigmas,
            tonalSigma=tonalSigma, truncation=truncation,
        )
        return {'dipImgOut': img}


class BinaryAreaClosingNode(CtrlNode):
    """
    Node with control widget for BinaryAreaClosing of areas smaller than
    filterSize
    """
    nodeName = 'BinaryAreaClosing'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('filterSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        filterSize = int(self.ctrls['filterSize'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryAreaClosing(
            dipImgIn, connectivity=connectivity,
            filterSize=filterSize, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class BinaryAreaOpeningNode(CtrlNode):
    """
    Node with control widget for BinaryAreaOpening of areas smaller than
    filterSize
    """
    nodeName = 'BinaryAreaOpening'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '8-Connectivity', '4-Connectivity'
        ]}),
        ('filterSize', 'spin', {
            'value': 0, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        else:
            connectivity = 1
        filterSize = int(self.ctrls['filterSize'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryAreaOpening(
            dipImgIn, connectivity=connectivity,
            filterSize=filterSize, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class BinaryClosingNode(CtrlNode):
    """
    Node with control widget for BinaryClosing with iterations
    """
    nodeName = 'BinaryClosing'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '4-8 Connectivity', '8-4 Connectivity', '8-Connectivity',
            '4-Connectivity',
        ]}),
        ('iterations', 'spin', {
            'value': 3, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'special', 'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        elif self.stateGroup.state()['connectivity'] == '4-Connectivity':
            connectivity = 1
        elif self.stateGroup.state()['connectivity'] == '4-8 Connectivity':
            connectivity = -1
        elif self.stateGroup.state()['connectivity'] == '8-4 Connectivity':
            connectivity = -2
        iterations = int(self.ctrls['iterations'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryClosing(
            dipImgIn, connectivity=connectivity,
            iterations=iterations, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class BinaryOpeningNode(CtrlNode):
    """
    Node with control widget for BinaryOpening with iterations
    """
    nodeName = 'BinaryOpening'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '4-8 Connectivity', '8-4 Connectivity', '8-Connectivity',
            '4-Connectivity',
        ]}),
        ('iterations', 'spin', {
            'value': 3, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'special', 'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        elif self.stateGroup.state()['connectivity'] == '4-Connectivity':
            connectivity = 1
        elif self.stateGroup.state()['connectivity'] == '4-8 Connectivity':
            connectivity = -1
        elif self.stateGroup.state()['connectivity'] == '8-4 Connectivity':
            connectivity = -2
        iterations = int(self.ctrls['iterations'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryOpening(
            dipImgIn, connectivity=connectivity,
            iterations=iterations, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class BinaryDilationNode(CtrlNode):
    """
    Node with control widget for BinaryDilation with iterations
    """
    nodeName = 'BinaryDilation'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '4-8 Connectivity', '8-4 Connectivity', '8-Connectivity',
            '4-Connectivity',
        ]}),
        ('iterations', 'spin', {
            'value': 3, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'background', 'object'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        elif self.stateGroup.state()['connectivity'] == '4-Connectivity':
            connectivity = 1
        elif self.stateGroup.state()['connectivity'] == '4-8 Connectivity':
            connectivity = -1
        elif self.stateGroup.state()['connectivity'] == '8-4 Connectivity':
            connectivity = -2
        iterations = int(self.ctrls['iterations'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryDilation(
            dipImgIn, connectivity=connectivity,
            iterations=iterations, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class BinaryErosionNode(CtrlNode):
    """
    Node with control widget for BinaryErosion with iterations
    """
    nodeName = 'BinaryErosion'
    uiTemplate = [
        ('connectivity', 'combo', {'values': [
            '4-8 Connectivity', '8-4 Connectivity', '8-Connectivity',
            '4-Connectivity',
        ]}),
        ('iterations', 'spin', {
            'value': 3, 'step': 1, 'bounds': [0, None]
        }),
        ('edgeCondition', 'combo', {'values': [
            'object', 'background'
        ]}),
    ]

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgIn': {'io': 'in'},
            'dipImgOut': {'io': 'out'},
        })

    def process(self, dipImgIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        if self.stateGroup.state()['connectivity'] == '8-Connectivity':
            connectivity = 2
        elif self.stateGroup.state()['connectivity'] == '4-Connectivity':
            connectivity = 1
        elif self.stateGroup.state()['connectivity'] == '4-8 Connectivity':
            connectivity = -1
        elif self.stateGroup.state()['connectivity'] == '8-4 Connectivity':
            connectivity = -2
        iterations = int(self.ctrls['iterations'].value())
        edgeCondition = self.stateGroup.state()['edgeCondition']
        img = dip.BinaryErosion(
            dipImgIn, connectivity=connectivity,
            iterations=iterations, edgeCondition=edgeCondition
        )
        return {'dipImgOut': img}


class OperatorPlusNode(Node):
    """
    Node for operator plus
    """
    nodeName = 'OperatorPlus'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipImgOneIn': {'io': 'in'},
            'dipImgTwoIn': {'io': 'in'},
            'dipImgPlusOut': {'io': 'out'},
        })

    def process(self, dipImgOneIn, dipImgTwoIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        img = dipImgOneIn + dipImgTwoIn
        return {'dipImgPlusOut': img}


class CombineMeasurementNode(Node):
    """
    Node for making list of input dip.Measurement objects
    """
    nodeName = 'CombineMeasurement'

    def __init__(self, name):
        super().__init__(name=name, terminals={
            'dipMsrOutIn': {'io': 'in'},
            'dipMsrInIn': {'io': 'in'},
            'listMsrOut': {'io': 'out'},
        })

    def process(self, dipMsrOutIn, dipMsrInIn, display=True):
        """
        Node process function. If display=False, no effect
        """
        lst = [dipMsrOutIn, dipMsrInIn]
        return {'listMsrOut': lst}
