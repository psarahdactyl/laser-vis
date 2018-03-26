import cv2
import numpy as np

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

    cv2.imwrite('components.png', labeled_img)

    nodes = dict()
    for i in range(num_labels):
        nodes[i] = labeled_img[label_hue==i]

    output = (nodes,labels,labeled_img)

    return output


def organize_components(nodes, labels, labeled_img):
    graph = dict()
    graph[0] = 0
    # graph will have form
    # graph[level number] : {comp0, comp1, comp2, ...}

    label_nums = list(nodes.keys())
    
    background_mask = np.uint8(labels==0)
    for i in label_nums:
        print(i)

        mask_i = np.uint8(labels==label_nums[i])

        #mask_iplus1 = np.uint8(labels==label_nums[i+1])
        new_mask = background_mask+mask_i
        output = cv2.connectedComponentsWithStats(new_mask, 8, cv2.CV_32S)

        print(output[0])
        if output[0] < 3: #belongs in level 1
            graph[1] = mask_i
        else:
            ls = [l for l in label_nums if l not in graph.keys()]

    print(graph)

def dfs(graph, start):
    visited, stack = set(), [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited


if __name__ == '__main__':
    # Read the image you want connected components of
    img = cv2.imread('a.png')
    output = get_components(img)
    print('components got')
    nodes, labels, labeled_img = get_labeled_img(output)
    print('labels got')
    organize_components(nodes, labels, labeled_img)
    print('stuff organized')
