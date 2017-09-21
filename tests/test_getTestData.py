#!/usr/bin/env python
'''
test_getTestData.py - Gathering test data (base images, bounding boxes, box locations) for patricks classifier
'''
from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.cameras.camera_PTZSNC_ER585 import CameraSession
import cv2
import os
import errno
import shutil


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

if __name__ == '__main__':
    tools = JICTools(detector=Tensorbox,
                     classifier=DefaultClassifier)

    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")
    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.3")


    path = "/home/cskunk/temp/for_patrick"
    # clean path
    shutil.rmtree(path)

    cam0Path = path + "/cam0"
    cam1Path = path + "/cam1"
    mkdir_p(cam0Path)
    mkdir_p(cam1Path)

    for x in xrange(0, 10):
        for idx, camContainer in enumerate(tools.camContainers):
            # make the directory for the current image in the correct cam location
            framePath = path + "/cam" + str(idx) + "/frame" + str(x)
            mkdir_p(framePath)

            # get the image
            frame = camContainer.camera.getFrame()
            cv2.imwrite(framePath + "/frame" + str(x) + ".jpg", frame)
            height, width, _ = frame.shape
            h_ratio = height/480
            w_ratio = width/640

            # find the boxes and save the boxes
            boxes = tools.getBoxes(frame, bestOnly=False)
            bigBoxes = []
            for box in boxes:
                bigBoxes.append([int(w_ratio*box[0]),
                                 int(h_ratio*box[1]),
                                 int(w_ratio*box[2]),
                                 int(h_ratio*box[3])])
            boxPath = framePath + "/boxes"
            mkdir_p(boxPath)
            f = open(framePath + '/boxes_frame%s.txt' % idx, 'w')
            # extract the boxed images and save as the name as the box location
            for box in bigBoxes:
                f.write("%s\n" % box)
                boxedImg = frame[box[1]:box[3], box[0]:box[2]]
                cv2.imwrite(boxPath + "/%s.jpg" % box, boxedImg)
            f.close()
