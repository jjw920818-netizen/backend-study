import cv2
import numpy as np

img = np.zeros((500, 500, 3), dtype = np.uint8)

pt1 = (250, 50)   # 상단
pt2 = (100, 400)  # 좌측 하단
pt3 = (400, 400)  # 우측 하단

# 삼각형의 세 변을 선으로 그리기
cv2.line(img, pt1, pt2, (0, 255, 0), 5)  # 상단 -> 좌측 하단
cv2.line(img, pt2, pt3, (0, 255, 0), 5)  # 좌측 하단 -> 우측 하단
cv2.line(img, pt3, pt1, (0, 255, 0), 5)  # 우측 하단 -> 상단

# 트리 장식 (원) 그리기 - 노란색 (BGR: 0, 255, 255)
cv2.circle(img, (250, 100), 8, (0, 255, 255), -1)  # 상단 중앙
cv2.circle(img, (200, 180), 8, (0, 255, 255), -1)  # 좌측 상단
cv2.circle(img, (300, 180), 8, (0, 255, 255), -1)  # 우측 상단
cv2.circle(img, (170, 280), 8, (0, 255, 255), -1)  # 좌측 중간
cv2.circle(img, (250, 250), 8, (0, 255, 255), -1)  # 중앙
cv2.circle(img, (330, 280), 8, (0, 255, 255), -1)  # 우측 중간
cv2.circle(img, (200, 350), 8, (0, 255, 255), -1)  # 좌측 하단
cv2.circle(img, (300, 350), 8, (0, 255, 255), -1)  # 우측 하단

# 이미지 출력
cv2.imshow('Christmas Tree', img)
cv2.waitKey(0)
cv2.destroyAllWindows()