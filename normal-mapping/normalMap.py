#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy
from sklearn.preprocessing import normalize

import time

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

    '''
    cv2.imshow('image', sobelx)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow('image', sobely)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    tic()
    h,w,c = img.shape
    # go through each pixel in the image
    for i in range(h):
      for j in range(w):

        gx = np.array([1,0,sobelx[i][j]])
        gy = np.array([0,1,sobely[i][j]])


        n = np.cross(gx,gy)

        #normal = normal / np.linalg.norm(normal)
        normal = normalize(n[:,np.newaxis], axis=0).ravel()

        r = ((normal[0] + 1.0) / 2.0) * 255   
        g = ((normal[1] + 1.0) / 2.0) * 255   
        b = ((normal[2] + 1.0) / 2.0) * 255

        #print(r,g,b)

        normal_map[i][j][0] = b
        normal_map[i][j][1] = g
        normal_map[i][j][2] = r

        #print(normal_map[i][j])

    cv2.imwrite('normal.png', normal_map)
    toc()
    
if __name__ == '__main__':
  img = cv2.imread('test1.jpg')

  create_normal_map(img)