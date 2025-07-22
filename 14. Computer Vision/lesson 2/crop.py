import os
import cv2

img = cv2.imread(os.path.join(".", "brain.jpeg"))
print(img.shape)

brain  = img[ 170:340, 256:512]
cv2.imshow("Akili Kijana", img)
cv2.waitKey(0)