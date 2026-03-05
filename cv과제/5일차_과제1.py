import cv2
import numpy as np

# 검은 배경에 흰색 원(도넛) 그리기
mask = np.zeros((400,400), dtype = np.uint8) #400x400 크기의 검은색 이미지 생성
# dtype=np.uint8: 데이터 타입을 0~255 사이의 정수로 지정 0 검은색 -255 흰색  중간값 회색 

#cv2.circle 원 그리는 함수
cv2.circle(mask,(200,200),100,255,-1)
# (200, 200): 원의 중심 좌표
#   └─ (x, y) = (가로 200번째 픽셀, 세로 200번째 픽셀)
#   └─ 400x400 이미지의 정중앙
# - 100: 원의 반지름 (중심에서 100픽셀 떨어진 거리)
# - 255: 원의 색상 (255 = 흰색)
# - -1: 채우기 옵션
#   └─ -1 = 내부를 완전히 채움 (●)
#   └─ 양수(예: 2) = 테두리만 그림, 숫자는 두께 (○)
print('✅ ⚪ 바깥원 그리기 완료!')
# 작은 원 그리기

# 파라미터:
# - (200, 200): 첫 번째 원과 같은 중심
# - 50: 반지름 50 (첫 번째 원의 반지름 100보다 작음)
# - 0: 검은색 (0 = 검은색)
# - -1: 내부를 채움

cv2.circle(mask, (200, 200), 50, 0, -1)
print('✅ ⚫ 안쪽원 그리기 완료!')

# 배경에 랜덤 노이즈(흰색 점) 추가하기
# np.random.rand(400, 400): 0~1 사이의 랜덤 실수로 채워진 400x400 배열
random_values = np.random.rand(400, 400)

# 4-2. 랜덤값을 True/False로 변환
# > 0.99: 0.99보다 큰 값만 True (약 1%만 True)
noise_mask = random_values > 0.99

# 4-3. True/False를 0/1로 변환
# .astype(np.uint8): True → 1, False → 0
noise_binary = noise_mask.astype(np.uint8)

# 4-4. 0/1을 0/255로 변환
# * 255: 1은 255로, 0은 0으로
noise_white = noise_binary * 255

# 4-5. 기존 이미지에 노이즈 추가
# cv2.bitwise_or(): OR 연산 (둘 중 하나라도 흰색이면 흰색)
# 
# OR 연산 원리:
# - 0 OR 0 = 0 (검은색 + 검은색 = 검은색)
# - 0 OR 255 = 255 (검은색 + 흰색 = 흰색)
# - 255 OR 0 = 255 (흰색 + 검은색 = 흰색)
# - 255 OR 255 = 255 (흰색 + 흰색 = 흰색)
mask = cv2.bitwise_or(mask, noise_white)

# 5. 도넛 내부에 랜덤 구멍(검은색 점) 추가하기
# 5-1. 랜덤 구멍 생성 (99%는 유지, 1%만 구멍)
# > 0.01: 0.01보다 큰 값만 True (약 99%)
hole_mask = np.random.rand(400, 400) > 0.01

# 5-2. True/False를 0/255로 변환
# True → 1 → 255 (유지)
# False → 0 → 0 (구멍)
hole_binary = hole_mask.astype(np.uint8) * 255

# 5-3. 기존 이미지에 구멍 뚫기
# cv2.bitwise_and(): AND 연산 (둘 다 흰색이어야 흰색)
#
# AND 연산 원리:
# - 0 AND 0 = 0 (검은색 + 검은색 = 검은색)
# - 0 AND 255 = 0 (검은색 + 흰색 = 검은색) ← 구멍이 뚫림!
# - 255 AND 0 = 0 (흰색 + 검은색 = 검은색) ← 구멍이 뚫림!
# - 255 AND 255 = 255 (흰색 + 흰색 = 흰색)
mask = cv2.bitwise_and(mask, hole_binary)

kernel = np.ones((3, 3), np.uint8)

opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)

# cv2.imshow(): 이미지를 화면에 표시하는 함수
# 
# 파라미터:
# - '창 제목': 창의 제목 (문자열)
# - 이미지: 표시할 이미지 배열

# 원본 이미지 (노이즈와 구멍이 있는 상태)
cv2.imshow('Dirty Mask', mask)

# Step 1 결과 (배경 노이즈 제거됨)
cv2.imshow('Cleaned Step 1 (Opening)', opening)

# Step 2 최종 결과 (구멍까지 채워진 깨끗한 이미지)
cv2.imshow('Final Result (Closing)', closing)

cv2.waitKey(0)