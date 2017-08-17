import numpy as np  
import cv2  
import math

img_color = cv2.imread( 'LDC.jpg', cv2.COLOR_BGR2RGB )
#img_color = cv2.imread( 'img3.bmp', cv2.COLOR_BGR2RGB )
jpgheight, jpgwidth, jpgchannel = img_color.shape



img_margin = 10
sampling = 16
palZoom = 1
kwyval = 1
omegaRadian = 150*math.pi/180
rrMax = 400

OriMat = np.zeros((jpgheight, jpgwidth,2), np.float)
TgtMat = np.zeros((jpgheight, jpgwidth,2), np.float)
X,Y = np.meshgrid(np.arange(jpgwidth), np.arange(jpgheight))

img_Ox = jpgwidth/2
img_Oy = jpgheight/2

while kwyval > 0:
    OriMat = TgtMat = np.dstack([Y, X])
    for y in range(0,jpgheight,sampling):
        for x in range(0, jpgwidth,sampling):
            Dy = float(abs(OriMat[y][x][0] - img_Oy))
            Dx = float(abs(OriMat[y][x][1] - img_Ox))
            RR = math.sqrt((Dx * Dx) + (Dy * Dy))
            if Dx :
                theta = math.atan(Dy/Dx)
                Drg = theta*180/3.14
            else:
                Drg = 90
                theta = 90*math.pi/180

            CorrTmp = (rrMax) * math.tan(RR/rrMax)
            RR = CorrTmp/palZoom
            NewdY = RR * np.sin(theta)
            NewdX = RR * np.cos(theta)

            if y<img_Oy:
                TgtMat[y][x][0] = round(img_Oy - round(NewdY) )
            else:
                TgtMat[y][x][0] = round(img_Oy + round(NewdY))

            if x < img_Ox:
                TgtMat[y][x][1] = round(img_Ox - round(NewdX) )
            else:
                TgtMat[y][x][1] = round(img_Ox + round(NewdX))

            if x==0 and y==0:
                img_margin = 50
                palet_ww = img_margin + jpgwidth + img_margin
                palet_hh = img_margin + jpgheight + img_margin
                black_image = np.zeros((palet_hh, palet_ww, 3), np.uint8)
                cv2.rectangle(black_image, (img_margin, img_margin), (img_margin + jpgwidth, img_margin + jpgheight),(240, 240, 240), 1)
                cv2.circle(black_image, (img_margin + jpgwidth / 2, img_margin + jpgheight / 2), 3, (255, 0, 0), 1)

            if img_margin + int(TgtMat[y][x][1])>img_margin and img_margin + int(TgtMat[y][x][1])<1280+img_margin and img_margin + int(TgtMat[y][x][0])>img_margin and img_margin + int(TgtMat[y][x][0])<720+img_margin :
                black_image[img_margin + int(TgtMat[y][x][0]), img_margin + int(TgtMat[y][x][1]), 0]= img_color[y, x, 0]
                black_image[img_margin + int(TgtMat[y][x][0]), img_margin + int(TgtMat[y][x][1]), 1]= img_color[y, x, 1]
                black_image[img_margin + int(TgtMat[y][x][0]), img_margin + int(TgtMat[y][x][1]), 2]= img_color[y, x, 2]


    #black_image = cv2.resize(black_image, (0, 0), fx=palZoom, fy=palZoom)

    font = cv2.FONT_HERSHEY_SIMPLEX
    TEXT = "key(%d) Max(%d) Zoom(%f) smpl(%d)" % (kwyval, rrMax, palZoom,sampling)

    cv2.putText(black_image, TEXT, (20, 50), font, 1, (255, 255, 255), 1)
    cv2.imshow("image", black_image)

    kwyval = cv2.waitKey()

    if kwyval==97:     # A
        rrMax += 50
    if kwyval == 122:  # S
        rrMax -= 50

    if kwyval == 115:  # S
        palZoom -=0.1
    if kwyval == 120:  # X
        palZoom +=0.1

    if kwyval == 100:
        sampling += 2
    if kwyval == 99 and sampling>2:
        sampling -= 2

    if kwyval == 113:
        kwyval = 0

