import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

print("📚 로딩 완료!")

#이미지 파일 찾기
current_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(current_dir, "images")

#이미지 자동 찾기
if os.path.exists(images_dir):
    image_files = [f for f in os.listdir(images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    if image_files:
        image_path = os.path.join(images_dir, image_files[0])
        print(f"✅ 이미지 발견: {image_files[0]}")
    else:
        print("❌ images 폴더에 이미지가 없습니다!")
        exit()
else:
    print("❌ images 폴더가 없습니다!")
    exit()

#이미지 읽기
img = cv2.imread(image_path) 
height, width, channels = img.shape 

#채널분리
ori_b, ori_g, ori_r = cv2.split(img)
print('✅채널분리 완료')
print(f"   Blue:  {ori_b.shape}")
print(f"   Green: {ori_g.shape}")
print(f"   Red:   {ori_r.shape}")

#수동 흑백 이미지 만들기
#평균값 계산
gray = ((ori_b.astype(np.uint16) + ori_g + ori_r) / 3).astype(np.uint8)

#B,G,R 모든 채널에 똑같이 넣어 재결합
gray_color = cv2.merge([gray, gray, gray])
print('✅재결합 완료')

plt.figure(figsize=(12,6))

plt.subplot(1,2,1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Original (Color)")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(gray_color, cv2.COLOR_BGR2RGB))
plt.title("Manual Grayscale")
plt.axis('off')
         
plt.show()
