#!/usr/bin/env python
# -*- coding: utf-8 -*-

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import cv
import numpy as np
import rospy

def switch_to_octant_zero(theta, p):
        step = 6.28/8.0

        if theta < step and theta >= 0.0:
                return p
        if theta < step*2.0 and theta >= step:
                return (p[1],p[0])
	if theta < step*3.0 and theta >= step*2.0:
		return (p[1],-p[0])
	if theta < step*4.0 and theta >= step*3.0:
		return (-p[0],p[1])
	if theta < step*5.0 and theta >= step*4.0:
		return (-p[0],-p[1])
	if theta < step*6.0 and theta >= step*5.0:
		return (-p[1],-p[0])
	if theta < step*7.0 and theta >= step*6.0:
		return (-p[1],p[0])
	if theta < step*8.0 and theta >= step*7.0:
		return (p[0],-p[1])

def switch_from_octant_zero(theta, p):
        step = 6.28/8.0

        if theta < step and theta >= 0.0:
                return p
        if theta < step*2.0 and theta >= step:
                return (p[1],p[0])
        if theta < step*3.0 and theta >= step*2.0:
                return (-p[1],p[0])
        if theta < step*4.0 and theta >= step*3.0:
                return (-p[0],p[1])
        if theta < step*5.0 and theta >= step*4.0:
                return (-p[0],-p[1])
        if theta < step*6.0 and theta >= step*5.0:
                return (-p[1],-p[0])
        if theta < step*7.0 and theta >= step*6.0:
                return (p[1],-p[0])
        if theta < step*8.0 and theta >= step*7.0:
                return (p[0],-p[1])


def detect_collision_in_ray(image, theta, p1, p2):
	p1c = switch_to_octant_zero(theta, p1)
	p2c = switch_to_octant_zero(theta, p2)
	dx = (p2c[0] - p1c[0])
	dy = (p2c[1] - p1c[1])
	D = dy - dx

	line_pos = []
	line_col = []
	y = p1c[1]
	for x in range(p1c[0], p2c[0]-1):
		line_pos.append(switch_from_octant_zero(theta, (x,y)))
		line_col.append(image[line_pos[-1][1]][line_pos[-1][0]])
	#	cv2.line(image, switch_from_octant_zero(theta,(x,y)), switch_from_octant_zero(theta,(x+1,y+1)), (255,0,0), 1)

		if D >= 0:
			y += 1
			D -= dx
		D += dy

	filter = [-1,-1,-1,-1,0,1,1,1,1]
	line_grad =  np.convolve(line_col, filter, 'same')
	for idx, val in enumerate(line_grad):
		if theta > 3.49:
			if np.abs(val) > 100 and idx > 60 and idx < line_grad.size-10:
				cv2.circle(image, line_pos[idx], 6, (255,0,0), 1)
		else:
			if np.abs(val) > 200 and idx > 5 and idx < line_grad.size-10:
				cv2.circle(image, line_pos[idx], 6, (255,0,0), 1)

if __name__ == '__main__':		
with PiCamera() as camera:
	camera.resolution = (1024,768)
	camera.ISO = 100
	camera.sa = 100
	camera.awb = "flash"
	camera.co = 100


	raw_capture = PiRGBArray(camera)

	time.sleep(0.1)

	camera.capture(raw_capture, format="bgr")
	image = raw_capture.array
	image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#circles = cv2.HoughCircles(image_gray, cv2.cv.CV_HOUGH_GRADIENT, 1, 200, param1=50, param2=20, minRadius=110, maxRadius=130)
	circles = cv2.HoughCircles(image_gray, cv2.cv.CV_HOUGH_GRADIENT, 1, 200, param1=50, param2=40, minRadius=10, maxRadius=230)
#	if circles is not None:
#		for c in circles[0,:]:
#			x,y,r = c
#			cv2.circle(image_gray, (x,y), r, (255,0,0), 2)
#	cv2.imshow("test", image_gray)
#	cv2.waitKey(0)
	raw_capture.truncate(0)
		
	for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
		image = frame.array
		image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#	image_gray = cv2.blur(image_gray, (7,7))

	#	circles = cv2.HoughCircles(image_gray, cv2.cv.CV_HOUGH_GRADIENT, 1, 200, param1=50, param2=20, minRadius=140, maxRadius=150)

	#	if True:
		if circles is not None:
	#		circles = np.uint16(np.around(circles))
			x, y, r = circles[0][0]
	#		cv2.circle(image_gray, (x,y), int(r*1.7), (255,0,0), 1)
	#		cv2.circle(image_gray, (x,y), int(r*1.2), (255,0,0), 1)
	#		x = 1024/2
	#		y = 768/2
	#		r = 128
			p1x = int(x + r*1.2)
			p1y = int(y)
			p2x = int(x + r*2.25)
			p2y = int(y)
	
			for theta in np.linspace(0.0, 6.28, 50, False):
				p1xr = int( np.cos(theta) * (p1x - x) - np.sin(theta) * (p1y - y) + x )
				p1yr = int( np.sin(theta) * (p1x - x) + np.cos(theta) * (p1y - y) + y )
				p2xr = int( np.cos(theta) * (p2x - x) - np.sin(theta) * (p2y - y) + x  )
				p2yr = int( np.sin(theta) * (p2x - x) + np.cos(theta) * (p2y - y) + y  )
		#		cv2.line(image_gray, (p1xr, p1yr), (p2xr, p2yr), (255,0,0), 1)
				detect_collision_in_ray(image_gray, theta, (p1xr,p1yr), (p2xr,p2yr))

		cv2.imshow("derp", image_gray)
		key = cv2.waitKey(1) & 0xFF

		raw_capture.truncate(0)

		if key == ord("q"):
			break