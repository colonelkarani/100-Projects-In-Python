import cv2
import os

# Read Image
image_path = "ex.png"

img = cv2.imread(image_path)

# Write Image

cv2.imwrite("write.jpg", img)

# Visualize image

cv2.imshow("frame", img)
cv2.waitKey(0)