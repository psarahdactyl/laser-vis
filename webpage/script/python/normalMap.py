#!/usr/bin/env python

import cv2
import numpy as np
import math
import sys
import urllib.request
import io
import scipy
import os
from sklearn.preprocessing import normalize

def create_normal_map(img):
    # make sure image is grayscale to create normal map
    blur_img = cv2.GaussianBlur(img,(3,3),0)

    grayscale_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(os.getcwd()+'/img/_displacement.png', grayscale_img)
    grayscale_img = cv2.bitwise_not(grayscale_img)
    normal_map = np.zeros(img.shape)

    # find gradients in x directions and y directions
    sobelx = cv2.Sobel(grayscale_img,cv2.CV_64F,1,0,ksize=-1) #TODO: find best kernel size for texturing
    sobely = cv2.Sobel(grayscale_img,cv2.CV_64F,0,1,ksize=-1)
    sobelx = np.absolute(((sobelx*2.0) / 255.0) - 1.0)
    sobely = np.absolute(((sobely*2.0) / 255.0) - 1.0)

    ones = np.ones(sobelx.shape)
    zeros = np.zeros(sobelx.shape)
    gx = np.stack([ones, zeros, sobelx], axis=2)
    gy = np.stack([zeros, ones, sobely], axis=2)
    
    n = np.cross(gx,gy)

    normals = np.empty_like(n)

    norm = np.linalg.norm(n, axis=2)
    normals = np.divide(n,norm[:,:,np.newaxis])
    normals = ((normals + 1.0) / 2.0) * 255
    #print(normals)

    normal_map = np.empty_like(normals)
    normal_map[:,:,0] = normals[:,:,2]
    normal_map[:,:,1] = normals[:,:,1]
    normal_map[:,:,2] = normals[:,:,0]

    cv2.imwrite(os.getcwd()+'/img/_normal.png', normal_map)



if __name__ == '__main__':
  #a = sys.argv[1]
  a = sys.stdin.read()
  with urllib.request.urlopen(a) as url:
    img = np.asarray(bytearray(url.read()), dtype='uint8')
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    create_normal_map(img)