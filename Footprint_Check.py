from skimage.metrics import structural_similarity
import cv2
import numpy as np
# np.set_printoptions(threshold=np.inf)

before = cv2.imread("Footprints/Footprints0.jpg")
after = cv2.imread("Footprints/Footprints1.jpg")

""" 
image_size will store image.shape 
which is a 3obj tuple (dimension_y, dimension_x, RBG)
"""
print(before)
print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
print(after)
before_size = before.shape
after_size = after.shape
# To see te dimension of before_size
print("Before_size = " + str(before_size))
print("After_size = " + str(after_size))  # To see te dimension of after_size

# create after with grids
after_with_grid = after.copy()
height, width, channels = after_with_grid.shape

for i in range(0, width, 30):
    cv2.line(after_with_grid, (i, 0), (i, height), (0, 0, 0), 1)
for i in range(0, height, 30):
    cv2.line(after_with_grid, (0, i), (width, i), (0, 0, 0), 1)

# Convert images to grayscale
before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

# Compute SSIM between two images
(score, diff) = structural_similarity(before_gray, after_gray, full=True)
print("Image similarity = ", score)

# The diff image contains the actual image differences between the two images
# and is represented as a floating point data type in the range [0,1]
# so we must convert the array to 8-bit unsigned integers in the range
# [0,255] before we can use it with OpenCV
diff = (diff * 255).astype("uint8")

# Threshold the difference image, followed by finding contours to
# obtain the regions of the two input images that differ
thresh = cv2.threshold(
    diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
contours = cv2.findContours(
    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]

mask1 = np.zeros(before.shape, dtype="uint8")
filled_after = after.copy()

bouding_boxes = []
index = 1

for c in contours:
    area = cv2.contourArea(c)
    if area > 50:

        x, y, w, h = cv2.boundingRect(c)
        bouding_boxes.append((x, y, w, h))
        cv2.rectangle(before, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            before,
            "point" + str(index),
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )  # labels
        cv2.rectangle(after, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(
            after,
            "point" + str(index),
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )  # labels
        cv2.drawContours(mask1, [c], 0, (0, 255, 0), -1)
        cv2.drawContours(filled_after, [c], 0, (0, 255, 0), -1)
        index += 1


print("box_count = " + str(len(bouding_boxes)) + " \n >> " + str(bouding_boxes))
cv2.imshow("before", before)
cv2.imshow("after", after)
cv2.imshow("diff", diff)
cv2.imshow("mask1", mask1)
cv2.imshow("filled after", filled_after)
cv2.imshow("after with grid", after_with_grid)
cv2.waitKey(0)


"""
 Impact assessment part / pseudo ignore
list_1 = [(x,y,w,h), (obj2.1)]
list_2 = [(name, shape_size, bla), (obj_2.2)]

>>list_3 = [((x,y,w,h), (name, shape_size, bla)), (obj2.12)]

for i in range(len(list_1)):
    list_3.append((list_1[i], list2[i]))

print(list_3)

list_1 = bouding_boxes

list_2 = []
"""
