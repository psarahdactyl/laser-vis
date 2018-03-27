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

    ret = (nodes,labels,labeled_img)

    return ret

def make_levels(label_nums, labels, graph):
    level_num = len(graph.keys())
    background_mask = sum(graph[l] for l in graph.keys())
    mask_0 = np.uint8(labels==0)
    graph[level_num] = np.zeros_like(mask_0)

    for i,label in enumerate(label_nums):
        #print(i)

        mask_i = np.uint8(labels==label_nums[i])
        
        new_mask = background_mask+mask_i-mask_0

        kernel = np.ones((3,3),np.uint8)
        new_mask = cv2.dilate(new_mask, kernel, iterations=2)

        ret, thresh = cv2.threshold(new_mask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        output = cv2.connectedComponentsWithStats(thresh, 8, cv2.CV_32S)

        #print(output[0])
        if output[0] < 3: #belongs in level
            graph[level_num] += mask_i
            label_nums.remove(label)

def organize_components(nodes, labels, labeled_img):
    background_mask = np.uint8(labels==0)

    graph = dict()
    graph[0] = background_mask
    # graph will have form
    # { level number : comp0 + comp1 + comp2 + ...] }

    label_nums = list(nodes.keys())
    label_nums.remove(0)

    while label_nums:
        make_levels(label_nums, labels, graph)

    components = list()
    for level in graph.keys(): 
        #print(level)     
        img = graph[level]

        label_hue = np.uint8(179*img/np.max(img))
        blank_ch = 255*np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

        labeled_img[label_hue==0] = 0
        if not(np.count_nonzero(labeled_img) == 0) and not(level==0):
            #cv2.imwrite('components'+str(level)+'.png', labeled_img)
            components.append(labeled_img)

    return components


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


if __name__ == '__main__':
    # Read the image you want connected components of
    img = cv2.imread('a.png')
    output = get_components(img)
    print('connected components got')
    nodes, labels, labeled_img = get_labeled_img(output)
    print('labels got')
    components = organize_components(nodes, labels, labeled_img)
    print('levels got')
    combine_components(components)
    print('combined conmponents got')
