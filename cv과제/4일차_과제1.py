import cv2
import numpy as np

# 전역 변수
drawing = False
mode = None
start_x, start_y = -1, -1 #마우스를 처음 클릭한 위치(시작점)
img = None 
temp_img = None

def draw_shape(event, x, y, flags, param):
    """마우스 이벤트를 처리하는 함수"""
    global start_x, start_y, drawing, mode, img, temp_img
    
    # 1. 왼쪽 버튼 누름 → 원 그리기 시작
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        mode = 'circle'
        start_x, start_y = x, y
        temp_img = img.copy()
    
    # 2. 오른쪽 버튼 누름 → 선 그리기 시작
    elif event == cv2.EVENT_RBUTTONDOWN:
        drawing = True
        mode = 'line'
        start_x, start_y = x, y
        temp_img = img.copy()
    
    # 3. 마우스 움직임 → 미리보기
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = temp_img.copy()
            
            if mode == 'circle':
                # 원 미리보기 (파란색)
                radius = int(np.sqrt((x - start_x)**2 + (y - start_y)**2))
                cv2.circle(img_copy, (start_x, start_y), radius, (255, 0, 0), 2)
            
            elif mode == 'line':
                # 선 미리보기 (빨간색)
                cv2.line(img_copy, (start_x, start_y), (x, y), (0, 0, 255), 2)
            
            cv2.imshow('Drawing', img_copy)
    
    # 4. 왼쪽 버튼 뗌 → 원 완성 (녹색)
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing and mode == 'circle':
            radius = int(np.sqrt((x - start_x)**2 + (y - start_y)**2))
            cv2.circle(img, (start_x, start_y), radius, (0, 255, 0), 2)
            cv2.imshow('Drawing', img)
            drawing = False
    
    # 5. 오른쪽 버튼 뗌 → 선 완성 (주황색)
    elif event == cv2.EVENT_RBUTTONUP:
        if drawing and mode == 'line':
            cv2.line(img, (start_x, start_y), (x, y), (0, 165, 255), 2)
            cv2.imshow('Drawing', img)
            drawing = False

def main():
    global img

    img = np.ones((600,800,3), dtype = np.uint8) * 255 #세로 600 가로 800 3채널

    cv2.namedWindow('Drawing')  # 'Drawing'이라는 이름의 창 생성
    cv2.setMouseCallback('Drawing', draw_shape)  # 마우스 움직임을 draw_shape 함수와 연결
    
    while True:
        cv2.imshow('Drawing', img)  # 현재 캔버스를 화면에 표시
        key = cv2.waitKey(1) & 0xFF  # 1밀리초 대기하면서 키 입력 확인
        
        # 종료 조건: 'q' 키 또는 ESC(27번) 키를 누르면
        if key == ord('q') or key == 27:
            break  # 루프 탈출
        
        # 초기화: 'c' 키를 누르면
        elif key == ord('c'):
            img = np.ones((600, 800, 3), dtype=np.uint8) * 255  # 새 흰색 캔버스
            print("캔버스가 초기화되었습니다.")
    cv2.destroyAllWindows()  # 프로그램 종료 시 모든 OpenCV 창 닫기

if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 main() 실행
    # (다른 파일에서 import 했을 때는 실행 안 됨)
    main()        