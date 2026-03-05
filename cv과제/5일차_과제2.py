import cv2
import pytesseract
from PIL import Image
import os

#이미지 파일 불러오기
image_files = [
     'doc/doc1.jpg',
    'doc/doc2.jpg',
    'doc/doc3.jpg',
    'doc/doc4.jpg',
    'doc/doc5.jpg'
]
#총 페이지 수
total_pages = len(image_files)
print(f'총{total_pages}개의 페이지를 처리합니다.\n')

# 전체 텍스트를 저장할 변수 초기화
full_text = "" #5개의 텍스트를 하나로 합쳐서 파일로 저장

for i, img_path in enumerate(image_files, 1):
    
    print(f"\n{'='*60}")
    print(f"📄 처리 중: {i}/{total_pages} 페이지")
    print(f"📁 파일명: {img_path}")
    print(f"{'='*60}")
    
    # 이미지 파일 읽기
    img = cv2.imread(img_path)
    
    # 파일 읽기 오류 처리
    if img is None:
        print(f"⚠️  경고: '{img_path}' 파일을 찾을 수 없거나 읽을 수 없습니다.")
        print(f"💡 확인사항:")
        print(f"   1. 파일 이름이 정확한가? (대소문자, 확장자 포함)")
        print(f"   2. 파일이 Python 파일과 같은 폴더에 있는가?")
        print(f"   3. 파일이 손상되지 않았는가?")
        print(f"➡️  이 페이지를 건너뛰고 다음 페이지로 진행합니다.\n")
        continue
    
    # 이미지 크기 정보 출력
    height, width = img.shape[:2]
    print(f"📐 이미지 크기: {width} x {height} 픽셀")
    
    # 전처리 1단계: 그레이스케일 변환
    print(f"🔄 전처리 1단계: 그레이스케일 변환 중...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 전처리 2단계: 이진화
    print(f"🔄 전처리 2단계: 이진화 처리 중...")
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 전처리 3단계: 노이즈 제거
    print(f"🔄 전처리 3단계: 노이즈 제거 중...")
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    
    print(f"✅ 전처리 완료!")
    
    # OCR 실행
    print(f"🔍 OCR 실행 중 (텍스ト 인식)...")
    text = pytesseract.image_to_string(denoised, lang='kor+eng')
    
    # 추출된 텍스트 정보 출력
    char_count = len(text)
    line_count = text.count('\n')
    
    print(f"✅ OCR 완료!")
    print(f"📊 추출 결과:")
    print(f"   - 문자 수: {char_count}자")
    print(f"   - 줄 수: 약 {line_count}줄")
    
    # 텍스트 미리보기 (처음 100자)
    preview = text[:100] if len(text) > 100 else text
    print(f"📝 텍스트 미리보기:")
    print(f"   {preview}...")

    # 전체 텍스트에 추가
    separator = '=' * 50
    full_text += f"\n{separator}\n"
    full_text += f"페이지 {i} / {total_pages}\n"
    full_text += f"파일: {img_path}\n"
    full_text += f"{separator}\n\n"
    full_text += text
    full_text += "\n\n"
    
    print(f"💾 페이지 {i} 텍스트가 전체 문서에 추가되었습니다.\n")

# ============================================================
# 4. 전체 텍스트를 파일로 저장
# ============================================================

print(f"\n{'='*60}")
print(f"💾 텍스트 파일로 저장 중...")
print(f"{'='*60}\n")

output_filename = 'output_document.txt'

with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(full_text)

# ============================================================
# 5. 최종 통계 및 완료 메시지
# ============================================================

total_chars = len(full_text)
total_lines = full_text.count('\n')
file_size = os.path.getsize(output_filename)
file_size_kb = file_size / 1024

print(f"\n{'='*60}")
print(f"🎉 모든 작업이 완료되었습니다!")
print(f"{'='*60}\n")

print(f"📊 작업 통계:")
print(f"   ✓ 처리된 페이지: {total_pages}개")
print(f"   ✓ 총 문자 수: {total_chars:,}자")
print(f"   ✓ 총 줄 수: {total_lines:,}줄")
print(f"   ✓ 파일 크기: {file_size_kb:.2f} KB")

print(f"\n💾 저장된 파일:")
print(f"   📄 파일명: {output_filename}")
print(f"   📁 위치: {os.path.abspath(output_filename)}")

print(f"\n{'='*60}\n")