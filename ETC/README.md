# POS GUI - Search

### Function

* 상품 촬영시, 낮은 확률로 검출되지 못하는 상품은 고객이 직접 POS GUI를 통해 입력
* 검색된 '초성' 혹은 '글자'를 포함하는 모든 상품명을 후보에 띄움 >> 그 중 고객이 선택 및 추가  

### Algorithm
  * 파이썬 'jamo' 라이브러리를 활용하여 자음과 모음을 추출할 수 있도록 함
  * 코드를 살펴보면 우리가 기본적으로 사용하는 문자형과 인코딩 숫자가 달라 8252를 더해줌으로써 맞춤
  * DB의 모든 단어와 비교하여 후보군 탐색 
  * [블로그](https://smlee729.github.io/python/natural%20language%20processing/2015/12/29/korean-letter-processing-search.html)

### Example
![1](https://user-images.githubusercontent.com/32587029/144233739-f84f74e7-ea04-4087-9539-5b6f178bf0ed.JPG)

