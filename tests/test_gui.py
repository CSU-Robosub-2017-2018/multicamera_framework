#!/usr/bin/env python
'''
test_gui.py - This test is an example of how to build a GUI using the JIC
Framework package.  It will place the base image with classified bounding
boxes in the top frame, and place the individual feeds side-by-side in the
bottom frame.  The individual feeds also have the classified bounding boxes
that exist within their frame of view.  This calls the doRealFlow() function
in the JIC framework.  The GUI and processing are each on their own thread
and communicate via queues.  This test is using predetermined homographies
for each camera in order to speed things up.  The ideal setup would be to have
a lookup table of homographies for each camera based on the PTZ settings of
that camera.  Those homographies would then be applied inside the doRealFlow()
via a call to find the homography matrix from the lookup table.
'''
from __future__ import division
from Tkinter import *
from PIL import Image, ImageTk
from Queue import Empty
import cv2
import imutils
import multiprocessing

from context import multicamera_framework
from multicamera_framework.jic_framework_tools import JICTools
from multicamera_framework.detectors.tensorbox.tensorbox import Tensorbox
from multicamera_framework.classifiers.patrick.image_to_classification import Image2Class
from multicamera_framework.controllers.default_controller import DefaultController
from multicamera_framework.controllers.A3C_Controller.A3C_Controller import A3C_Controller
from multicamera_framework.classifiers.default_classifier import DefaultClassifier
from multicamera_framework.cameras.camera_PTZSNC_ER585 import CameraSession
from multicamera_framework.cameras.camera_IMM12018 import IMM_Camera


class MACER_GUI:

    def __init__(self,
                 q,          # Queue for passing in frames
                 framerate,  # The framerate, causes a delay between updates
                 numVids,    # The number of individual feeds
                 killEvent,  # The multiprocessing kill event
                 classList,  # List of possible classifications
                 guiQ,       # Queue for passing back flags
                 height=900,
                 width=1400):
        self.liveFeeds = []
        self.liveFeedIdx = 0
        # convert framerate to delay time
        self.framerateDly = int(1000/framerate)
        self.kill = killEvent

        self.root = Tk()

        self.classList = classList
        self.guiQ = guiQ

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        self.numVids = numVids
        self.height = height
        self.width = width
        self.cameraWidth = min(int(width/numVids), 400)
        self.cameraHeight = int(300*(self.cameraWidth/400))

        # calculate x and y coordinates for the Tk root window
        x = int(w/4) - int(width/2)
        y = int(h/2) - int(height/2)
        # Prevent resize
        self.root.resizable(width=False, height=False)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.root.title("MACER")

        # Menu bars
        self.menubar = Menu(self.root)
        # File menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit..", command=self.quitAndKill)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # Help menu
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About..", command=self.doNothing)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        # Display the menubar
        self.root.config(menu=self.menubar)

        # Setup the frames
        # ## Top Frame: Contains registered feed
        self.registeredFrame = Frame(self.root)
        self.registeredFrame.pack(side=TOP)
        # ## Checkbox frame: contains the classification check boxes
        self.checkboxFrame = Frame(self.root)
        self.checkboxFrame.pack(side=TOP)
        # ## Bottom Frame: Contains the individual feeds
        self.individualFrame = Frame(self.root)
        self.individualFrame.pack(side=BOTTOM)

        # ### Add registered feed box to the top frame
        self.registeredFeed = Label(self.registeredFrame)
        self.registeredFeed.pack(side=RIGHT, padx=1, pady=1)

        # ### Add live feed boxes to bottom frame
        for x in xrange(0, numVids):
            self.liveFeeds.append(Label(self.individualFrame))
            self.liveFeeds[x].pack(side=LEFT, padx=5, pady=1)

        # ### Setup check boxes for displaying classed frames
        self.classListVars = []
        for x in xrange(0, len(self.classList)):
            var = IntVar(self.checkboxFrame)
            var.set(1)
            c = Checkbutton(self.root,
                            text=self.classList[x],
                            variable=var,
                            command=self.checkButton)
            c.pack(side=LEFT, fill=X, expand=1, pady=2)
            self.classListVars.append(var)

        self.checkAllVar = IntVar(self.checkboxFrame)
        self.checkAllBoxes = Checkbutton(self.root,
                                         text='Select All',
                                         variable=self.checkAllVar,
                                         command=self.checkAllButton)
        self.checkAllVar.set(1)
        self.checkAllBoxes.pack(side=LEFT, fill=X, expand=1, pady=2)

        # Check the queue every framerateDly millis
        self.root.after(self.framerateDly, self.CheckQueuePoll, q)

    def checkAllButton(self):
        for idx, var in enumerate(self.classListVars):
            self.classListVars[idx].set(self.checkAllVar.get())
        self.checkButton()

    def checkButton(self):
        # Clear and update the queue - this way we can change more than one
        # checkbox at a time
        while not guiQ.empty():
            try:
                guiQ.get(False)
            except Empty:
                continue
            guiQ.task_done()
        varVal = [var.get() for var in self.classListVars]
        self.guiQ.put(varVal)

    def quitAndKill(self):
        # print "quitting.."
        self.kill.set()
        self.root.quit

    def doNothing(self):
        print "Nothing.."

    def CheckQueuePoll(self, queue):
        try:
            base, camFeeds = queue.get(0)
            base = imutils.resize(base,
                                  height=(self.height - self.cameraHeight))
            base = cv2.cvtColor(base, cv2.COLOR_BGR2RGB)
            photo = Image.fromarray(base)
            photo = ImageTk.PhotoImage(photo)

            self.registeredFeed.configure(image=photo)
            self.registeredFeed.image = photo

            for idx, frame in enumerate(camFeeds):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, width=self.cameraWidth)
                # this Image.fromarray() is the ticket/glue/magic the gathering
                photo = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(photo)

                self.liveFeeds[idx].configure(image=photo)
                self.liveFeeds[idx].image = photo
        except Empty:
            pass
        finally:
            self.root.after(self.framerateDly, self.CheckQueuePoll, queue)


def generateVid(q):
    base, camFrames = tools.doRealFlow(control=False)
    for idx, camContainer in enumerate(tools.camContainers):
        camFrames[idx] = tools.drawClassBoxes(
            camContainer.currFrame,
            camContainer.boundingBoxes,
            camContainer.boxClasses,
            drawName=True)
    q.put((base, camFrames))

if __name__ == '__main__':
    m = multiprocessing.Manager()
    q = m.Queue(20)
    guiQ = m.Queue(20)

    killEvent = multiprocessing.Event()

    # Read in base image
    # base = cv2.imread("./test_files/front_base.jpg")
    # base = imutils.resize(base, width=1600)

    # Initialize the JIC tools class which implements methods for
    # controlling the registration, detector, classifier and controller
    tools = JICTools(base=CameraSession,
                     baseArgs="192.168.0.4",
                     # baseAsImage=True,
                     detector=Tensorbox,
                     classifier=DefaultClassifier,
                     controller=A3C_Controller)

    tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.3")
    tools.addCamera(camera=IMM_Camera, cameraArgs="192.168.0.2")
    classificationList = tools.classifier.getClassNames()

    # DEBUG
    # 0: -48.33, 1397.64
    # print "0: ", tools.cameras[0][0].getPan(), "; ",
    # tools.cameras[0][0].getTilt()
    # 1: -33.79, -31.85
    # tools.addCamera(camera=CameraSession, cameraArgs="192.168.0.4")
    # tools.addCamera(camera=IMM_Camera, cameraArgs="192.168.0.2")
    # 0: -48.33, 1397.64
    # tools.camContainers[0].camera.setPan(-48.33)
    # tools.camContainers[0].camera.setTilt(1397.64)
    # print "0: ", tools.camContainers[0].camera.getPan(), "; ",
    # tools.camContainers[0].camera.getTilt()
    # 1: -33.79, -31.85
    # tools.camContainers[1].camera.setPan(-33.79)
    # tools.camContainers[1].camera.setTilt(-31.85)
    # print "1: ", tools.camContainers[1].camera.getPan(), "; ",
    # tools.camContainers[1].camera.getTilt()

    framerate = 100
    numVids = 3
    macer = MACER_GUI(q,
                      framerate,
                      numVids,
                      killEvent,
                      classificationList,
                      guiQ)

    # Start the tkinter gui on another process so we can do stuff
    p_macer = multiprocessing.Process(target=macer.root.mainloop)
    p_macer.daemon = True
    p_macer.start()

    try:
        while not killEvent.is_set():
            generateVid(q)
            try:
                enabledClasses = guiQ.get(0)
                tools.enabledClasses = enabledClasses
            except Empty:
                pass
    except KeyboardInterrupt:
        exit(0)
