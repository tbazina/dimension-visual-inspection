# PyQtGraph
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, \
    registerParameterType


class CameraParams(pTypes.GroupParameter):
    def __init__(self, cam_obj, **opts):
        """
        Camera parameters group

        :param cam_obj: camera object

        :param opts: dictionary with options passed to GroupParameter
        """
        opts['type'] = 'group'
        # Camera object instance
        self.cam = cam_obj.cam
        # Functions for changing parameters
        self.set_width = cam_obj.set_width
        self.set_height = cam_obj.set_height
        self.set_offsetx = cam_obj.set_offsetx
        self.set_offsety = cam_obj.set_offsety
        self.set_gain = cam_obj.set_gain
        self.set_exposure_time = cam_obj.set_exposure_time
        # Amplification of camera signal manual control
        self.cam.GainAuto.SetValue("Off")
        # Exposure Time manual control
        self.cam.ExposureAuto.SetValue("Off")
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChildren([
            {
                'name': 'ROI', 'title': 'ROI Size and position',
                'type': 'group', 'children':
                [
                    # Camera Width Parameter
                    {
                        'name': 'Width', 'type': 'int',
                        'value': self.cam.Width(),
                        'default': 2592,
                        'decimals': 4,
                        'limits': (self.cam.Width.Min, self.cam.Width.Max),
                        'step': 32,
                        'suffix': 'px', 'siPrefix': False
                    },
                    # Camera Height Parameter
                    {
                        'name': 'Height', 'type': 'int',
                        'value': self.cam.Height(),
                        'default': 2048,
                        'decimals': 4,
                        'limits': (self.cam.Height.Min, self.cam.Height.Max),
                        'step': 2,
                        'suffix': 'px', 'siPrefix': False
                    },
                    # Camera OffsetX Parameter
                    {
                        'name': 'OffsetX', 'type': 'int',
                        'value': self.cam.OffsetX(),
                        'default': 0,
                        'decimals': 4,
                        'limits': (self.cam.OffsetX.Min, self.cam.OffsetX.Max),
                        'step': 32,
                        'suffix': 'px', 'siPrefix': False
                    },
                    # Camera OffsetX Parameter
                    {
                        'name': 'OffsetY', 'type': 'int',
                        'value': self.cam.OffsetY(),
                        'default': 0,
                        'decimals': 4,
                        'limits': (self.cam.OffsetY.Min, self.cam.OffsetY.Max),
                        'step': 2,
                        'suffix': 'px', 'siPrefix': False
                    },
                ]
            },
            {
                'name': 'Gain', 'type': 'float', 'value': self.cam.Gain(),
                'default': 12,
                'decimals': 5,
                'limits': (self.cam.Gain.Min, self.cam.Gain.Max),
                'step': 0.05,
                'suffix': ' dB', 'siPrefix': False
            },
            {
                'name': 'Exposure Time', 'type': 'float',
                'value': self.cam.ExposureTime()*1e-6,
                'default': 9500*1e-6,
                'decimals': 12,
                'limits': (81*1e-6, 150000*1e-6),
                'step': 100*1e-6,
                'suffix': 's', 'siPrefix': True
            },
        ])

        # Connect OnValueChanged
        self.connect_recursive(self, self.OnValueChanged)

    def connect_recursive(self, param, func):
        """
        Recursively connect func to sigValueChanged of all children of param
        """
        param.sigValueChanged.connect(func)
        if param.hasChildren():
            [self.connect_recursive(ch, func) for ch in param.children()]

    def OnValueChanged(self, param, value):
        """
        Function which handles parameter value changes
        """
        if param.name() == 'Width':
            self.child('ROI', 'OffsetX').setLimits((
                0, self.cam.Width.Max - value))
            self.set_width(value)
        if param.name() == 'Height':
            self.child('ROI', 'OffsetY').setLimits((
                0, self.cam.Height.Max - value))
            self.set_height(value)
        if param.name() == 'OffsetX':
            self.child('ROI', 'Width').setLimits((
                self.cam.Width.Min, self.cam.Width.Max - value))
            self.set_offsetx(value)
        if param.name() == 'OffsetY':
            self.child('ROI', 'Height').setLimits((
                self.cam.Height.Min, self.cam.Height.Max - value))
            self.set_offsety(value)
        if param.name() == 'Gain':
            self.set_gain(value)
        if param.name() == 'Exposure Time':
            self.set_exposure_time(value*1e6)


class CalibrationParams(pTypes.GroupParameter):
    def __init__(self, standard_dict, **opts):
        """
        Calibration parameters group

        :param standard_dict:
        dictionary with standard height, working distance and mm/px ratio

        :param opts: dictionary with options passed to GroupParameter
        """
        opts['type'] = 'group'
        super().__init__(**opts)

        self.addChildren([
            {
                'name': 'Standard', 'title': 'Standard',
                'type': 'group', 'children':
                [
                    # Standard height
                    {
                        'name': 'Height', 'type': 'float',
                        'value': standard_dict['std_height'],
                        'default': standard_dict['std_height'],
                        'limits': (0, None),
                        'step': 0.001,
                        'decimals': 6,
                        'suffix': ' mm', 'siPrefix': False
                    },
                    # Standard working distance
                    {
                        'name': 'Working Distance', 'type': 'float',
                        'value': standard_dict['std_work_dist'],
                        'default': standard_dict['std_work_dist'],
                        'limits': (0, None),
                        'step': 0.01,
                        'decimals': 6,
                        'suffix': ' mm', 'siPrefix': False
                    },
                    # Standard mm/px ration
                    {
                        'name': 'mm/px Ratio', 'type': 'float',
                        'value': standard_dict['std_mm_px'],
                        'default': standard_dict['std_mm_px'],
                        'limits': (0, None),
                        'step': 0.00001,
                        'decimals': 8,
                        'suffix': ' mm/px', 'siPrefix': False
                    },
                ]
            },
            {
                'name': 'Object', 'title': 'Measured Object',
                'type': 'group', 'children':
                [
                    # Measured object height
                    {
                        'name': 'Height', 'type': 'float',
                        'value': 2.3967111111,
                        'default': 2.3967111111,
                        'limits': (0, None),
                        'step': 0.001,
                        'decimals': 6,
                        'suffix': ' mm', 'siPrefix': False
                    },
                    # Measured object mm/px ration
                    {
                        'name': 'mm/px Ratio', 'type': 'float',
                        'value': 0,
                        'limits': (0, None),
                        'decimals': 8,
                        'suffix': ' mm/px', 'siPrefix': False,
                        'readonly': True
                    },
                ]
            },
        ])

        # Parameters to attributes
        self.std_height = self.child('Standard', 'Height')
        self.std_work_dist = self.child('Standard', 'Working Distance')
        self.std_mm_px = self.child('Standard', 'mm/px Ratio')
        self.obj_height = self.child('Object', 'Height')
        self.obj_mm_px = self.child('Object', 'mm/px Ratio')
        # Setting object mm/px ratio initial value
        self.obj_mm_px_calc()

        # Connect obj_mm_px_calc
        self.connect_recursive(self, self.obj_mm_px_calc)

    def obj_mm_px_calc(self):
        """
        Calculate mm/px ratio on object height image using thin lens equation
        and linear interpolation
        """
        self.obj_mm_px.setValue(
            (1. + (self.std_height.value() - self.obj_height.value()) /
             self.std_work_dist.value()) * self.std_mm_px.value()
        )

    def connect_recursive(self, param, func):
        """
        Recursively connect func to sigValueChanged of all children of param
        except obj_mm_px
        """
        if param is not self.obj_mm_px:
            param.sigValueChanged.connect(func)
            if param.hasChildren():
                [self.connect_recursive(ch, func) for ch in param.children()]

