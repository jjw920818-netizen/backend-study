import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

print("📚 로딩완료!")

#이미지 파일 찾기
current_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(current_dir, "images")

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
    print("❌ images 폴더가 없습니다! 폴더를 생성하고 이미지를 넣어주세요.")
    exit()

img = cv2.imread(image_path)
if img is None:
    print("❌ 이미지를 읽을 수 없습니다.")
    exit()

ori_b, ori_g, ori_r = cv2.split(img)
gray = ((ori_b.astype(np.uint16) + ori_g + ori_r) / 3).astype(np.uint8)

color_splash = cv2.merge([gray, gray, ori_r])

swap_rgb = cv2.merge([ori_r, ori_g, ori_b])

swap_grb = cv2.merge([ori_g, ori_r, ori_b])

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1); plt.title("Original"); plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.subplot(1, 3, 2); plt.title("Prob 2: Color Splash"); plt.imshow(cv2.cvtColor(color_splash, cv2.COLOR_BGR2RGB))
plt.subplot(1, 3, 3); plt.title("Prob 3: Swap (R,G,B)"); plt.imshow(cv2.cvtColor(swap_rgb, cv2.COLOR_BGR2RGB))

plt.show()