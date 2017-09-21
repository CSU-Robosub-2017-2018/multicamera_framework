#!/usr/bin/env python
'''
test_multicamera.py - Tests registration of a single video against a
                 background image, detection and classification of things,
                 and identification of the classified things on screen.
'''
from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.bing import Bing
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.controllers.default_controller import DefaultController
from multicamera_framework.cameras.camera_PTZSNC_ER585 import CameraSession
import cv2
import imutils
import multiprocessing
import numpy as np

if __name__ == '__main__':
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Multicamera Test: Testing registration of single video against a"
    print "                  background image, detection and classification,"
    print "                  and drawing of bounding boxes."
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Read in base image
    base = cv2.imread("./test_files/front_base.jpg")
    base = imutils.resize(base, width=1600)

    # Initialize two instances of JIC tools class which implements methods for
    # controlling the registration, detector, classifier and controller
    tools = JICTools(base=base,
                     baseAsImage=True,
                     detector=Bing,
                     classifier=DefaultClassifier,
                     controller=DefaultController)

    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")
    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.3")



    man = multiprocessing.Manager()
    queue = man.Queue()
    # Setup a loop to capture a frame from the video feed
    while True:
        # tools.camContainers[1].setH(np.array(
                                # [[1.26341851e+00, -2.29042207e-01, -5.82081380e+02],
                                 # [7.99743633e-02, 1.52323928e+00, -4.05929038e+02],
                                 # [1.78190698e-04, -1.14213539e-04, 1.00000000e+00]]))
        # tools.camContainers[0].setH(np.array(
                                # [[9.88132986e-01, 7.25633524e-02, -3.67207583e+02],
                                 # [-4.03193648e-02, 1.42428234e+00, -4.57379372e+02],
                                 # [-2.61607264e-04, 3.04265762e-04, 1.00000000e+00]]))
        tools.doNext(queue)

        images = []
        images.append(queue.get())
        images.append(queue.get())
        base_mask = tools.processMasks(images)
        final = tools.processAll(base_mask, images)
        tools.updateBaseFrame()

        cv2.imshow("Boxed", final)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
