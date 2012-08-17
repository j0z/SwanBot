#Most of this is taken from OpenCV's examples

import numpy as np
import cv2
import cv2.cv as cv
import time
import os
from video import create_capture
from common import clock, draw_str

def detect(img, cascade):
	rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
		flags = cv.CV_HAAR_SCALE_IMAGE)
	if len(rects) == 0:
		return []
	rects[:,2:] += rects[:,:2]
	return rects

def draw_rects(img, rects, color):
	for x1, y1, x2, y2 in rects:
		cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def compare(face_to_check,learn=False):
	import sys, getopt
	detected_time = 0
	detected_time_max = 10
	
	video_src = 0
	cascade_fn = os.path.join('data','haarcascades','haarcascade_frontalface_alt2.xml')

	cascade = cv2.CascadeClassifier(cascade_fn)

	cam = create_capture(video_src, fallback='synth:bg=../cpp/lena.jpg:noise=0.05')
	
	while True:
		ret, img1 = cam.read()
		gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
		gray = cv2.equalizeHist(gray)
		
		t = clock()
		rects = detect(gray, cascade)
		
		if len(rects):
			if detected_time<detected_time_max:
				detected_time+=1
			else:
				_found_size = (rects[0][0],rects[0][1],rects[0][2]-rects[0][0],
					rects[0][3]-rects[0][1])
				
				_found_face = cv.GetImage(cv.fromarray(img1))
				
				cv.SetImageROI(_found_face,_found_size)
				
				current_face = cv.CreateImage(cv.GetSize(_found_face),
					_found_face.depth,
					_found_face.nChannels)
				
				if learn:
					cv.Copy(_found_face, current_face, None)
					cv.SaveImage(os.path.join('data','images',face_to_check),current_face)
				
				cv.ResetImageROI(cv.GetImage(cv.fromarray(img1)))
				
				img2 = cv.LoadImage(os.path.join('data','images',face_to_check))
				
				dest_face = cv.CreateImage(cv.GetSize(img2),
					img2.depth,
					img2.nChannels)
				
				cv.Resize(_found_face, dest_face)
				
				if cv.Norm(dest_face,img2)<=30000:
					return True
				else:
					return False
				
				sys,exit()
		else:
			detected_time = 0
		
		dt = clock() - t

		#draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
		#cv2.imshow('facedetect', vis)

print compare('luke_facing.jpg',learn=True)

