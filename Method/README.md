# Method


## Problem Definition

* 계산대에 올라갈 수 있는 **다양한 조합의 상품들을** 카메라로 촬영해서 사진에 담긴 상품들의 종류를 **Classification** 하는 것

* 현재 데이터셋은 단일 상품에 대한 이미지로 구성되어 있고 이를 가공하려면 Data Augmentation 기법에 대한 Survey가 필요함

* 상품의 바코드를 detect 해서 , 이를 가지고 classification 하는 방법을 설계할 수도 있으나 , 여러 case에 대해서 Robust 하지 않을 것이라고 생각됨
  * 예를 들면 고객이 바코드를 가리게 상품을 배치해서 인식을 하지 못하는 상황

* **Data Augmentation 기법을 적용하지 않는 다면 우리의 Framework는 Category를 하나씩 학습 하지만 , Inference는 Multi-label Classifiaction이 가능하도록 설계해야 함**
  * 최대한 이 방법을 고수하고 싶음 , 실제 편의점에서도 새로운 상품이 들어올 때 그 상품만 학습을 진행해도 문제가 없게끔 설계해야 더 가치있다고 생각이 듬

#### 즉 , 정리하면 단일 이미지 데이터셋을 가지고 학습을 진행했을 때 Multiclass Inference가 가능한 모델을 설계하는 것이 목표

## Method Keyword

> 방법론 Survey를 진행할 때 , Computing Resource가 어느정도 요구 될지도 고려를 해야 함

**1. Metric Learning**

**2. Multi-class Classification**
