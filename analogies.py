#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
import math
#from sklearn.neighbors import LSHForest
from sklearn.neighbors import NearestNeighbors

'''
Based on the paper [Image Analogies, 2001] by Hertzmann et al.
Implemented by Sarah Kushner October 2017.

'''


def create_pyramid(image, num_levels):
    # generate Gaussian pyramid with num_levels for image
    G = image.copy()
    gp = [G]
    h,w,c = image.shape
    for i in range(num_levels):
        print(i)
        # downsample
        G = cv2.pyrDown(G)
        # upsample
        U = cv2.pyrUp(G)
        gp.append(G)
        #plt.imshow(G)
        #plt.show()
        #plt.imshow(U)
        #plt.show()
    return gp

def compute_features(image):
    # append luminance
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV) 
    rgbyuv = np.concatenate((image, yuv), axis=2)
    rgby = f[...,0:4]

    h,w,c = image.shape

    f_3x3 = np.ones(h-2,w-2,c*9)
    f_5x5 = np.ones(h-4,w-4,c*25)

    # go through image and get features by neighboorhoods
    h,w,c = rgby.shape
    for i,row in enumerate(h):
    	for j,p in enumerate(r):
    		small = find_3x3_N(rgby, (i,j))
    		large = find_5x5_N(rgby, (i,j))
    		if small is not None:
    			f_3x3[i][j] = small.flatten
    		if large is not None:
    			f_5x5[i][j] = large.flatten

    return (f_3x3, f_5x5)
    
def make_search_structure(features, level):
    #lshf = LSHForest(n_estimators=20, n_candidates=200, n_neighbors=1).fit(f)
    h,w,c = f.shape
    f = f.reshape(h*w, c)
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(f)
    return nbrs, f

def find_3x3_N(matrix, point):
    i,j = point
    if i-3 < 0 or i+3 > matrix.shape[0]:
    	return None
    else if j-3 < 0 or j+3 > matrix.shape[1]:
    	return None
    return matrix[np.ix_([i-1,i,i+1],[j-1,j,j+1])]

def find_5x5_N(matrix, point):
    i,j = point
    if i-5 < 0 or i+5 > matrix.shape[0]:
    	return None
    else if j-5 < 0 or j+5 > matrix.shape[1]:
    	return None
    return matrix[np.ix_([i-2,i-1,i,i+1,i+2],[j-2,j-1,j,j+1,j+2])]

# concatenates a 3x3 neighborhood and a 5x5 neighborhood
def F_l(small, large):
    return small.flatten() + large.flatten()

def find_best_match(a, a_prime, b, b_prime, s, l, q, i, j,
    pyramids, features, search_structures):

    #pyramids
    a_img_pyr, b_img_pyr, a_prime_img_pyr = pyramids
    a_l = a_img_pyr[l]
    b_l = b_img_pyr[l]
    try:
        a_l_minus_one = a_img_pyr[l+1] 
    except IndexError:
        a_l_minus_one = None

    # find matches
    p_app = best_approx_match(a, a_prime, b, b_prime, l, q, search_structures)
    p_coh = best_coherence_match(a, a_prime, b, b_prime, s, l, q, i, j, features)
    # TODO:
    # compute the weighted distance of neighboorhood features with a gaussian kernel
    d_app = 1
    d_coh = 1
    kappa = 10
    if d_coh < d_app * (1 + kappa * pow(2, (l-num_levels))):
        return p_coh
    else:
        return p_app

def best_approx_match(a, a_prime, b, b_prime, l, q, search_structures):
    (a_structure, a_r), (a_prime_structure, a_p_r), (b_structure, b_r) = search_structures
    p_i = a_structure.kneighbors([q], 1, return_distance=False)
    h,w,c = a_prime
    p = a_p_r[p_i]
    p_app = a_prime[int(p_i/w)][p_i%w]
    if p == p_app:
        return p_app
    else:
        print('help')

def best_coherence_match(a, a_prime, b, b_prime, s, l, q, i, j, features):
    a_features, b_features, a_prime_features = features
    # TODO:
    # also find a way to take out already synthesized as close as possible to 5x5 portions of B' :
    N = b_prime[i][j]
    r_star = np.argmin([ np.norm(F_l(s(r) + (q-r)) - F_l(q)) for r in N])
    p_coh = s(r_star) + (q - r_star)
    return p_coh

# create image analogy
def get_b_prime(a, a_prime, b):
	images = [a, a_prime, b]

    # find the minimum dimension
    a_h,a_w,a_c = a.shape
    a_prime_h,a_prime_w,a_prime_c = a_prime.shape
    b_h,b_w,b_c = b.shape

    if a.shape is not a_prime.shape:
    	print("The images A and A' must be of the same dimensions.")
    	return -1

    num_levels = int(math.log(min(a_h,b_h,a_,b_w),2))

    # initialize image pyramids for A, A', and B
    image_pyramids = list() # [A_pyramid, A'_pyramid, B pyramid]
    for im in images:
    	image_pyramids.append(create_pyramid(im, num_levels))
    # reversed because it goes from coarse to fine
    image_pyramids = reversed(image_pyramids)

    # compute features for A, A', and B
    features = list()
    for pyr in image_pyramids:
    	pyr_features = list()
    	for im in pyr:
    		# appends in the form of (3x3 neighborhood features, 5x5 features)
    		pyr_features.append(compute_features(im))
    	# has the form :
    	# [
    	#   [features of every image in pyramid A], 
    	#   [features of every image in pyramid A'],
    	#   [features of every image in pyramid B] 
    	#      ]
    	features.append(pyr_features) 
   
    # initialize B' stuff
    b_prime = np.ones(b.shape)
    b_prime_img_pyr = list()

    # find best match at every level
    for l in range(num_levels):
    	# image_pyramids[2] is the pyramid for B'
    	# image_pyramids[2][l] is the image at level l in the B' pyramid
        b_prime_l = np.ones(image_pyramids[2][l].shape)

        # source stores all the indices of taken pixels in B'
        source_l = np.ones(b_prime_l.shape)

        # initialize search structures for approximate nearest neighbor
        if l is not 0:
        	search_structure, reshaped_features = make_search_structure(features[l], l)
        else:
        	search_structure, reshaped_features = make_search_structure(features[l]+features[l-1], l)

        for i,row in enumerate(b_prime_l):
            for j,q in enumerate(row):
                p = find_best_match(a, a_prime, b, b_prime, source_l, l, b[i][j], i, j, 
                        pyramids, features, search_structures)
                b_prime_l[i][j] = p
        b_prime_img_pyr.append(b_prime_l)
        
    return b_prime_img_pyr[num_levels]


if __name__ is not "__main__":
    # TODO:
    # read paper again and clarify s(q) = p
    # source of index q in B or B' equals p, an index in A or A'
    a = cv2.imread("imgs/oxbow-mask.png")
    a_prime = cv2.imread("imgs/oxbow.png")
    b = cv2.imread("imgs/oxbow-newmask.png")
    b_prime = get_b_prime(a, a_prime, b)


