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
> 3. SSD 모델을 활용하여 경향성 평가 [.mp4]()
> > * Miss Rate: 0% / mAP: 0.909% 달성 






