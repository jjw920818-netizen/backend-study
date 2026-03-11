#conda create -n vision_env3 python=3.10
#conda activate vision_env3
#pip install ultralytics easyocr opencv-python

# 1. 현재 설치된 최신 버전 삭제
#pip uninstall pillow -y

# 2. ANTIALIAS 속성이 남아있는 마지막 안정 버전(9.5.0) 설치
# pip install "pillow<10.0.0"


import cv2
from ultralytics import YOLO  #자동차검출
import easyocr #검출된 자동차로부터 번호를 읽는다

# 1. 모델 및 OCR 초기화
# 번호판 전용 학습 모델이 없다면 'yolov8n.pt'를 사용하세요. 
# (실제 서비스시엔 번호판만 학습된 pt파일이 성능이 훨씬 좋습니다.)
model = YOLO('yolov8n.pt') 
reader = easyocr.Reader(['ko', 'en']) # 한국어와 영어 지원

# 2. 이미지 로드
image_path = './images/car4.webp'
img = cv2.imread(image_path)

# 3. YOLO로 번호판(또는 차량) 검출
results = model.predict(source=image_path, conf=0.4)

for r in results:
    for box in r.boxes:
        print("검출")
        # 검출된 물체의 클래스가 '번호판'인 경우 (여기선 예시로 모든 박스 처리)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # 4. 번호판 영역만 자르기 (ROI 추출)
        plate_img = img[y1:y2, x1:x2]
        
        # 5. 잘린 영역에서 글자 읽기 (OCR)
        # detail=0은 텍스트만 가져오겠다는 의미입니다.
        ocr_result = reader.readtext(plate_img, detail=0)
        
        if ocr_result:
            plate_text = "".join(ocr_result).replace(" ", "")
            print(f"인식된 번호판: {plate_text}")
            
            # 6. 결과 시각화
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, plate_text, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# 7. 결과 출력
cv2.imshow('License Plate Recognition', img)
cv2.waitKey(0)
cv2.destroyAllWindows()