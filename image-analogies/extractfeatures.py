#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
import math

def find_3x3_N(matrix):
    features = list()
    h,w,c = matrix.shape
    for i in xrange(h-2):
        i += 1
        for j in xrange(w-2):
            j += 1
            features.append(matrix[np.ix_([i-1,i,i+1],[j-1,j,j+1])])

def find_3x3_edges(matrix):
    features = list()
    h,w,c = matrix.shape
    for i in xrange(w-2):
        i += 1
        features.append(matrix[np.ix_([0],[i-1,i,i+1])])
        features.append(matrix[np.ix_([h-1],[i-1,i,i+1])])
    for i in xrange(h-2):
        i += 1
        features.append(matrix[np.ix_([i-1,i,i+1],[0])])
        features.append(matrix[np.ix_([i-1,i,i+1],[w-1])])


def find_3x3_corners(matrix):
    features = list()
    h,w,c = matrix.shape
    features.append(matrix[np.ix_([0,1],[0,1])])
    features.append(matrix[np.ix_([0,1],[w-2,w-1])])
    features.append(matrix[np.ix_([h-2,h-1],[0,1])])
    features.append(matrix[np.ix_([h-2,h-1],[w-2,w-1])])

def compute_3x3_features(image):
    features = list()
    h,w,c = image.shape
    edges = find_3x3_edges(image)
    corners = find_3x3_corners(image)
    neighborhoods = find_3x3_N(image)

    features.append(corners[0])
    features.append(edges[0:w])
    features.append(corners[1])
    features.append(edges[])

def find_5x5_N(matrix):
    features = list()
    h,w,c = matrix.shape
    for i in xrange(h-4):
        i += 2
        for j in xrange(w-4):
            j += 2
            features.append(matrix[np.ix_([i-2,i-1,i,i+1,i+2],[j-2,j-1,j,j+1,j+2])])

def find_5x5_edges(matrix):
    features = list()
    h,w,c = matrix.shape
    for i in xrange(w-4):
        i += 2
        features.append(matrix[np.ix_([0,1,2],[i-2,i-1,i,i+1,i+2])])
        features.append(matrix[np.ix_([h-1,h-2,h-3],[i-2,i-1,i,i+1,i+2])])
    for i in xrange(h-4):
        i += 2
        features.append(matrix[np.ix_([i-2,i-1,i,i+1,i+2],[0,1,2])])
        features.append(matrix[np.ix_([i-2,i-1,i,i+1,i+2],[w-1,w-2,w-3])])

def find_5x5_corners(matrix):
    features = list()
    h,w,c = matrix.shape
    features.append(matrix[np.ix_([0,1,2],[0,1,2])])
    features.append(matrix[np.ix_([0,1,2],[w-3,w-2,w-1])])
    features.append(matrix[np.ix_([h-3,h-2,h-1],[0,1,2])])
    features.append(matrix[np.ix_([h-3,h-2,h-1],[w-3,w-2,w-1])])

def compute_features(image, size):
    #image = cv2.imread("imgs/red.jpg")
    if size is 3:
        find_3x3_N(image)
        #print(len(features))
        #print('should be ' + str(353*353))

        find_3x3_edges(image)
        #print(len(features))
        #print('should be ' + str((355*355)-4))

        find_3x3_corners(image)
        #print(len(features))
        #print('should be ' + str(355*355))

        #print([i.shape for i in features])
    elif size is 5:
        find_5x5_N(image)

        find_5x5_edges(image)

        find_5x5_corners(image)

    return
