@mainpage
This document is meant to be read through the Doxygen docs output.  Reading the raw file may lead to confusion due to some markup language used.
# JIC Framework 2016
## Overview
This project is the Joint Inference Control Framework for performing object detection and classification.  The goal of this project is to build a framework in which the following four types of components can be integrated and tested at the system level:

  Cameras\n
  Camera Controllers\n
  Object Detectors\n
  Object Classifiers\n\n

This project is written in Python 2.7+ and relies heavily on OpenCV 3+.  This has been developed and tested on Ubuntu 15.10 64 bit.  Other systems may not the ability to install the correct dependencies (specifically cmake for compiling OpenCV 3+), but the framework code will run on any system that already contain OpenCV 3+ with the correct dependencies installed.  Note that the original development environment needed to be changed from Ubuntu 14.10 to 15.10 because of cmake limitations and some other build tool requirements on 14.10.

In order to use the framework you will need to clone the git repo from the address below.  Once the repo is cloned, please install all dependencies by running the Makefile with the following command:

  __make init__

You can then run a basic test to ensure OpenCV is installed correctly by executing the following and checking for errors in the terminal:

  __make test__

If there are any issues with the install, please refer to the requirements.txt file to see all requirements for both pip installs and apt-get installs.

The git repo is located at:
https://repos.vdl.afrl.af.mil/community/macer/multicamera_framework



### Cameras
Each camera component is an interface to the actual camera hardware.  The camera component is required to retrieve and return individual frames to the framework upon request by the framework.  There are a number of class variables that must be set and functions that must be implemented for the specific camera type in the extended camera class.  Please see the multicamera_framework/cameras/camera.py file or the Doxygen docs for more information.

### Camera Controllers
Each camera controller component is a control algorithm used to control the viewing area of the camera (typically the PTZ settings).  There are a number of functions that must be implemented for the specific controller in the extended controller class. Please see the multicamera_framework/controllers/controller.py file or the Doxygen docs for more information.

### Object Detectors
Each object detector component is an algorithm used to detect objects in each frame of the video feed.  The object detectors are to identify bounding box coordinates that surround the detected objects, and return those bounding boxes back to the framework.  There are a number of functions that must be implemented for the specific controller in the extended object detector class. The bounding boxes that are returned by the detector should be based on a 640x480 image size and will cause many, many errors if they are not.  Please ensure that the detector resizes the input to 640x480 before processing.  Please see the multicamera_framework/detectors/detector.py file or the Doxygen docs for more information.

### Object Classifiers
Each object classifier component is an algorithm used to classify objects that are inside the bounding boxes identified by the object detectors.  The object classifiers are required to return an array of floats that represent the confidence in each class that exists within the classifier.  Typically the framework will take the greatest confidence value and compare that to a threshold.  If the confidence rating is greater than the threshold then the object within the bounding box is noted as being classified.  There are a number of functions that must be implemented for the specific classifier in the extended object classifier class. Please see the multicamera_framework/classifiers/classifier.py file or the Doxygen docs for more information.

### JIC Framework Tools
The JIC framework tools are contained in the multicamera_framework/jic_framework_tools.py file.  The file contains two classes.  The first is a camera container class that is used to capture and associate information with each camera instance.  The second is a class containing general functions for operating on certain aspects of each of the four main component types.  

There are a number of worker functions as well as a number of process flow functions.  Please see the source code or Doxygen docs for detailed information on what each one of the functions does.  These functions can be used without a front end as long as the JICTools class is instantiated.

#### Tool Initialization
The tools take in instances of the controller, detector and classifier upon initialization as well as either a base image to register individual video stream against or a camera instance in which captured frames act as the base image.  If a camera stream is passed in as the base, then the actual instance of the camera needs to be passed in upon initialization.  See the tests as examples for passing in both images and videos as the base.  The initialization of the tools will call the initialization function for the controller, detector and the classifier.  None of these components are actually needed to initialize the tools or use any of the functions within the JICTools class.  There are a number of class variables that automatically get set during a full initialization (passing in a controller, detector and classifier), and some functions will not operate correctly unless the tools are fully initialized.

In order to add individual feeds to the tools, the program needs to make calls to the addCamera() function.  It will take in an instance of the camera as well as the IP address associated with the camera.  Once this function is called, the tools will initialize a CameraContainer class and add that instance to its camContainers list.

Please refer to the Doxygen docs for more information about the initialization and camera adding process.  Also review the tests provided for different examples of tool initialization.

## Tests
### Running example tests
There are a number of example tests available in the tests/ directory.  In order to run one of the tests, navigate to the tests/ directory and execute the test file.  The tests follow typical Python project file naming convention where the test filename is prepended with 'test\_'.

### Creating new tests
To create a new test, it is easiest to copy the heading of an already existing test case and paste it into the new test.  If nothing else, the following line _must_ be added to the header of the new test in order to get proper scoping of the framework files:

  __from context import multicamera_framework__

## GUI
A sample GUI can be used by running the test_gui.py test.  It provides a three paned window, with the top pane containing the base video feed that displays the classified bounding boxes as well as the outline of where the individual video feeds map to on the base video feed.  The middle pane displays check boxes that are used to enable or disable the display bounding boxes of specific classifications.  The bottom pane shows each individual video feed with the classified bounding boxes.

The GUI is written in Tkinter for cross platform compatibility.  The GUI test runs the GUI on one process while it performs all of the backend work on another process.  This prevents deadlock in the GUI while processing occurs.  The GUI test can be extended to add functionality if desired.

## Adding new components
Each of the four components are implemented as abstract classes within the framework.  The files for each component live in the multicamera_framework/<component_type>/ directory.  In order to add new types of components, the abstract classes must be extended.  Examples of this can be found in the multicamera_framework/controllers/default_controller.py and multicamera_framework/classifiers/default_classifier.py files.

The following guidelines should be followed to maintain consistency with the rest of the framework:
  1. All new components should extend the abstract base class.  The base classes are generically named (ex. abstract detector class is multicamera_framework/detectors/detector.py).
  2. The new components _must_ implement the indicated functions from the abstract class in order to interface with the framework correctly.  Check either the source code or the Doxygen docs to find out more information about each abstract class.
  3. New components that are just a single file can be placed in the appropriate component directory (ex. single file detector should be placed in multicamera_framework/detectors/)
  4. New components that are multiple files should be placed in their own containing directory within the appropriate component directory (ex. detector with multiple files should be placed in multicamera_framework/detectors/<new_detector_name>/).  The containing directory needs to have an empty file named '\_\_init\_\_.py' in order for Python to recognize that it can be imported into the project.

## Generating Doxygen documentation
To get the latest documentation for the project, navigate to the multicamera_framework/doc/ directory and execute the following command:

  __doxygen config.dox__

This will generate a html/ and latex/ directory containing the documentation for the project in the respective formats.  The easiest way to view the documentation is to open the html/index.html file in your favorite web browser.
