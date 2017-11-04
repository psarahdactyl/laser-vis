#!/usr/bin/env python

import cv2
import numpy as np
from matplotlib import pyplot as plt
import img2pdf

def find_factors(image_size, num_of_factors):
	# This function takes a number finds the first n factors
	factors = list()
	for i in range(2, image_size + 1):
		if image_size % i == 0:
			factors.append(i)

	return factors[:num_of_factors]

# read in image
src_img = cv2.imread('sized.png')

# make it grayscale and threshold it
gray_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)

# initialize colors
pure_blue = np.array([0,0,255])
pure_white = np.array([255,255,255])
pure_blue_opposite = np.array([255,255,0])
pure_black = np.array([0,0,0])

# initialize result
h,w,c = src_img.shape
result = np.empty((h,w,c), np.uint8)
result[:] = pure_white

num_of_levels = 3
image_factors = find_factors(h, num_of_levels)
#print(image_factors)

# for every level of gray threshold that i want
for i in range(1,(num_of_levels+1)):
	# make the stripe pattern
	pattern = np.zeros((h,w,c), np.uint8)
	#pattern[:] = pure_blue_opposite
	#pattern[::i*5] = pure_black

	pattern[:] = pure_black
	'''
	if i % 2 == 0:
		pattern[::image_factors[0]] = pure_blue_opposite
		#pattern[::image_factors[i-1]] = pure_blue_opposite
	else:
		pattern[:, ::image_factors[0]] = pure_blue_opposite
		#pattern[:, ::image_factors[i-1]] = pure_blue_opposite
	'''
	pattern[::image_factors[1]] = pure_blue_opposite

	lower_gray_level = (i*40) % 255
	ret, thresh = cv2.threshold(gray_img,lower_gray_level,255,0)

	# find contours
	contour_img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, \
		cv2.CHAIN_APPROX_SIMPLE)

	contoured_imgs = \
		[cv2.drawContours(contour_img, contours, i, (0,255,0), 3) for i in range(len(contours))]

	for n,c_n in enumerate(contoured_imgs):
		if n == 0:
			mask_inv = cv2.bitwise_not(c_n)
			stripe_contour =  cv2.bitwise_and(pattern, pattern, mask = mask_inv)
			stripe_contour = cv2.bitwise_not(stripe_contour)
			
	result = cv2.bitwise_and(result, stripe_contour)

	#plt.imshow(result)
	#plt.show()

	cv2.imwrite(str(i)+'.png', result)

pdf_img = cv2.imread(str(num_of_levels)+'.png')
pdf_img = cv2.cvtColor(pdf_img, cv2.COLOR_BGR2RGB)
cv2.imwrite('hatched.png', pdf_img)

with open('hatched.pdf', 'wb') as f:
	f.write(img2pdf.convert('hatched.png'))
