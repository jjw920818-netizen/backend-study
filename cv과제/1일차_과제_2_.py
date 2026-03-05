import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

img = cv2.imread('dumbo.jpg')

img_h, img_w = img.shape[:2] 
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
pil_img = Image.fromarray(img_rgb)

draw = ImageDraw.Draw(pil_img)

try:
    font = ImageFont.truetype('/System/Library/Fonts/AppleSDGothicNeo.ttc', 25)
except:
    print("⚠️ 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    font = ImageFont.load_default()

text = 'Hello, my name is Jeong joowon'


bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x_position = (img_w - text_width) // 2
y_position = img_h - text_height - 30


padding = 10
draw.rectangle(
    [(x_position - padding, y_position - padding),
     (x_position + text_width + padding, y_position + text_height + padding)],
    fill=(255, 255, 255)
)


draw.text((x_position, y_position), text, font=font, fill=(255, 0, 0))

result = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

cv2.imshow('My Introduction', result)
cv2.waitKey(0)
cv2.destroyAllWindows()