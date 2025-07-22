import cv2
import os

#Read the Image
img = cv2.imread(os.path.join(".","write.jpg"))
img_2 = cv2.resize(img, (500, 500))
print(img_2.shape)

cv2.imshow("My Image", img_2)


cv2.waitKey(0)