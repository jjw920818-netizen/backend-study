import cv2
import numpy as np

SIZE = 500 # 500x500 크기의 3채널(컬러) 이미지 생성
SKY_BLUE = (255, 200, 100)
img = np.full((SIZE, SIZE, 3), SKY_BLUE, dtype = np.uint8)
#하늘색 배경 이미지

text = "OpenCV Text Practice"
font = cv2.FONT_HERSHEY_TRIPLEX
font_scale = 1.2
thickness = 2
color = (0,0, 255)

(text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

center_x = (SIZE - text_w) // 2
center_y = text_h + 20

cv2.putText(img, text, (center_x, center_y), font, font_scale, color, thickness)

cv2.imshow('Sky Blue Background', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
