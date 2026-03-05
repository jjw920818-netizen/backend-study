import cv2
import numpy as np

#이미지 불러오기
image_path = 'images/제니.webp'
original = cv2.imread(image_path)
print('✅이미지 업로드 완료!')

# 그레이스켕ㄹ 변환(흑백으로 변환)
gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
print("✅그레이스케일 변환 완료!")

kernel_size = 5 

# 세 가지 블러 적용
blur_avg = cv2.blur(gray,(kernel_size, kernel_size)) #평균 블러

blur_gaussian = cv2.GaussianBlur(gray, (kernel_size, kernel_size),0) #가우시안 블러

blur_median = cv2.medianBlur(gray, kernel_size) #미디안 블러

def add_label(img, text):
        """
        이미지 상단에 흰색 배경 + 검은색 텍스트 레이블 추가
        
        Args:
            img: 원본 이미지
            text: 표시할 텍스트
        Returns:
            레이블이 추가된 이미지
        """
        labeled = img.copy()  # 원본 보존을 위해 복사
        
        # 흰색 사각형 그리기 (배경)
        # cv2.rectangle(이미지, 시작점, 끝점, 색상, 두께)
        # -1 = 내부를 채움
        cv2.rectangle(labeled, (0, 0), (labeled.shape[1], 40), (255, 255, 255), -1)
        
        # 검은색 텍스트 쓰기
        # cv2.putText(이미지, 텍스트, 위치, 폰트, 크기, 색상, 두께)
        cv2.putText(labeled, text, (10, 28), 
                    cv2.FONT_HERSHEY_SIMPLEX,  # 폰트 종류
                    0.7,  # 폰트 크기
                    (0, 0, 0),  # 검은색
                    2)  # 두께
        return labeled
    
    # 각 이미지에 레이블 추가
gray_labeled = add_label(gray, "Original (Grayscale)")
blur_avg_labeled = add_label(blur_avg, f"Average Blur ({kernel_size}x{kernel_size})")
blur_gaussian_labeled = add_label(blur_gaussian, f"Gaussian Blur ({kernel_size}x{kernel_size})")
blur_median_labeled = add_label(blur_median, f"Median Blur ({kernel_size}x{kernel_size})")

result = np.hstack([gray_labeled, blur_avg_labeled, 
                       blur_gaussian_labeled, blur_median_labeled])
    
print("\n✅ 4개 이미지 합치기 완료!")

cv2.imshow('Blur Comparison', result)

while True:
        key = cv2.waitKey(1) & 0xFF  # 키 입력 확인
        
        if key == ord('q') or key == 27:  # 'q' 또는 ESC 키
            print("\n프로그램 종료")
            break
        
        elif key == ord('s'):  # 's' 키로 저장
            output_path = 'blur_comparison_result.jpg'
            cv2.imwrite(output_path, result)  # 이미지 파일로 저장
            print(f"\n💾 결과 이미지 저장 완료: {output_path}")