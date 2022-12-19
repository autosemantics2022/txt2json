import random
import numpy as np
import os
import cv2
import glob
from PIL import Image
import PIL.ImageOps    
import shutil
import matplotlib.pyplot as plt
import base64
import json
from collections import OrderedDict
from pathlib import Path
from random import randrange

# json 파일을 만들기 위해 참고해야 할 txt 파일이 들어있는 주소
file_path = "Yolov7-Pytorch/runs/predict-seg/exp11/labels/" 

# file_path 폴더에 있는 파일의 리스트
file_names = os.listdir(file_path) #array that have file name


# json 파일을 만들 predict 폴더의 주소
file_path2 = "Yolov7-Pytorch/runs/predict-seg/exp11/" 

# file_path2 폴더에 있는 파일의 리스트
file_names2 = os.listdir(file_path2) #array that have file name

# predict 되기 전의, 픽셀 부분이 segment되지 않은 이미지의 주소
raw_path = "Yolov7-Pytorch/test2017/"


#obejct의 클래스
def getLabel(line):
    line = int(line)
    if (line == 0):
        label = "artificial stone"
    if (line == 1):
        label = "terrazotile"
    if (line == 2):
        label = "stone"
    if (line == 3):
        label = "vinyl tile"
    if (line == 4):
        label = "window"
    if (line == 5):
        label = "wood"
    if (line == 6):
        label = "rubber"
    if (line == 7):
        label = "tile"
    if (line == 8):
        label = "chair&desk"
    if (line == 9):
        label = "vinyle sheet"
    if (line == 10):
        label = "access floor"
    if (line == 11):
        label = "elastic floor"
    return label
    

for f in file_names:

    global img_name #json에 들어갈 image path
    global name #json저장할때 쓰일것임
    for i in file_names2:
        name = os.path.splitext(f)
        image = os.path.splitext(i)
        if(name[0]==image[0]):
            img_path = i
            break
    
    img_data = base64.b64encode(open(os.path.join(raw_path,img_path),"rb").read()).decode("utf-8") #json에 들어갈 image data

    now_file_name = os.path.join(file_path,f) #txt 경로 설정


    print(now_file_name)

    myFile = open(now_file_name, 'r')
    listarr = list(enumerate(myFile))
    total_line = listarr[-1][0]+1

    myFile.close()


    #json틀 생성
    file_data = OrderedDict()
    file_data["version"] = "5.0.1"
    file_data["flags"] = {}
    file_data["shapes"] = []
    file_data["imagePath"] = img_path
    file_data["imageData"] = img_data
    file_data["imageHeight"] = 3024
    file_data["imageWidth"] = 4032

    #total line만큼 ojbect가 있음
    for i in range(total_line):
        line = listarr[i][1].split(' ') #띄어쓰기로 나눈 값들이 들어간 리스트
        #label = line[0] #라벨
        label = getLabel(line[0])
        #txt파일을 토대로 json에서의 boundingbox의 중심좌표(x,y), 너비, 높이 복원하기
        center_x = float(line[1]) * 4032 #boundingbox 중심좌표 x
        center_y = float(line[2]) * 3024 #boundingbox 중심좌표 y
        width = float(line[3]) * 4032 #boundingbox 너비
        height = float(line[4]) * 3024 #boundingbox 높이

        #json 파일에는 bounding box의 4개의 꼭짓점이 polygon형식으로 들어감
        #각 꼭짓점의 좌표 구하기
        basket = [0,0,0,0,0,0,0,0]
        basket[0] = center_x - width/2
        basket[1] = center_y - height/2
        basket[2] = center_x + width/2
        basket[3] = center_y - height/2
        basket[4] = center_x + width/2
        basket[5] = center_y + height/2
        basket[6] = center_x - width/2
        basket[7] = center_y + height/2

        #json point 영역에 해당한 값 지정
        point_list = []
        index = 0
        for i in range(4):
            xy = []
            for j in range(2):
                xy.append(basket[index])
                index = index + 1
            point_list.append(xy)

        file_data["shapes"].append({"label": label, "points": point_list, "group_id": None, "shape_type": "polygon", "flags": {}})

    #Yolov7-Pytorch/resultmerge/에 json파일들 저장
    with open('Yolov7-Pytorch/resultmerge/'+name[0]+'.json','w',encoding="utf-8") as make_file:
        json.dump(file_data, make_file,ensure_ascii=False,indent="\t")
