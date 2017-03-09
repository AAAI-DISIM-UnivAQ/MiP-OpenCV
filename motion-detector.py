# import the necessary packages
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import redis
import numpy as np

red = redis.Redis(host='127.0.0.1', port=6379)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
print conf
client = None


# initialize the camera and grab a reference to the raw camera capture
video_capture = cv2.VideoCapture(0)

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

#k=0
# capture frames from the camera
start_env = cv2.imread('start_env.jpg')
while True:
	# grab the raw NumPy array representing the image and initialize
	# the timestamp and occupied/unoccupied text

	ret, frame = video_capture.read()
	#timestamp = datetime.datetime.now()
	text = "Unoccupied"

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the average frame is None, initialize it
	if avg is None:
		print "[INFO] starting background model..."
		avg = gray.copy().astype("float")
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# loop over the contours
	for c in cnts: 
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < conf["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		#Send center to Redis
		center = ((x + w / 2), (y + h / 2 ))
		red.lpush("mip_position", center)
		cv2.rectangle(frame, (x-25 , y-25), (x + w + 25 , y + h + 25), (255, 0, 0),-1)
		text = "Occupied"

	if text == "Occupied":

		# check to see if enough time has passed between uploads
		#if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
			# increment the motion counter
			#motionCounter += 1

			# check to see if the number of frames with consistent motion is
			# high enough
			#if motionCounter >= conf["min_motion_frames"]:
                                #path = "current_env.jpg"
                                #cv2.imwrite(path, frame)


				motionCounter = 0

                                #image-merge

                                current_env = frame
                                res = cv2.addWeighted(start_env, 0.5, current_env, 0.5, 0)
                                #cv2.imwrite('result_img.jpg', res)
                                #recognise violet object
                                read_img  = res
                                hsv = cv2.cvtColor(read_img, cv2.COLOR_BGR2HSV)
                                lower_violet = np.array([133,100,100])
                                upper_violet = np.array([151,255,255])

                                mask = cv2.inRange(hsv, lower_violet, upper_violet)
                                res = cv2.bitwise_and(read_img,read_img, mask= mask)
								# Create Contours for all violet objects
                                contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                maximumArea = 0
                                bestContour = None
                                for contour in contours:
                                    currentArea = cv2.contourArea(contour)
                                    x,y,w,h = cv2.boundingRect(contour)
                                    cv2.rectangle(res, (x,y),((x+w),(y+h)), (0,255,0), 3)
                                    violet_center = (x + w/2, y + h/2)
                                    cv2.circle(frame, violet_center,3, (0,255,0), 3)
                                    red.lpush("obs_position", violet_center)                                            
                                    #red.publish("event_collision",1)
                                #if len(contours) == 0:
                                 #       red.publish("event_collision",0)
	# otherwise, the room is not occupied
	#else:
                #red.publish("event_collision",-1)
	#	motionCounter = 0

	# check to see if the frames should be displayed to screen
	if conf["show_video"]:
		# display the security feed
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break

        
