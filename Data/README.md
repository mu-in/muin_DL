# Data

* 데이터셋 출처 : https://aihub.or.kr/aidata/34145

---

![캡처](https://user-images.githubusercontent.com/70448161/131636731-e2abdd3f-0fc6-4e19-8d9b-0f89235f4c13.PNG)

* 제공되는 이미지를 그대로 사용하지 않고 , Bounding Box 정보를 바탕으로 상품만 Crop을 해준다.

* Crop 시킨 이미지 중 width나 height에서 작은 부분을 기준으로 256 pixel로 Resize 시켜준다

---
# Data Preprocessing

### 최종 데이터 전처리 코드: [.ipynb](https://github.com/mu-in/muin_DL/blob/main/Data/LOTTE_Data_Augmentation.ipynb)

![README](https://user-images.githubusercontent.com/32587029/133219260-67a994d2-8cee-4867-981e-903d9945a8f5.PNG)

* 배경이미지(=계산대)를 생성하고 롯데정보통신 상품이미지(단일 상품만 고려)를 순차적으로 축소하여 배경 이미지에 삽입
> 1. 배경이미지 해상도: 2988 x 2988 / 색(RGB): (173, 255, 47) - 계산대의 색
> 2. 배경이미지 속 상품들의 위치 - 랜덤 좌표 적용 (Occlusion issue 10번 발생시 무시)
> 3. Jacard Overlap(IOU) 0.05 이상 발생하지 않도록 코드 작성Cancel changes
> 4. 상품이미지 축소 비율: 30% 로 축소 (resize ratio = 0.3)
> 5. Annotation file (.json)
> > * categories - 합성이미지 속 상품들의 라벨
> > * path - 합성이미지 위치 경로
> > * resolutions - 합성이미지 해상도
> > * boxes - 합성이미지 속 상품들의 Bounding Box 정보 

### 시행착오 및 구상

![README2](https://user-images.githubusercontent.com/32587029/133219268-8a59f21c-e457-4c22-90c9-c5aee0466d52.PNG)

* 초기 아이디어: [.pdf](https://github.com/mu-in/muin_DL/blob/main/Data/DataAugmentationPlan.pdf)

### 샘플 합성 데이터 생성 및 평가

> 1. 데이터 전처리 코드를 활용하여 롯데정보통신 상품이미지 샘플 데이터에 적용
> 2. Train: 4200 장 / Test: 835 장 생성
> 3. SSD 모델을 활용하여 경향성 평가 [.mp4](https://github.com/mu-in/muin_DL/blob/main/Data/detected_video_semi.mp4)
> > * Miss Rate: 0% / mAP: 0.909% 달성 

### 시뮬레이션

> 1. 우드락(계산대), 상품(샘플 데이터셋에 속하는 종류) 직접 구입
> 2. LED 스탠드(그림자 제거)를 이용하여 계산대 환경 조성 후 촬영
> 3. SSD 모델을 활용하여 상품 DETECT -> 몇가지 문제점 발견

* [시뮬레이션 준비물]
![simul_1](https://user-images.githubusercontent.com/32587029/134758521-9f260bb1-b042-432d-80f4-17f493d3f6e4.PNG)

* [시뮬레이션 결과]
> 1. Max Overlap (NMS) = 0.5
![simul_2](https://user-images.githubusercontent.com/32587029/134758544-85ab5fd3-cc0d-4a55-8354-bdd2b41362ab.PNG)

> 2. Max Overlap (NMS) = 0.05
![simul_3](https://user-images.githubusercontent.com/32587029/134758545-b2842230-5192-402b-837b-7f79de392b03.PNG)

##### 결과 - 문제점
> 1. 1개의 상품을 부분부분 인식하여 다수의 상품으로 DETECT
> > - NMS 기준을 낮훈다고 하여도 완벽히 해결 X (바싹 붙어있는 다른 물체를 인식하지 못함)
> > - 성능이 좋은 YOLO.v5 모델을 사용했을 때도 이러한 문제가 발생하는지 확인 필요
> 2. 특히, 과자(얼룩이 많은)와 같이 모델이 인식하기 어려운 상품에서 해당 문제 발생 

#### 샘플 합성데이터 > yolov5 모델 학습 > 시뮬레이션 영상 적용

![image](https://user-images.githubusercontent.com/32587029/136557302-ac52db25-9ff3-457a-b026-4c61f9f1a3f0.png)

> 1. 상품을 눕힌 상태로 변과 수직 혹은 수평으로 놓았을 때의 정확도는 상승함 (그림에서 삼다수는 학습 데이터셋에 없음)
> 2. 상품을 비스듬하게 놓거나 상표가 잘 보이지 않을 경우, 인식에 실패 >> 문제점 <<

* 학습 데이터에 존재하는 상품만으로 구성하고 최대한 학습 데이터의 영상과 유사한 환경을 조성한 뒤 다시 시뮬레이션 계획
* 성능이 더 좋은 모델을 고려하고, 비스듬하게 놓인 물체도 detect 할 수 있도록 학습 데이터 전처리 코드를 재작성  

