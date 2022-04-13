from multiprocessing.connection import wait
from flask import Flask,render_template,Response
import cv2
import numpy as np
import time
import os
import handtrackingmodule as htm

app=Flask(__name__)
camera=cv2.VideoCapture(0)

def generate_frames():
    ptime = 0
    canvas = np.zeros((480,640, 3), np.uint8)
    brushthickness = 10
    erasethickness = 15
    overlayList = []
    image = cv2.imread('/home/sourav/test/automation/collerpallet/orange.png')
    overlayList.append(image)
    image = cv2.imread('/home/sourav/test/automation/collerpallet/green.png')
    overlayList.append(image)
    image = cv2.imread('/home/sourav/test/automation/collerpallet/red.png')
    overlayList.append(image)
    image = cv2.imread('/home/sourav/test/automation/collerpallet/blue.png')
    overlayList.append(image)
    image = cv2.imread('/home/sourav/test/automation/collerpallet/erase.png')
    overlayList.append(image)
    header = overlayList[0]
    drawcolor =(0,165,255)

    detector = htm.handDetector(detectionCon=0.65,maxHands=1)
    xprev = 0
    yprev = 0
    thumb = 15
    pinkyfinger = 5
    while True:
            
        ## read the camera frame
        success,img=camera.read()
        if not success:
            print("################image not found#######################")
            break
        else:
            cTime = time.time()
            rate = 1/(cTime - ptime)
            ptime = cTime
            print("################found it not found#######################")

            img = cv2.flip(img, 1)
            img[10:54,10:54] = overlayList[0]
            img[10:54,84:128] = overlayList[1]
            img[10:54,158:202] = overlayList[2]
            img[10:54,232:276] = overlayList[3]
            img[10:54,306:350] = overlayList[4]
            img = detector.findHands(img, draw=True)
            lmlist = []
            fingers = []
            lmList= detector.findPosition(img, draw=False)

            if len(lmList) != 0:
                x = lmList[8][1]
                y = lmList[8][2]
                x2 = lmList[12][1]
                y2 = lmList[12][2]
                thumb = lmList[4][1]
                pinkyfinger = lmList[20][1]
                fingers = detector.fingersUp()
                if fingers[1] and fingers[2]:
                    xprev = 0
                    yprev = 0
                    if x2>=10 and x2<=54 and y2>=10 and y2<=54:
                        drawcolor = (0,165,255)#orange
                    elif x2>=84 and x2<=128 and y2>=10 and y2<=54:
                        drawcolor = (124,252,0)#green
                    elif x2>=158 and x2<=202 and y2>=10 and y2<=54:
                        drawcolor = (0,69,255)#red
                    elif x2>=232 and x2<=276 and y2>=10 and y2<=54:
                        drawcolor = (209,206,0)#blue
                    elif x2>=306 and x2<=350 and y2>=10 and y2<=54:
                        drawcolor = (0,0,0)
                    cv2.circle(img, (x2, y2), 15, drawcolor, cv2.FILLED)
                if fingers[1] and fingers[2] == False:
                    if xprev == 0 and yprev == 0:
                        xprev = x 
                        yprev = y
                    thickness =brushthickness
                    if drawcolor == (0,0,0):
                        thickness = erasethickness
                        cv2.circle(img, (x, y), thickness, drawcolor, cv2.FILLED)
                        cv2.line(canvas, (xprev, yprev), (x, y), drawcolor, thickness)
                    else:
                        cv2.circle(img, (x, y), thickness, drawcolor, cv2.FILLED)
                        cv2.line(canvas, (xprev, yprev), (x, y), drawcolor, thickness)
                    xprev = x
                    yprev = y
                if all (x ==0 for x in fingers) and len(fingers) >4:
                    canvas = np.zeros((480,640, 3), np.uint8)

                # if thumb<pinkyfinger:
                #     cv2.imwrite('savedframe'+ '.jpg', canvas)


            imageingrey = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, invertedimage = cv2.threshold(imageingrey, 50, 255, cv2.THRESH_BINARY_INV)
            invertedimage = cv2.cvtColor(invertedimage,cv2.COLOR_GRAY2BGR)
            img = cv2.bitwise_and(img,invertedimage)
            img = cv2.bitwise_or(img,canvas)



            cv2.putText(img, str(int(rate)), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            ret,buffer=cv2.imencode('.jpg',img)
            img=buffer.tobytes()

        yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')


@app.route('/')
def index():
    print("index method is running")
    return render_template('index.html')

@app.route('/video')
def video():
    print("video method asdifjasdio method is running")
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)
