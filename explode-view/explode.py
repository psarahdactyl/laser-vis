import cv2
import numpy as np
from collections import defaultdict

def get_components(src):
    src_bw = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    connectivity = 8

    ret, thresh = cv2.threshold(src_bw,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)

    return output


def get_labeled_img(connected_comps):
    output = connected_comps

    # The first cell is the number of labels
    num_labels = output[0]

    # The second cell is the label matrix
    labels = output[1]

    # The third cell is the stat matrix
    stats = output[2]

    # The fourth cell is the centroid matrix
    centroids = output[3]

    # Map component labels to hue val
    label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    # set bg label to black
    labeled_img[label_hue==0] = 255

    #kernel = np.ones((3,3),np.uint8)
    #labeled_img = cv2.morphologyEx(labeled_img, cv2.MORPH_OPEN, kernel)
    #labeled_img = cv2.morphologyEx(labeled_img, cv2.MORPH_OPEN, kernel)

    cv2.imwrite('components.png', labeled_img)

    nodes = dict()
    for i in range(num_labels):
        nodes[i] = labeled_img[label_hue==i]

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    #print(largest_label)

    ret = (nodes,labels,labeled_img,largest_label)

    return ret


def combine_components(components):
    even = np.zeros_like(components[0])
    odd = np.zeros_like(components[0])
    for i,comp in enumerate(components):
        if i % 2 == 0:
            even += comp
        else:
            odd += comp

    cv2.imwrite('odd_components.png', odd)
    cv2.imwrite('even_components.png', even)


def find_nearest_white(img, target):
    nonzero = cv2.findNonZero(img)
    if nonzero is not None:
        distances = np.sqrt((nonzero[:,:,0] - target[0]) ** 2 + (nonzero[:,:,1] - target[1]) ** 2)
        nearest_index = np.argmin(distances)
        return tuple(nonzero[nearest_index][0])
    else:
        return None
        

def flood_fill(img):
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_thresh = cv2.threshold(img_bw,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    #cv2.imwrite('step.png', img_thresh)

    h,w,c = img.shape

    components = list()
    #components.append(img_thresh)

    i = 0
    target = (0,0)
    mask = np.zeros((h+2, w+2), np.uint8)

    while not(np.count_nonzero(img_thresh) == 0):
        if target:
            old_thresh = img_thresh.copy()
            cv2.floodFill(img_thresh, mask, target, (0,0,0))#, flags=8|cv2.FLOODFILL_FIXED_RANGE)

            if target[0] < w/2 and target[1] < h/2:
                new_target = (0,0)
            elif target[0] < w/2 and target[1] > h/2:
                new_target = (0,h)
            elif target[0] > w/2 and target[1] < h/2:
                new_target = (w,0)
            else:
                new_target = (w,h)

            target = find_nearest_white(img_thresh, new_target)
            #cv2.imwrite('step'+str(i)+'.png', img_thresh)

            #cv2.imshow('new', img_thresh)
            #cv2.imshow('old', old_thresh)
            #cv2.waitKey(0)

            component = cv2.absdiff(img_thresh,old_thresh)
            #cv2.imwrite('comp'+str(i)+'.png', component)
            components.append(component)
            i += 1

    print('out of loop')
    return components


if __name__ == '__main__':
    # Read the image you want connected components of
    img = cv2.imread('a.png')
    #output = get_components(img)
    #nodes, labels, labeled_img, largest_label = get_labeled_img(output)

    components = flood_fill(img)
    combine_components(components)
