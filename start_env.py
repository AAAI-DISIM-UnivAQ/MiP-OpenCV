from picamera import PiCamera
import cv2
import numpy as np
from time import sleep

camera = PiCamera()
camera.saturation=100
camera.resolution = (500,375)
camera.start_preview()
sleep(5)
path='/home/pi/Downloads/motion-detection-with-opencv-master/start_env.jpg'
camera.capture(path)
camera.stop_preview()

start_env = cv2.imread(path)
hsv = cv2.cvtColor(start_env, cv2.COLOR_BGR2HSV)
lower_red = np.array([0,110,95])
upper_red = np.array([20,255,255])
mask = cv2.inRange(hsv, lower_red, upper_red)
res = cv2.bitwise_and(start_env,start_env, mask= mask)

cv2.imshow('obs',res)
contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
maximumArea = 0
bestContour = None
for contour in contours:
        currentArea = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        cv2.rectangle(res, (x-10,y-10),((x+w+10),(y+h+10)), (0,0,255), -1)

cv2.imshow('prova', res)
cv2.imwrite(path, res)
