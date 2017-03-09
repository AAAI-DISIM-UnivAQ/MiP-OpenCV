import cv2
import numpy as np
start_env = cv2.imread('start_env.jpg')
current_env = cv2.imread('current_env.jpg')

res = cv2.addWeighted(start_env, 0.7, current_env, 0.3, 0)
cv2.imwrite('result_img.jpg', res)
read_img = cv2.imread('result_img.jpg')
#recognise violet object
hsv = cv2.cvtColor(read_img, cv2.COLOR_BGR2HSV)
print(hsv)
lower_violet = np.array([100,0,100])
upper_violet = np.array([255,255,255])

mask = cv2.inRange(hsv, lower_violet, upper_violet)
                              
#Create Contours for all violet objects
contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
maximumArea = 0

bestContour = None
for contour in contours:
    currentArea = cv2.contourArea(contour)
    if currentArea > maximumArea:
        bestContour = contour
        maximumArea = currentArea
        #Create a bounding box around the biggest blue object
        if bestContour is not None:
            x,y,w,h = cv2.boundingRect(bestContour)
            cv2.rectangle(res, (x,y),(x+w,y+h), (0,0,255), 3)
            print((x+w)/2,(y+h)/2)
