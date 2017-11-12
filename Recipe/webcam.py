#!/usr/bin/env python
#
# Snippet to save image of a builtin webcam.
# Taken from numerous sources and minified.
#
# Sometimes I get "select timeout" message.
# Do not know why, perhaps a too dark image?

import opencv 
import opencv.highgui

cc = opencv.highgui.cvCreateCameraCapture(0)
im = opencv.highgui.cvQueryFrame(cc)
opencv.highgui.cvSaveImage("/tmp/webcam.png", im)

