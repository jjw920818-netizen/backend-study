import numpy as np #숫자 계산과 행렬 처리하는 도구
import tensorflow as tf 
#구글에서 만든 가장 유명한 AI 라이브러리 신경망을 만들고, 복잡한 수학 연산을 GPU나 CPU에서 빠르게 돌아가게 해주는 '본체' 역할
from tensorflow import keras 
from tensorflow.keras import layers #신경망의 층(Layer)을 만드는 부품
import matplotlib.pyplot as plt #그래프 그리기 도구

print("🤖 TensorFlow 버전:", tf.__version__)
print("✅ 라이브러리 로딩 완료!\n")

#윤년 판별 함수 만들기
def is_leap_year(year):
    """
   규칙 :
   1. 4의 배수이면서 100의 배수가 아니면 ➡️ 윤년
   2. 400의 배수면 ➡️ 윤년
   3. 그 외 ➡️ 평년
    """
    if(year % 400 == 0):
        return 1 #400의 배수 윤년
    elif ( year % 100 == 0):
        return 0 #100의 배수 평년(400 제외)
    elif (year % 4 == 0):
        return 1 #4의 배수 윤년(100 제외)
    else:
        return 0 # 그 외 평년

years = np.array([i for i in range(1, 2001)]) #1년부터 2000년까지의 연도
labels = np.array([is_leap_year(y) for y in years]) #각 연도의 윤년 여부   

print("\n📈 윤년 비율:")
print(f"  윤년: {np.sum(labels)/len(labels)*100:.2f}%")
print(f"  평년: {(1-np.sum(labels)/len(labels))*100:.2f}%")

#데이터 전처리
X_train = years / 2000.0  # 0~1 사이로 변환
y_train = labels

# Sequential: 층을 순서대로 쌓는 방식
model = keras.Sequential([
    # 입력층
    layers.Input(shape=(1,)),  # 입력: 연도 1개
    
    # 은닉층 1: 64개 뉴런
    layers.Dense(64, activation='relu', name='hidden_layer_1'),
    
    # 은닉층 2: 32개 뉴런
    layers.Dense(32, activation='relu', name='hidden_layer_2'),
    
    # 은닉층 3: 16개 뉴런
    layers.Dense(16, activation='relu', name='hidden_layer_3'),
    
    # 출력층: 1개 뉴런 (0~1 확률)
    layers.Dense(1, activation='sigmoid', name='output_layer')
], name='LeapYearModel')

print("\n📋 모델 요약:")
model.summary()

#모델 컴파일(학습 준비)
print("""
컴파일 설정:
- Optimizer (최적화): Adam (가장 많이 쓰이는 방법)
- Loss (손실함수): Binary Crossentropy (0/1 분류용)
- Metrics (평가지표): Accuracy (정확도)
""")

model.compile(
    optimizer='adam',  # 학습 방법
    loss='binary_crossentropy',  # 손실 함수 (0/1 분류)
    metrics=['accuracy']  # 평가 지표
)

print("✅ 컴파일 완료!")


# 학습 실행
history = model.fit(
    X_train, y_train,
    epochs=100,  # 100번 반복 학습
    batch_size=32,  # 32개씩 묶어서 학습
    validation_split=0.2,  # 20%는 검증용
    verbose=1  # 학습 과정 출력
)

print("\n✅ 학습 완료!")

#결과 시각화
# 학습 곡선 그리기
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 정확도 그래프
axes[0].plot(history.history['accuracy'], label='훈련 정확도', linewidth=2)
axes[0].plot(history.history['val_accuracy'], label='검증 정확도', linewidth=2)
axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('Accuracy', fontsize=12)
axes[0].set_title('모델 정확도 변화', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 손실 그래프
axes[1].plot(history.history['loss'], label='훈련 손실', linewidth=2)
axes[1].plot(history.history['val_loss'], label='검증 손실', linewidth=2)
axes[1].set_xlabel('Epoch', fontsize=12)
axes[1].set_ylabel('Loss', fontsize=12)
axes[1].set_title('모델 손실 변화', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 최종 성능
final_accuracy = history.history['val_accuracy'][-1] * 100
print(f"\n🎯 최종 검증 정확도: {final_accuracy:.2f}%")

#2040년 예측
# 2040년 데이터 준비
year_to_predict = 2040
year_normalized = year_to_predict / 2000.0  # 정규화

# 예측 실행
prediction = model.predict(np.array([year_normalized]), verbose=0)
probability = prediction[0][0]

print(f"\n🤖 모델 예측:")
print(f"  - 윤년 확률: {probability*100:.2f}%")

if probability > 0.5:
    result = "윤년 ⭕"
else:
    result = "평년 ❌"

print(f"  - 최종 판정: {result}")

# 실제 정답 확인
actual = is_leap_year(year_to_predict)
actual_text = "윤년 ⭕" if actual == 1 else "평년 ❌"
print(f"\n✅ 실제 정답: {actual_text}")

if (probability > 0.5 and actual == 1) or (probability <= 0.5 and actual == 0):
    print("🎉 정답! 모델이 올바르게 예측했습니다!")
else:
    print("❌ 오답... 모델이 틀렸습니다.")