import cv2
import numpy as np

# Read the image you want connected components of
src = cv2.imread('a.png')

cv2.imshow('image', src)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Threshold it so it becomes binary
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
inv = cv2.bitwise_not(gray)
print(gray.shape)
kernel = np.ones((6,6),np.uint8)
new = cv2.dilate(inv, kernel, iterations = 1)

cv2.imshow('image', new)
cv2.waitKey(0)
cv2.destroyAllWindows()

#ret, thresh = cv2.threshold(new,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

im, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

red = (0,0,255)
line_thickness = 1
fill_shape = -1
for c,cont in enumerate(contours):
    mask = np.ones(src.shape,np.uint8)
    cv2.drawContours(mask, [cont], 0, 255, fill_shape)
    #cv2.drawContours(src, contours, c, red, line_thickness)
    #cv2.imwrite('contour_'+str(c)+'.png', mask)
    print(c)

'''
connectivity = 4

output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)

# The first cell is the number of labels
num_labels = output[0]

# The second cell is the label matrix
labels = output[1]

cv2.imshow('image', labels)
cv2.waitKey(0)
cv2.destroyAllWindows()

# The third cell is the stat matrix
stats = output[2]

# The fourth cell is the centroid matrix
centroids = output[3]
'''