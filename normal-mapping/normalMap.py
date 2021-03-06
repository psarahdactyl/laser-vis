#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.preprocessing import normalize

import time

###########################
# timing code from 
# https://stackoverflow.com/questions/5849800/tic-toc-functions-analog-in-python

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)
###########################

def create_normal_map(img):
    # make sure image is grayscale to create normal map
    blur_img = cv2.GaussianBlur(img,(3,3),0)

    grayscale_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)
    grayscale_img = cv2.bitwise_not(grayscale_img)
    normal_map = np.zeros(img.shape)

    # find gradients in x directions and y directions
    sobelx = cv2.Sobel(grayscale_img,cv2.CV_64F,1,0,ksize=-1) #TODO: find best kernel size for texturing
    sobely = cv2.Sobel(grayscale_img,cv2.CV_64F,0,1,ksize=-1)
    sobelx = np.absolute(((sobelx*2.0) / 255.0) - 1.0)
    sobely = np.absolute(((sobely*2.0) / 255.0) - 1.0)

 
    tic()
    h,w,c = img.shape

    ones = np.ones(sobelx.shape)
    zeros = np.zeros(sobelx.shape)
    gx = np.stack([ones, zeros, sobelx], axis=2)
    gy = np.stack([zeros, ones, sobely], axis=2)
    
    n = np.cross(gx,gy)
    print(n)

    h,w,c = n.shape
    #print(h,w,c)
    normals = np.empty_like(n)

    norm = np.linalg.norm(n, axis=2)
    normals = np.divide(n,norm[:,:,np.newaxis])
    normals = ((normals + 1.0) / 2.0) * 255
    #print(normals)

    normal_map = np.empty_like(normals)
    normal_map[:,:,0] = normals[:,:,2]
    normal_map[:,:,1] = normals[:,:,1]
    normal_map[:,:,2] = normals[:,:,0]

    cv2.imwrite('normal.png', normal_map)
    toc()
    
if __name__ == '__main__':
  img = cv2.imread('test.jpg')

  create_normal_map(img)