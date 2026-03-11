import cv2
import numpy as np

# --- 설정 파일 경로 ---
MODEL_PATH = './yolov8n.onnx'  # 다운로드한 YOLOv8 ONNX 모델 파일 경로
LABELS_PATH = './coco.names.txt'   # COCO 데이터셋 클래스 이름 파일 경로
INPUT_IMAGE = './images/unnamed.jpg' # 검출할 이미지 파일 경로
#INPUT_IMAGE = './images/sample2.jpg' # 검출할 이미지 파일 경로
# --------------------

#8400개의 격자를 만들어서
CONFIDENCE_THRESHOLD = 0.5     # 객체로 인정할 최소 신뢰도 (50%)
NMS_THRESHOLD = 0.4            # 중복 박스를 제거하기 위한 NMS 임계값
# --------------------

# 1. 클래스 이름 로드 - coco.names
try:
    with open(LABELS_PATH, 'r') as f:
        classes = f.read().splitlines()  # 파일을 읽어 각 줄(클래스 이름)을 리스트에 저장
    NUM_CLASSES = len(classes)
    print(f"로딩된 클래스 개수: {NUM_CLASSES}")
except FileNotFoundError:
    print(f"오류: 클래스 파일 '{LABELS_PATH}'을 찾을 수 없습니다.")
    exit()
print(classes)

# 2. YOLOv8 ONNX 모델 로드
try:
    net = cv2.dnn.readNet(MODEL_PATH)  # ONNX 파일을 OpenCV DNN 네트워크 객체로 로드
except:
    print(f"오류: 모델 파일 '{MODEL_PATH}'을 로드할 수 없습니다.")
    exit()

# 3. 이미지 로드
img = cv2.imread(INPUT_IMAGE)
if img is None:
    print(f"오류: 이미지 파일을 찾을 수 없습니다: {INPUT_IMAGE}")
    exit()

img_height, img_width = img.shape[:2]
INPUT_WIDTH, INPUT_HEIGHT = 640, 640 # YOLOv8 표준 입력 크기 정의

# 4. 이미지 전처리: Blob 생성 (DNN 입력 형식으로 변환)
blob = cv2.dnn.blobFromImage(
    img, 
    1/255.0,                         # 픽셀 값을 0~1로 정규화
    (INPUT_WIDTH, INPUT_HEIGHT),     # 이미지 크기를 640x640으로 조정
    swapRB=True,                     # BGR -> RGB 채널 순서로 스왑
    crop=False
)
net.setInput(blob)  # 변환된 Blob을 네트워크의 입력으로 설정, YOLO의 입력값으로 한다.

# 5. 모델 추론 실행
outputs = net.forward(net.getUnconnectedOutLayersNames())  # 순방향 전달(추론) 실행

# 6. 결과 후처리 (Non-Maximum Suppression - NMS)
# 검출한 항목의 경계(c,y,w,h), 0.2, 3 
boxes = []        # 최종 경계 상자 좌표 저장 리스트
confidences = []  # 신뢰도 저장 리스트
class_ids = []    # 클래스 ID 저장 리스트

output_data = outputs[0]  # YOLOv8의 첫 번째 출력 텐서 가져오기

# --- V8 출력 해석 방식 수정 ---
# YOLOv8 출력 형태가 (1, 84, 8400) 형태라면 전치(Transpose)하여 순회하기 쉽게 변환
if output_data.shape[1] == (NUM_CLASSES + 4): 
    output_data = output_data.transpose((0, 2, 1)) # (1, 84, 8400) -> (1, 8400, 84)로 변환

# output_data[0]을 순회 (8400개의 예측 상자 순회)
for detection in output_data[0]:
    # 클래스 확률은 4번째 인덱스부터 시작 (0:cx, 1:cy, 2:w, 3:h)
    scores = detection[4:] 
    class_id = np.argmax(scores)      # 가장 높은 확률의 클래스 ID
    confidence = scores[class_id]     # 해당 클래스의 신뢰도
    
    # 클래스 ID가 로드된 클래스 개수를 초과하면 무시 (비정상적인 출력 방지)
    if class_id >= NUM_CLASSES:
        continue

    # 최소 신뢰도 이상일 경우에만 처리
    if confidence >= CONFIDENCE_THRESHOLD:
        # 바운딩 박스 좌표 추출 및 원본 이미지 크기로 스케일링
        center_x = int(detection[0] * img_width / INPUT_WIDTH)
        center_y = int(detection[1] * img_height / INPUT_HEIGHT)
        width = int(detection[2] * img_width / INPUT_WIDTH)
        height = int(detection[3] * img_height / INPUT_HEIGHT)

        # 박스의 좌상단 좌표 (x, y) 계산
        x = int(center_x - width / 2)
        y = int(center_y - height / 2)

        # NMS 처리를 위해 상자 정보와 신뢰도, 클래스 ID 저장
        boxes.append([x, y, width, height])
        confidences.append(float(confidence))
        class_ids.append(class_id)

# 비최대 억제(Non-Maximum Suppression)를 적용하여 겹치는 상자 제거
indexes = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

# 7. 결과 시각화
label =""
if len(indexes) > 0:
    for i in indexes.flatten():  # NMS를 통과한 최종 인덱스만 순회
        x, y, w, h = boxes[i]
        label += " " + str(classes[class_ids[i]]) 
        confidence_str = str(round(confidences[i], 2))
        
        # 초록색 박스로 설정
        color = (0, 255, 0)

        # 이미지에 경계 사각형 그리기
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        
        # 이미지에 클래스 이름 및 신뢰도 텍스트 표시
        print(label)
        cv2.putText(img, f'{label}    {confidence_str}', (x, y + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


print(f"총 {len(indexes)}개의 객체가 검출되었습니다.")
# 8. 결과 출력
cv2.imshow("YOLOv8 Object Detection", img)
cv2.waitKey(0) # 키 입력 대기 (창 유지)
cv2.destroyAllWindows() # 열린 모든 창 닫기