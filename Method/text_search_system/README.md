## Hardware

#### 무인매장 계산대 하드웨어 구현
* 재료: 우드락, 절연 테이프, 초강력 본드, 'ㄷ'자형 벽걸이용 책꽂이, 클립형 무선 LED 조명등, 웹캠(ABKO, 1080 FHD) 등
* 영상의 선명도와 그림자를 고려하여 2개의 LED 조명등 활용
* 최종 발표 전 프로토타입으로써 80% 완성   
![2](https://user-images.githubusercontent.com/32587029/144235528-3f31fb05-c9d8-47c3-8dda-6724909a1fce.JPG)

---
## POS GUI - Search

#### Function
* 상품 촬영시, 낮은 확률로 검출되지 못하는 상품은 고객이 직접 POS GUI를 통해 입력
* 검색된 '초성' 혹은 '글자'를 포함하는 모든 상품명을 후보에 띄움 >> 그 중 고객이 선택 및 추가  

#### Algorithm
* 파이썬 'jamo' 라이브러리를 활용하여 자음과 모음을 추출할 수 있도록 함
* 코드를 살펴보면 우리가 기본적으로 사용하는 문자형과 인코딩 숫자가 달라 8252를 더해줌으로써 맞춤
* DB의 모든 단어와 비교하여 후보군 탐색 
* [블로그](https://smlee729.github.io/python/natural%20language%20processing/2015/12/29/korean-letter-processing-search.html)

#### Example
![3](https://user-images.githubusercontent.com/32587029/144235547-c7fa5bfe-5eb0-43b8-b2ee-f41c11b13a74.JPG)


