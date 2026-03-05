#cnn 과 opencv
#cnn  파이썬 pillow 라는 라이브러리를 통해서 이미지를 불러와서 예측을 할 수 있다
# 이거보다는 opncv로 이미지 하나를 불러와서 cnn에서 예측가능

from ntpath import exists
import cv2
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import requests



# 1. 모델 준비 (예시로 이미 학습된 ResNet18 모델 사용)
# 처음 실행 시 모델 파일을 다운로드하느라 시간이 조금 걸릴 수 있습니다.
model = models.resnet18(pretrained=True)
model.eval()  # 추론 모드로 전환

# 2. OpenCV를 사용하여 이미지 로드
# 'test.jpg' 대신 실제 본인의 이미지 경로를 넣으세요.
image_path = './images/cat2.jpg'
img = cv2.imread(image_path)

if img is None:
    print("이미지를 찾을 수 없습니다. 경로를 확인하세요.")
    exit()

# 3. 이미지 전처리 (OpenCV -> PyTorch)
# A. BGR을 RGB로 변환 (OpenCV는 기본이 BGR임)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# B. 리사이즈 및 텐서 변환 (모델이 기대하는 224x224 크기로)
preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

input_tensor = preprocess(img_rgb)

# C. 배치 차원 추가 (1, 3, 224, 224) - 모델은 여러 장을 한꺼번에 받는 구조이기 때문
input_batch = input_tensor.unsqueeze(0)

# 4. CNN 모델에 입력 및 결과 확인
with torch.no_grad():
    output = model(input_batch)

# 결과 출력 (1000개의 클래스 중 가장 높은 점수의 인덱스)
_, predicted_idx = torch.max(output, 1)
print(f"예측된 클래스 인덱스: {predicted_idx.item()}")

# 1. 1000개의 클래스 이름이 담긴 텍스트 파일 가져오기
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL).text.splitlines()

# 2. 인덱스를 이름으로 변환
predicted_name = labels[predicted_idx.item()]
print(f"최종 예측 결과: {predicted_name} (인덱스: {predicted_idx.item()})")



# 5. OpenCV로 원본 이미지 화면에 띄우기
cv2.imshow('Input Image', img)

import gradio as gr

def predict_image(img):
    # 여기에 사용자님이 작성하신 3번(전처리)과 4번(모델 입력) 로직을 넣으세요.
    # 최종 결과 predicted_name을 반환하면 끝!
    return predicted_name

# gr.Interface(fn=predict_image, inputs="image", outputs="text").launch()
# 'q' 키를 누르거나 창을 닫을 때까지 대기
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty('Input Image', cv2.WND_PROP_VISIBLE) < 1:
        break
        
cv2.destroyAllWindows()
