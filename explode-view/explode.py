import cv2
import numpy as np

# Read the image you want connected components of
src = cv2.imread('a.png')

cv2.imshow('image', src)
cv2.waitKey(0)
cv2.destroyAllWindows()

src_bw = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(src_bw,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

im, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

red = (0,0,255)
line_thickness = 1
fill_shape = -1
'''
for c,cont in enumerate(contours):
    mask = np.ones(src.shape,np.uint8)
    cv2.drawContours(mask, [cont], 0, 255, fill_shape)
    #cv2.drawContours(src, contours, c, red, line_thickness)
    cv2.imwrite('contour_'+str(c)+'.png', mask)
    print(c)
'''
connectivity = 8

np.pad(src_bw, 3, mode='constant')
cv2.imshow('image', src_bw)
cv2.waitKey(0)
cv2.destroyAllWindows()

ret, thresh = cv2.threshold(src_bw,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)

# The first cell is the number of labels
num_labels = output[0]

# The second cell is the label matrix
labels = output[1]

# The third cell is the stat matrix
stats = output[2]

# The fourth cell is the centroid matrix
centroids = output[3]

graph = dict()

# Map component labels to hue val
label_hue = np.uint8(179*labels/np.max(labels))
blank_ch = 255*np.ones_like(label_hue)
labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

print(labeled_img)


h,w,c = labeled_img.shape
for i in range(h-1):
    for j in range(w-1):
        label = labeled_img[i][j]
        #print(label)

# cvt to BGR for display
labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

# set bg label to black
labeled_img[label_hue==0] = 255

cv2.imwrite('components.png', labeled_img)

cv2.imshow('labeled.png', labeled_img)
cv2.waitKey()
