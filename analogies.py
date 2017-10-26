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
        #print(i)
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
    rgby = rgbyuv[...,0:4]

    h,w,c = image.shape

    if h-2 > 0 and w-2 > 0:
        f_3x3 = np.ones((h-2,w-2,rgby.shape[2]*9))
    else:
        f_3x3 = np.ones((2,2,rgby.shape[2]*9))
    if h-4 > 0 and w-4 > 0:
        f_5x5 = np.ones((h-4,w-4,rgby.shape[2]*25))
    else:
        f_5x5 = np.ones((4,4,rgby.shape[2]*25))

    # go through image and get features by neighboorhoods
    h,w,c = rgby.shape
    for i,row in enumerate(rgby):
        for j,p in enumerate(row):
            small = find_3x3_N(rgby, (i,j))
            large = find_5x5_N(rgby, (i,j))
            if small is not None:
                f_3x3[i][j] = small.flatten()
            if large is not None:
                f_5x5[i][j] = large.flatten()

    return (f_3x3, f_5x5)

def combine_features(list_of_features):
    combined = np.ones((list_of_features[0]).shape) # all feature matrices should be the same shape
    for m in list_of_features:
        combined = np.concatenate((combined,m), axis=2)

    print("combined")
    print(type(combined))
    return combined

def make_search_structure(features, level):
    #lshf = LSHForest(n_estimators=20, n_candidates=200, n_neighbors=1).fit(f)
    #h,w,c = features.shape
    f = features
    h,w,c = f.shape
    f = f.reshape(h*w,c)
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(f)
    return nbrs, f

def find_3x3_N(matrix, point):
    i,j = point
    if i-3 < 0 or i+3 > matrix.shape[0]:
        return None
    elif j-3 < 0 or j+3 > matrix.shape[1]:
        return None
    return matrix[np.ix_([i-1,i,i+1],[j-1,j,j+1])]

def find_5x5_N(matrix, point):
    i,j = point
    if i-5 < 0 or i+5 > matrix.shape[0]:
        return None
    elif j-5 < 0 or j+5 > matrix.shape[1]:
        return None
    return matrix[np.ix_([i-2,i-1,i,i+1,i+2],[j-2,j-1,j,j+1,j+2])]

def find_half_5x5_N(matrix, point):
    i,j = point
    if i-5 < 0 or i+5 > matrix.shape[0]:
        return None
    elif j-5 < 0 or j+5 > matrix.shape[1]:
        return None
    N = matrix[np.ix_([i-2,i-1,i,i+1,i+2],[j-2,j-1,j,j+1,j+2])]
    N = N.flatten()
    return N[:12]


# concatenates a 3x3 neighborhood and a 5x5 neighborhood
def F_l(point, layer, image_pyramid):
    if l is not 0:
        small = find_3x3_N(image_pyramid[l], point) + find_3x3_N(image_pyramid[l-1], point)
        large = find_5x5_N(image_pyramid[l], point) + find_5x5_N(image_pyramid[l-1], point)
    else:
        small = find_3x3_N(image_pyramid[l], point)
        large = find_5x5_N(image_pyramid[l], point)
    return small.flatten() + large.flatten()

def find_best_match(s, l, q, point, image_pyramids, search_structure):
    # find matches
    p_app = best_approx_match(l, q, search_structure, image_pyramids)
    p_coh = best_coherence_match(s, l, q, point, features, image_pyramids)

    # compute the weighted distance of neighboorhood features with a gaussian kernel
    d_app = np.norm(F_l(p_app, l, image_pyramid[3]) - F_l(q, l, image_pyramid[3]))
    d_coh = np.norm(F_l(p_coh, l, image_pyramid[3]) - F_l(q, l, image_pyramid[3]))
    kappa = 10
    if d_coh < d_app * (1 + kappa * pow(2, (l))):
        return p_coh
    else:
        return p_app

def best_approx_match(l, q, search_structure, image_pyramids):
    p_i = search_structure.kneighbors([q], 1, return_distance=False)
    a_prime = image_pyramids[1][l]
    h,w,c = a_prime
    p = search_structure[p_i]
    point_index = (int(p_i/w), p_i%w)
    p_app = a_prime[point_index[0]][point_index[1]]
    if p == p_app:
        return p_app
    else:
        print('help')

def best_coherence_match(s, l, q, point, features, image_pyramids):
    # also find a way to take out already synthesized as close as possible to 5x5 portions of B' :
    b_prime = image_pyramids[3][l]
    N = find_half_5x5_N(b_prime, point)
    r_star = np.argmin([np.norm(
            F_l((s[point[0][point[1]]] + (q-r)), l, image_pyramid[3]) - 
            F_l(q, l, image_pyramid[3])) for r in N])
    p_coh = s[r_star] + (q - r_star)
    return p_coh

# create image analogy
def get_b_prime(a, a_prime, b):
    images = [a, a_prime, b]

    # find the minimum dimension
    a_h,a_w,a_c = a.shape
    a_prime_h,a_prime_w,a_prime_c = a_prime.shape
    b_h,b_w,b_c = b.shape

    if not a.shape == a_prime.shape:
        print("The images A and A' must be of the same dimensions.")
        return -1

    num_levels = int(math.log(min(a_h,b_h,a_w,b_w),2))

    print("Making image pyramids...")
    # initialize image pyramids for A, A', and B
    image_pyramids = list() # [A_pyramid, A'_pyramid, B pyramid]
    for im in images:
        # reversed because it goes from coarse to fine
        image_pyramids.append(list(reversed(create_pyramid(im, num_levels))))

    print("Computing features...")
    # compute features for A, A', and B
    features = list()
    for pyr in image_pyramids:
        pyr_features = list()
        # A, A', B
        for im in pyr:
            # appends in the form of (3x3 neighborhood features, 5x5 features)
            pyr_features.append(compute_features(im))
        # has the form :
        # [
        #   [features of every image in pyramid A: (level L 3x3, level L 5x5)]], 
        #   [features of every image in pyramid A'],
        #   [features of every image in pyramid B] 
        #      ]
        features.append(pyr_features)
   
    # initialize B' stuff
    a_features = features[0]
    a_prime_features = features[1]
    b_features = features[2]

    b_prime = np.ones((b_features[num_levels][1]).shape)
    b_prime_img_pyr = list()

    print("Creating B'...")
    # find best match at every level
    for l in range(num_levels):
        print("... at level " + str(l))
        # image_pyramids[2] is the pyramid for B
        # image_pyramids[2][l] is the image at level l in the B pyramid
        b_prime_l = np.ones((image_pyramids[2][l]).shape)

        # source stores all the indices of taken pixels in B'
        source_l = np.ones(b_prime_l.shape)

        # initialize search structures for approximate nearest neighbor
        print("... initializing search structure (NearestNeighbors)")
        if l == 0:
            f = a_features[l][1] # 5x5
            search_structure, reshaped_features = make_search_structure(f, l)
        else:
            f = combine_features([a_features[l], a_features[l-1]])
            search_structure, reshaped_features = make_search_structure(f, l)

        image_pyramids.append(b_prime_img_pyr)

        print("... finding best pixel match")
        for i,row in enumerate(b_prime_l):
            for j,q in enumerate(row):
                #s, l, q, point, image_pyramids, search_structure)
                #TODO: TODO: TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! combine features for query point from B
                point, point_index = find_best_match(source_l, l, b[i][j], (i,j), 
                    image_pyramids, search_structure)
                b_prime_l[i][j] = point
                source_l[i][j] = point_index
        b_prime_img_pyr.append(b_prime_l)

        print("----------------------------")

        
    return b_prime_img_pyr[num_levels]


if __name__ is not "__main__":
    a = cv2.imread("imgs/oxbow-mask.png")
    a_prime = cv2.imread("imgs/oxbow.png")
    b = cv2.imread("imgs/oxbow-newmask.png")
    b_prime = get_b_prime(a, a_prime, b)


