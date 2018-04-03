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


def fill_components(connected_comps):
    output = connected_comps
    #graph = dict()
    #label_nums = list(nodes.keys())
    num_labels = output[0]
    labels = output[1]
    stats = output[2]
    # Sort stats by leftmost components
    # stats = stats[stats[:, 0].argsort()]
    print(stats)

    # Map component labels to hue val
    label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    nodes = dict()
    for i in range(num_labels):
        nodes[i] = labeled_img[label_hue==i]

    label_nums = list(nodes.keys())

    for i,label in enumerate(label_nums):
        left_x = stats[i, cv2.CC_STAT_LEFT]
        top_y = stats[i, cv2.CC_STAT_TOP]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]

        topleft_x = min(filter(lambda x: x > 0, [left_x+width, left_x, left_x-width]))
        topleft_y = min(filter(lambda x: x > 0, [top_y+height, top_y, top_y-height]))
        print(labeled_img.shape)
        print(topleft_x, topleft_y)

        mask_i = np.uint8(labels==label_nums[i])
        mask_i = np.pad(mask_i, (1,1), 'constant', constant_values=(0))

        cv2.floodFill(labeled_img, (topleft_x-1, topleft_y-1), (255,255,255), flags=8|cv2.FLOODFILL_FIXED_RANGE)
        cv2.imwrite('help'+str(i)+'.png', labeled_img)


def make_levels(label_nums, labels, graph):
    level_num = len(graph.keys())
    mask_0 = np.uint8(labels==0)
    background_mask = sum(graph[l] for l in graph.keys())
    #background_mask = graph[level_num-1]
    
    graph[level_num] = np.zeros_like(mask_0)

    for i,label in enumerate(label_nums):
        mask_i = np.uint8(labels==label_nums[i])

        kernel = np.ones((3,3),np.uint8)
        new_mask = background_mask+mask_i-mask_0
        new_mask = cv2.dilate(new_mask, kernel, iterations=2)


        label_hue = np.uint8(179*new_mask/np.max(new_mask))
        blank_ch = 255*np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
        labeled_img[label_hue==0] = 0
        #cv2.imshow('helop', labeled_img)
        #cv2.waitKey(0)

        ret, thresh = cv2.threshold(new_mask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        output = cv2.connectedComponentsWithStats(thresh, 8, cv2.CV_32S)

        #print(output[0])
        if output[0] < 3: #belongs in level
            graph[level_num] += mask_i
            label_nums.remove(label)

def organize_components(nodes, labels, labeled_img, largest_label):
    #background_mask = np.uint8(labels==largest_label)

    graph = dict()
    graph[largest_label] = background_mask
    #background_mask = np.uint8(labels==0)
    graph[largest_label] = background_mask
    # graph will have form
    # { level number : comp0 + comp1 + comp2 + ...] }

    label_nums = list(nodes.keys())
    label_nums.remove(largest_label)

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

def find_nearest_white(img, target):
    nonzero = cv2.findNonZero(img)
    if nonzero is not None:
        distances = np.sqrt((nonzero[:,:,0] - target[0]) ** 2 + (nonzero[:,:,1] - target[1]) ** 2)
        nearest_index = np.argmin(distances)
        return tuple(nonzero[nearest_index][0])
    else:
        return None

def test_flood_fill(img):
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_thresh = cv2.threshold(img_bw,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    cv2.imwrite('step.png', img_thresh)

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
            cv2.imwrite('step'+str(i)+'.png', img_thresh)
            #cv2.imshow('new', img_thresh)
            #cv2.imshow('old', old_thresh)
            #cv2.waitKey(0)
            component = cv2.absdiff(img_thresh,old_thresh)
            cv2.imwrite('comp'+str(i)+'.png', component)
            components.append(component)
            i += 1

    print('out of loop')
    return components


if __name__ == '__main__':
    # Read the image you want connected components of
    img = cv2.imread('a1.png')
    #output = get_components(img)
    #print('connected components got')
    #nodes, labels, labeled_img, largest_label = get_labeled_img(output)
    #print('labels got')
    #components = organize_components(nodes, labels, labeled_img, largest_label)
    #print('levels got')
    #combine_components(components)
    #print('combined conmponents got')
    #fill_components(output)
    components = test_flood_fill(img)
    combine_components(components)