# Method


## Problem Definition

* 계산대에 올라갈 수 있는 **다양한 조합의 상품들을** 카메라로 촬영해서 사진에 담긴 상품들의 종류를 **Classification** 하는 것

* 현재 데이터셋은 단일 상품에 대한 이미지로 구성되어 있고 이를 가공하려면 Data Augmentation 기법에 대한 Survey가 필요함

* 상품의 바코드를 detect 해서 , 이를 가지고 classification 하는 방법을 설계할 수도 있으나 , 여러 case에 대해서 Robust 하지 않을 것이라고 생각됨
  * 예를 들면 고객이 바코드를 가리게 상품을 배치해서 인식을 하지 못하는 상황

* **Data Augmentation 기법을 적용하지 않는 다면 우리의 Framework는 Category를 하나씩 학습 하지만 , Inference는 Multi-label Classifiaction이 가능하도록 설계해야 함**
  * 최대한 이 방법을 고수하고 싶음 , 실제 편의점에서도 새로운 상품이 들어올 때 그 상품만 학습을 진행해도 문제가 없게끔 설계해야 더 가치있다고 생각이 듬

## Method Keyword

> 방법론 Survey를 진행할 때 , Computing Resource가 어느정도 요구 될지도 고려를 해야 함

**1. Object Detection**

**2. Retrieval**

**3. Image Classification**

---

#### 우선 , 8월 내로 진행해볼 사항

1. **Data Augmentation** -> 우선은 Copy and Paste Augmentation을 진행하기로 함 , Detection이 필연적으로 필요할 것 같아 Multi-object image data가 필요함

2. **Image Classification** -> Detection으로 Object를 잘 검출하면 그 box 이미지를 Classification Network에 던져줄 예정이므로 Image Classification 성능도 찍어볼 예정

3. **Object Detection** -> 상품을 분류하는 것은 아니고 , 어느 상품군인지까지만 분류 -> **Object의 위치를 잘 잡는 것이 핵심** 
