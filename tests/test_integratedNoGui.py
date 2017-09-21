#!/usr/bin/env python
'''
test_integratedNoGui.py - Tests registration of two video streams against a
                 background video, detection and classification of things,
                 and identification of the classified things on screen.
                 Uses the following flow:
              - Calculates and stores bounding boxes on base image only
              - Figures out (will know from calibration in future) the
                 required homography for each video feed per PTZ settings
              - Displays three different windows to ensure things work:
                  - Window 1 is the base with boxes
                  - Window 2 is one camera with translated boxes from homog
                  - Window 3 is one camera with translated boxes from homog
'''
from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.controllers.default_controller import DefaultController
from multicamera_framework.cameras.camera_PTZSNC_ER585 import CameraSession
from multicamera_framework.cameras.camera_IMM12018 import IMM_Camera
import cv2
import imutils
import numpy as np

if __name__ == '__main__':
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "test_integratedNoGui.py - Tests registration of two video streams against a"
    print "                background video, detection and classification of things,"
    print "                and identification of the classified things on screen."
    print "                Uses the following flow:"
    print "             - Calculates and stores bounding boxes on base image only"
    print "             - Figures out (will know from calibration in future) the"
    print "                required homography for each video feed per PTZ settings"
    print "             - Displays three different windows to ensure things work:"
    print "                 - Window 1 is the base with boxes"
    print "                 - Window 2 is one camera with translated boxes from homog"
    print "                 - Window 3 is one camera with translated boxes from homog"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Read in base image
    base = cv2.imread("./test_files/front_base.jpg")
    base = imutils.resize(base, width=1600)

    # Initialize two instances of JIC tools class which implements methods for
    # controlling the registration, detector, classifier and controller
    tools = JICTools(base=base,
                     baseAsImage=True,
                     detector=Tensorbox,
                     classifier=DefaultClassifier,
                     controller=DefaultController)

    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")
    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.3")
    # tools.addCamera(camera=IMM_Camera, cameraArgs="192.168.0.2")
    # 0: -48.33, 1397.64
    # print "0: ", tools.cameras[0][0].getPan(), "; ", tools.cameras[0][0].getTilt()
    # 1: -33.79, -31.85
    # print "1: ", tools.cameras[1][0].getPan(), "; ",  tools.cameras[1][0].getTilt()

    while True:
        # We know the Homography matrix from testing, so we can force that
        # into the systems information and prevent the homog from updating
        # In the real system the homography will just be looked up and no
        # calculation will be needed
        tools.camContainers[1].setH(np.array(
                [[1.26341851e+00, -2.29042207e-01, -5.82081380e+02],
                 [7.99743633e-02, 1.52323928e+00, -4.05929038e+02],
                 [1.78190698e-04, -1.14213539e-04, 1.00000000e+00]]))
        tools.camContainers[1].setUpdateH(False)
        tools.camContainers[0].setH(np.array(
                [[9.88132986e-01, 7.25633524e-02, -3.67207583e+02],
                 [-4.03193648e-02, 1.42428234e+00, -4.57379372e+02],
                 [-2.61607264e-04, 3.04265762e-04, 1.00000000e+00]]))
        tools.camContainers[0].setUpdateH(False)

        # You can get camera frames from doRealFlow() or from cam instance
        base, camFrames = tools.doRealFlow(normalize=True)
        for idx, camContainer in enumerate(tools.camContainers):
            camFrame = tools.drawBoxes(camContainer.boundingBoxes, camContainer.currFrame)
            cv2.imshow("Cam %s" % idx, camFrame)

        cv2.imshow("Boxed", base)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
