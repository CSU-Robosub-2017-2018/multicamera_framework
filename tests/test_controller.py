#!/usr/bin/env python
'''
test_controller.py - Tests the detector, classifier, camera and camera controller.  This test does not do anything meaningful besides setup connections and execute basic functionality. Do not expect meaningful results.
'''
from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.controllers.A3C_Controller.A3C_Controller import A3C_Controller
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.cameras.camera_PTZSNC_ER585 import CameraSession
import cv2
import imutils

if __name__ == '__main__':
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "test_controller.py - Tests the detector, classifier, camera and camera"
    print "controller.  This test does not do anything meaningful besides setup "
    print "connections and execute basic functionality. Do not expect meaningful"
    print "results. "
    print "Press 'q' to quit."
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Read in base image
    base = cv2.imread("./test_files/front_base.jpg")
    base = imutils.resize(base, width=1600)

    # Initialize the JIC tools class which implements methods for controlling
    # the registration, detector, classifier and controller
    tools = JICTools(base=base,
                     baseAsImage=True,
                     detector=Tensorbox,
                     classifier=DefaultClassifier,
                     controller=A3C_Controller)
    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")

    # Setup a loop to capture a frame from the video feed
    for x in xrange(0, 100):
        frame = tools.camContainers[0].camera.getFrame()
        frame = cv2.resize(frame, (640, 480))
        boxes = tools.getBoxes(frame, bestOnly=False)
        if not boxes:
            boxedFrame = frame
        else:
            classBoxes, _ = tools.classify(boxes, frame)
            boxedFrame = tools.drawBoxes(classBoxes, frame)

        cv2.imshow("Boxed", boxedFrame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

        tools.controller.control(
            tools.camContainers[0].camera,
            tools.base,
            frame,
            boxes,
            None
        )
