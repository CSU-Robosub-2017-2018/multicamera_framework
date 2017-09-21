#!/usr/bin/env python
'''
test_simple.py - Tests registration of a single video against a background
                 image, detection and classification of things, and
                 identification of the classified things on screen.
                 '''
import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
#from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
#from multicamera_framework.controllers.default_controller import DefaultController
#from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.cameras.raspberry_pi_cam_v2 import RaspBCamera
import cv2
import imutils


def dostuff(image, idx, h):
    myheight, mywidth, channels = image.shape
    warp = cv2.warpPerspective(image, h, (mywidth, myheight))

    return warp

if __name__ == '__main__':
    print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print ("Simple Test: Testing registration of single video against a")
    print ("             background image, detection and classification,")
    print ("             and drawing of bounding boxes.")
    print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    base = cv2.imread("./test_files/front_base.jpg")
    base = imutils.resize(base, width=1600)
    # Initialize the JIC tools class which implements methods for controlling
    # the registration, detector and classifier
    tools = JICTools(base=base,
                     baseAsImage=True)
    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")

    # Setup a loop to capture a frame from the video feed
    while True:
        #tools.updateBaseFrame()
        frame = tools.camContainers[0].camera.getFrame()
        frame = cv2.resize(frame, (640, 480))
      
	  
	  # Add processing of image here
	  
        cv2.imshow("Boxed", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
