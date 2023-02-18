# ElasticSearch basic commands

## cURL
1. 클러스터 내부 인덱스 목록 조회
    ```s
    curl -X GET "localhost:9200/_cat/indices?v"
    ```
2. bulk API 사용
    ```s
    curl -H "Content-Type: application/x-ndjson" -X POST localhost:9200/_bulk --data-binary "@./bulk_file"
    ```

    !!! warning

        bulk_file은 json이 아닌 ndjson 문법임에 주의할 것

## Kibana Dev Tools
### 도큐먼트 
1. 도큐먼트 삽입
    ```s
    PUT ljw_index/_doc/1  {
        "name": "garden",
        "age": 29,
        "gender": "male"
    }
    ```
    도큐먼트 삽입으로 인해서 ljw_index가 신규 생성됨 -> ljw_index 인덱스 정보 확인
    ```s
    GET ljw_index
    ```
2. 도큐먼트 조회
    1. 도큐먼트 아이디로 조회
    ```s
    GET ljw_index/_doc/1 
    ```
    2. DSL 쿼리를 이용한 조회 (예시)
    ```s
    GET ljw_index/_search
    {
        "query": {
            "match": {
                "name": "garden"
            }
        }
    }
    ```
3. 도큐먼트 업데이트
    ```s
    POST ljw_index/_update/1
    {
        "doc": {
            "name": "jeongwon"
        }
    }
    ```
4. 도큐먼트 삭제
    ```s
    DELETE ljw_index/_doc/1
    ```
### 인덱스
1. 클러스터 내부 인덱스 목록 조회
    ```s
    GET _cat/indices?v
    ```
2. 인덱스 매핑 확인
    ```s
    GET ljw_index/_mapping
    ```
3. 인덱스 명시적 매핑 (ljw_index 인덱스의 gender 필드 타입을 keyword로 변경하는 예시)
    ```s
    PUT ljw_index
    {
        "mappings": {
            "properties": {
                "gender": {"type": "keyword"}
            }
        }
    }
    ```
    Data type 참조: [ElasticSearch data mapping type](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)

    !!! note "텍스트 데이터의 두 가지 타입(text, keyword)의 특성"

        전문 검색이 필요한경우 text 타입 사용(텍스트 분리 후 인덱싱 = 많은 메모리 사용량)<br>
        정렬/집계에 필요한 경우(범주형 데이터) keyword 타입 사용(원문 통째로 인덱싱)

4. text타입의 경우 ElasticSearch analyzer에 의해 토큰으로 분리 후 인덱싱되어, 향후 토큰(단어) 단위로 검색이 가능한데, token으로 잘 분리되었는지 analyze API를 사용해 확인해볼 수 있다
    ```s
    POST _analyze
    {
        "analyzer": "starndard",
        "text": "token test"
    }
    ```
!!! tip
    
    정리하자면 "lee jeongwon"이라는 데이터를 text 타입으로 저장할 경우 jeongwon 키워드로 검색할 수 있지만,
    keyword타입으로 저장할 경우 jeongwon 키워드로 검색할 수 없고 "lee jeongwon" 전문을 키워드로 사용해야 검색할 수 있다
    
5. 