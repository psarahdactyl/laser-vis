#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
import math
from sklearn.neighbors import LSHForest
from sklearn.neighbors import NearestNeighbors

'''
Based on the paper [Image Analogies, 2001] by Hertzmann et al.
Implemented by Sarah Kushner October 2017.

'''


def create_pyramid(image):
    # generate Gaussian pyramid for A
    G = image.copy()
    gp = [G]
    h,w,c = image.shape
    for i in range(int(math.log(min(h,w),2))):
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
    f = image
    # append luminance
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV) 
    f = np.concatenate((f,yuv), axis=2)
    return f[...,0:4]
    
def make_search_structure(f):
    #lshf = LSHForest(n_estimators=20, n_candidates=200, n_neighbors=1).fit(f)
    h,w,c = f.shape
    f = f.reshape(h*w, c)
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='brute').fit(f)
    return nbrs, f

def find_3x3_N(matrix, point):
    i,j = point
    return matrix[np.ix_([i-1,i,i+1],[j-1,j,j+1])]

def find_5x5_N(matrix, point):
    i,j = point
    return matrix[np.ix_([i-2,i-1,i,i+1,i+2],[j-2,j-1,j,j+1,j+2])]

# concatenates a 3x3 neighborhood and a 5x5 neighborhood
def F_l(matrix, point):
    small = find_3x3_N(matrix, point)
    large = find_5x5_N(matrix, point)
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
    # initialize image pyramids for A, A', and B
    a_img_pyr = create_pyramid(a)
    a_prime_img_pyr = create_pyramid(a_prime)
    b_img_pyr = create_pyramid(b)
    pyramids = (a_img_pyr, b_img_pyr, a_prime_img_pyr)


    # find best match
    b_prime = np.ones(b.shape)
    b_prime_img_pyr = list()

    num_levels = min(len(a_img_pyr), len(b_img_pyr), len(a_prime_img_pyr))
    for l in reversed(range(num_levels)):
        b_prime_l = np.ones(b_img_pyr[l].shape)
        source_l = np.ones(b_prime_l.shape)
        # compute features for A, A', and B
        a_features = [compute_features(a) for a in a_img_pyr]
        a_prime_features = [compute_features(a_prime) for a_prime in a_prime_img_pyr]
        b_features = [compute_features(b) for b in b_img_pyr]
        #print(a_features)
        features = (a_features, b_features, a_prime_features)

        # initialize search structures for approximate nearest neighbor
        a_structure, reshaped_a = make_search_structure(a_features)
        a_prime_structure, reshaped_a_prime = make_search_structure(a_prime_features)
        b_structure, reshaped_b = make_search_structure(b_features)
        search_structures = ((a_structure, reshaped_a), (b_structure, reshaped_a_prime), (a_prime_structure, reshaped_b))
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


