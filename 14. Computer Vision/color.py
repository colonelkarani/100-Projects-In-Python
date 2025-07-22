import cv2 as cv
img = cv.imread("copy.png", cv.IMREAD_COLOR)

cv.imwrite("copy2.png", img)