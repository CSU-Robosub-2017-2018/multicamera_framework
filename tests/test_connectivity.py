#!/usr/bin/env python
'''
connectivitity_test.py - Tests basic connections and the initialization of detector, controller and classifier.  Also adds a camera and tests initialization and connectivity of the camera.  Testing of the camera assumes that there is the correct type of camera connected at the specified IP address.  This test uses a 'baseless' initialization.  In typical use cases, the user will need to specify a 'base' to the initialization routine for the JICTools.
'''
from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.controllers.A3C_Controller.A3C_Controller import A3C_Controller
from multicamera_framework.cameras.camera_IMM12018 import IMM_Camera


if __name__ == '__main__':
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Connectivity Test - Tests basic connections and the initialization"
    print "of detector, controller and classifier.  Also adds a camera and "
    print "tests initialization and connectivity of the camera.  Testing of the"
    print "camera assumes that there is the correct type of camera connected at"
    print "the specified IP address.  This test uses a 'baseless' "
    print "initialization.  In typical use cases, the user will need to specify"
    print " a 'base' to the initialization routine for the JICTools."
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    reg = JICTools(detector=Tensorbox,
                   classifier=DefaultClassifier,
                   controller=A3C_Controller)
    reg.addCamera(camera=IMM_Camera, cameraArgs="192.168.0.2")
