#!/usr/bin/env python

import cv2
import matplotlib.pyplot as plt
import numpy as np
import math

def create_normal_map(img):
	# make sure image is grayscale to create normal map
    grayscale_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # find gradients in x directions and y directions
    sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=-1) #TODO: find best kernel size for texturing
    sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=-1)

    h,w,c = img.shape
    # go through each pixel in the image
    for i,row in enumerate(h):
    	for j,pixel in enumerate(w):
    		gx = np.array([0,1,sobelx[i][j]])
    		gy = np.array([1,0,sobely[i][j]])


 '''	
Assuming that the image you want to extract the normal map is in grayscale, 
For every pixel in the image, you have to construct 2 vectors (wich z coordinates are the y difference of the image and the x differences of the image respectively), and do the cross product to get the normal at that point, then you store the normal coded in the [0, 255] range in an output image

The following pseudo-code explains it better 


for y = 1 to image_height - 1 do
   for x = 1 to image_width - 1 do

      # Construct both vectors with the surface difference at this point
      # (vec3 is a vector in 3d space) 

      # Observe that the z coordinate holds the x and y perturbation of the 
      # image, you can do this because you are assuming that the image actually 
      # represents a "surface", so, the x and y vector are altered in z due to 
      # to the bumpness of the surface at that point
  
      vec3 vx <- vec3(0, 1, image[x - 1][y] - image[x + 1][y])

      vec3 vy <- vec3(1, 0, image[x][y - 1] - image[x][y + 1])
      
      # Given vx and vy, you have both the x and y basis of the coordenate system 
      # tangent to the "surface" at the point, to get the normal, calculate 
      # the cross product of vx and vy 
      
      vec3 normal <- cross_product(vx, vy)

      # dont forget to normalize the normal vector
      normal <- normalize(normal)

      # Now, the tricky part, store the normal as a RGB pixel in the output image
      # to do that, remember that the x, y and z coordenates of the vector lies
      # in range [-1, 1] (because is a normalized vector), then you have to
      # take then to the range [0,255], so we first take then from [-1, 1]
      # to [0, 1]
      #
      #   -1 is equivalent to 0
      #    0 would be equivalent to 0.5
      #    1 would be equivalent to 1
      #
      # with this info, we deduce the following formula:
      #   pixel_component <- (coordenate + 1) / 2 

      # Multiply this by 255 and we are done for

      r <- ((normal.x + 1.0) / 2.0) * 255   
      g <- ((normal.y + 1.0) / 2.0) * 255   
      b <- ((normal.z + 1.0) / 2.0) * 255
      
      # Clamp the pixel components if neccesary 

      # Store the pixel in the output image 
      output_image[x][y] <- construct_pixel(r, g, b)    
   end for
end for
'''