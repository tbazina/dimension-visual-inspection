# Pylon
from pypylon import pylon
from pypylon import genicam

from pyqtgraph import QtCore
import pyqtgraph as pg

class CamObject():
    def __init__(self):
        # FPS counter
        self.fps = 0.
        self.fps_count = 0
        self.fps_start = 0.
        # Frame object
        self.frame = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create(self):
        try:
            self.cam = pylon.InstantCamera(
                pylon.TlFactory.GetInstance().CreateFirstDevice())
            print("\nDevice: {}".format(
                self.cam.GetDeviceInfo().GetModelName()))
            # Software trigger configuration registering
            self.cam.RegisterConfiguration(
                pylon.SoftwareTriggerConfiguration(),
                # pylon.AcquireContinuousConfiguration(),
                pylon.RegistrationMode_ReplaceAll,
                pylon.Cleanup_Delete
            )
            # Enabling camera events
            self.cam.GrabCameraEvents = True
        except Exception as e:
            print("\nCamera NOT FOUND!")
            print(e)
            raise

    def open(self):
        """
        Create camera object instance
        """
        # Camera instance
        try:
            self.cam.Open()
            print("\nCamera Opened")
        except Exception as e:
            print('\nCamera Open FAILED!')
            print(e)
            raise

        # Check if camera supports events.
        try:
            if not genicam.IsAvailable(self.cam.EventSelector):
                raise genicam.RuntimeException(
                    "The device doesn't support events.")
        except genicam.GenericException as e:
            # Error handling.
            print("An exception occurred.", e.GetDescription())

        # Maximum number of buffers for simultaneous image grabbing
        try:
            self.cam.MaxNumBuffer = 10
            print("\nMaximum Buffer Number: {}".format(
                self.cam.MaxNumBuffer.GetValue()))
        except Exception as e:
            print("\ncam.MaxNumBuffer FAILED!")
            print(e)
            raise

        # Frame rate upper limit for for simultaneous image grabbing
        try:
            self.cam.AcquisitionFrameRateEnable.SetValue(True)
            self.cam.AcquisitionFrameRate = 50
            print("\nFrame rate upper limit: {} FPS".format(
                self.cam.AcquisitionFrameRate.GetValue()))
        except Exception as e:
            print("\ncam.AcquisitionFrameRate  FAILED!")
            print(e)
            raise

        # Pixel format
        try:
            self.cam.PixelFormat = "Mono8"
            print("\nImage format: {}".format(self.cam.PixelFormat.GetValue()))
        except Exception as e:
            print("\ncam.PixelFormat FAILED!")
            print(e)
            raise

    def close(self):
        try:
            self.cam.Close()
            print("\nCamera Closed!")
        except Exception as e:
            print("\nClosing FAILED!")
            print(e)
            raise

    def print_info(self):
        """
        Print Camera info
        """
        try:
            print("\n\t\t~~~~ Camera Info ~~~~")
            print("\nDevice Vendor Name: {}".format(
                self.cam.DeviceVendorName.GetValue()))
            print("\nCamera Sensor")
            print("\tWidth: {} px".format(self.cam.SensorWidth.GetValue()))
            print("\tHeight: {} px".format(
                self.cam.SensorHeight.GetValue()))
            print("\nROI")
            print("\tMax Width: {} px".format(self.cam.WidthMax.GetValue()))
            print("\tMax Height: {} px".format(self.cam.HeightMax.GetValue()))
            print("\nDevice Link Speed: {} MB/sec".format(
                self.cam.DeviceLinkSpeed.GetValue()*1e-6))
            print("\nGain: {} dB".format(self.cam.Gain.GetValue()))
            print("\tMax: {} dB".format(self.cam.Gain.Max))
            print("\tMin: {} dB".format(self.cam.Gain.Min))
            print("\nExposure time: {} us".format(self.cam.ExposureTime()))
            print("\tMax: {}".format(self.cam.ExposureTime.Max))
            print("\tMin: {}".format(self.cam.ExposureTime.Min))
        except Exception as e:
            print('\nCamera Print Info FAILED!')
            print(e)
            raise


    def set_default_params(self):
        """
        MaxNumBuffer: 8
        """
        print("\n\t\t~~~~ Setting Default Parameters ~~~~")
        # Amplification of camera signal
        try:
            self.cam.GainAuto.SetValue("Off")
            self.cam.Gain = 2.28869
            print("\nGain: {} dB".format(self.cam.Gain()))
        except Exception as e:
            print("\ncam.Gain FAILED!")
            print(e)
            raise

        # Exposure time
        try:
            self.cam.ExposureAuto.SetValue("Off")
            self.cam.ExposureTime = 60000  # us
            print("\nExposure Time: {} us".format(
                self.cam.ExposureTime()))
        except Exception as e:
            print("\ncam.ExposureTime FAILED!")
            print(e)
            raise

        # ROI Size and position
        try:
            if genicam.IsWritable(self.cam.Width):
                self.cam.Width = self.cam.Width.Max
                # self.cam.Width.SetValue(1248)
            if genicam.IsWritable(self.cam.Height):
                self.cam.Height = self.cam.Height.Max
                # self.cam.Height.SetValue(750)
            if genicam.IsWritable(self.cam.OffsetX):
                self.cam.OffsetX = self.cam.OffsetX.Min
                # self.cam.OffsetX.SetValue(544)
            if genicam.IsWritable(self.cam.OffsetY):
                self.cam.OffsetY = self.cam.OffsetY.Min
                # self.cam.OffsetY.SetValue(800)
            print("\nImage ROI")
            print("\tOffsetX: {} px".format(self.cam.OffsetX.GetValue()))
            print("\tOffsetY: {} px".format(self.cam.OffsetY.GetValue()))
            print("\tWidth: {} px".format(self.cam.Width.GetValue()))
            print("\tHeight: {} px".format(self.cam.Height.GetValue()))
        except Exception as e:
            print("\nSetting ROI FAILED!")
            print(e)
            raise

    def set_gain(self, gain):
        """
        Set amplification of camera signal
        """
        try:
            self.cam.Gain = gain
            # print("\nGain: {} dB".format(self.cam.Gain()))
        except Exception as e:
            print("\ncam.Gain FAILED!")
            print(e)
            raise

    def set_exposure_time(self, exp_time):
        """
        Set camera exposure time
        """
        try:
            self.cam.ExposureTime = exp_time
            # print("\nExposure Time: {} us".format(self.cam.ExposureTime()))
        except Exception as e:
            print("\ncam.ExposureTime FAILED!")
            print(e)
            raise

    def set_width(self, width):
        """
        Set Camera ROI Width
        """
        try:
            if genicam.IsWritable(self.cam.Width):
                self.cam.Width = width
        except Exception as e:
            print("\ncam.Width FAILED!")
            print(e)
            raise

    def set_height(self, height):
        """
        Set Camera ROI Height
        """
        try:
            if genicam.IsWritable(self.cam.Height):
                self.cam.Height = height
        except Exception as e:
            print("\ncam.Height FAILED!")
            print(e)
            raise

    def set_offsetx(self, offsetx):
        """
        Set Camera ROI X Axis Offset
        """
        try:
            if genicam.IsWritable(self.cam.OffsetX):
                self.cam.OffsetX = offsetx
        except Exception as e:
            print("\ncam.OffsetX FAILED!")
            print(e)
            raise

    def set_offsety(self, offsety):
        """
        Set Camera ROI Y Axis Offset
        """
        try:
            if genicam.IsWritable(self.cam.OffsetY):
                self.cam.OffsetY = offsety
        except Exception as e:
            print("\ncam.OffsetY FAILED!")
            print(e)
            raise

    def start_grabbing(self, strategy=pylon.GrabStrategy_LatestImageOnly):
        try:
            self.cam.StartGrabbing(
                strategy, pylon.GrabLoop_ProvidedByInstantCamera)
            print('\nGrabbing started!')
        except Exception as e:
            print('\nGrabbing FAILED!')
            print(e)
            raise

    def stop_grabbing(self):
        try:
            self.cam.StopGrabbing()
            print('\nGrabbing stopped!')
        except Exception as e:
            print("\nStop Grabbing FAILED!")
            print(e)
            raise

    def frame_burst(self, joinable_queue):
        """
        Grab frames from camera using software trigger, scheduling and event
        handler
        """
        if self.fps_count == 0:
            self.fps_start = pg.ptime.time()
        if self.cam.IsGrabbing():
            if self.cam.WaitForFrameTriggerReady(
                    300, pylon.TimeoutHandling_ThrowException):
                self.cam.ExecuteSoftwareTrigger()
                self.frame = joinable_queue.get()
                self.fps_count += 1
                if self.fps_count >= 50:
                    fps_time = pg.ptime.time() - self.fps_start
                    self.fps = self.fps_count / fps_time
                    print("Camera FPS: {:.2f}".format(
                        self.cam.ResultingFrameRate.GetValue()))
                    print("FPS: {:.2f}".format(self.fps))
                    self.fps_count = 0
                QtCore.QTimer.singleShot(1, self.frame_burst)

