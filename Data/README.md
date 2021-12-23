# Data

* 데이터셋 출처 : https://aihub.or.kr/aidata/34145
---
## Preprocessing

#### 최종 데이터 전처리 코드: [.py]()

1. 합성 데이터 생성
> * AI Hub 플랫폼에서 제공하는 롯데정보통신 '단일 상품 이미지'를 활용
> * background 이미지를 생성하고 상품 이미지에서 bbox 좌표에 해당하는 영역(상품)만 crop하여 paste
> ![1](https://user-images.githubusercontent.com/32587029/147170065-c67b37a0-f387-49d5-9845-90214cc527e5.JPG)


2. Occlusion 고려
> * 고객이 계산대에 물건을 겹치게 올리는 경우에 대비하여 paste시, IOU 0.3까지 허용되도록 코드 작성
> ![2](https://user-images.githubusercontent.com/32587029/147170338-26f87ed3-8363-4ce3-b4d8-c8f3d3bb0da2.JPG)

3. 상품 추출
> * 단일 상품 이미지에서 직사각형의 bbox 좌표 영역(상품)만 추출한 것이므로 여전히 배경 존재
> * 이러한 특성이 Noise로 작용하거나 과적합을 유발한다고 판단하여 단일 상품 이미지에서 상품 외의 배경 흰색 처리
> * 이후, 흰색 background를 생성하고 그 위에 처리해준 단일 상품 이미지를 crop & paste
> ![3](https://user-images.githubusercontent.com/32587029/147170664-c38f60f8-9a31-4c04-8964-04e36b7ba208.JPG)     

4. 다양한 전처리 시도
> * 인식 모델에서는 상품인지(1) 아닌지(0)의 여부만 판단하기 때문에 Edge Extraction 처리 후 학습 및 평가 시도
> * 상품이 항상 정방향으로 놓이는 것이 아니라 비스듬히(대각 형태 등) 놓일 수 있기 때문에 45N° Rotation 고려  
> * 배경(계산대)에 과적합되지 않도록 다양한 색상, 명암의 background 고려
> ![5](https://user-images.githubusercontent.com/32587029/147171425-6fc60ccb-3487-4b0a-b204-7a777ea887e3.JPG)
    
5. 최종 학습 데이터 생성
> * 다음과 같이 최종 학습 데이터 생성
> ![5](https://user-images.githubusercontent.com/32587029/147171491-60882be6-2660-4184-ab3c-8c1728fbd182.JPG)

---
# Hardware

#### 무인매장 계산대 하드웨어 구현
* 재료: 우드락, 절연 테이프, 초강력 본드, 'ㄷ'자형 벽걸이용 책꽂이, 클립형 무선 LED 조명등, 웹캠(ABKO, 1080 FHD) 등
* 양질의 영상(선명도, 그림자 고려)을 얻기 위해 2개의 클립형 무선 LED 조명등 활용

![2](https://user-images.githubusercontent.com/32587029/144235528-3f31fb05-c9d8-47c3-8dda-6724909a1fce.JPG)
![6](https://user-images.githubusercontent.com/32587029/147169495-a5bf9c57-d47a-42c5-83f7-40987b0657da.JPG)
