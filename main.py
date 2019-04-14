import sys

# Numpy
import numpy as np


# Pylon
from pypylon import pylon
from pypylon import genicam
import cv2
import PyDIP as dip
import scipy.misc

# GUI imports
import pyforms
# from gui.pyforms import MeasuringApp
from gui.mainwindow import MeasuringApp
from pyqtgraph import QtGui


def save_cam_params(cam, fn):
    """
    Save cam parameters to file fn

    :param cam:
    :param fn:
    :return:
    """
    try:
        pylon.FeaturePersistence.Save(fn, cam.GetNodeMap())
        print("Features saved to {}".format(fn))
    except:
        print("\nFeatures saving failed!")

def grab_one_pic(cam, cs=pylon.PixelType_RGB8packed):
    """
    Grab one image, convert it to required color space

    :param cam:
    :return:
    """
    grab = cam.GrabOne(100)
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = cs
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    img = converter.Convert(grab)
    return img.GetArray()


if __name__ == "__main__":
        # save_cam_params(cam, "Features.pfs")
        # pyforms.start_app(MeasuringApp)
        app = QtGui.QApplication(sys.argv)
        GUI = MeasuringApp()
        sys.exit(app.exec_())
        """
        # Korekcijski faktor debljine etalona
        k_et = (104.5 - 2.366 + 2.13) / (104.5 - 9. +2.13)
        print("Korekcijski faktor debljine etalona: {}".format(k_et))
        pixel_size_corr = k_et * 0.035650623885918005
        print("Korigirani Omjer Pixel/mm: {}".format(pixel_size_corr))
        # grab_show_cv(cam)
        img = dip.Image(grab_one_pic(cam, pylon.PixelType_Mono8))
        img.Show()
        # Thresholding image
        thr = dip.Threshold(img, 'background', parameter=8)
        print("Threshold: {}".format(thr[1]))
        thr[0].Show()
        # Gaussian Smoothing
        smooth = dip.Gauss(img, sigmas=[0])
        smooth.Show()
        thr_sm = dip.Threshold(smooth, 'background', parameter=10)
        print("Gaussian smoothed threshold: {}".format(thr_sm[1]))
        thr_sm[0].Show()
        # Opening with kernel
        mask = dip.Opening(thr_sm[0], dip.SE(21, 'elliptic'))
        mask.Show()
        # Segmenting inner and outer parts
        seg = dip.Convert(dip.EdgeObjectsRemove(mask), 'UINT8')
        seg[seg > 0] = 100
        seg[mask == 0] = 250
        # Assigning physical dimension to segmented px
        seg.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(
            pixel_size_corr, "mm")))
        # seg.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(1, "px")))
        seg.Show()
        # Assigning physical dimension to img px
        img.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(
            pixel_size_corr , "mm")))
        # img.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(1, "px")))
        # Labeling inner and outer objects
        inner_lbl = dip.Label(seg == 100, minSize=100)
        outer_lbl = dip.Label(seg > 99, minSize=100)
        inner_lbl.Show()
        outer_lbl.Show()
        # Measuring
        m_outer = dip.MeasurementTool.Measure(
            outer_lbl, img, features=['Feret', 'Radius', 'Center'])
        m_inner = dip.MeasurementTool.Measure(
            inner_lbl, img, features=['Feret', 'Radius', 'Center'])
        print("\n\n\t\t~~~~ Outer Diameter Measures ~~~~")
        print(m_outer)
        print("\n\n\t\t~~~~ Inner Diameter Measures ~~~~")
        print(m_inner)
        # pixel_size = 20. / m_outer['Feret'][1][1]
        # print('Pixel/mm Omjer etalona: {}'.format(pixel_size))
        # dip.Show(dip.ObjectToMeasurement(outer_lbl, m_outer['Feret']))
        """

    # finally:
    #     pass
        # cam.close()
