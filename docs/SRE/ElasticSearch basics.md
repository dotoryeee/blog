# ElasticSearch 정리

!!! tip
    
    변경 가능한 변수 부분은 "garden" keyword를 포함하고 있다

## cURL
1. 클러스터 내부 인덱스 목록 조회
    ```s
    curl -X GET "localhost:9200/_cat/indices?v"
    ```
2. bulk API 사용
    ```s
    curl -H "Content-Type: application/x-ndjson" \
    -X POST localhost:9200/_bulk \
    --data-binary "@./bulk_file"
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
    2. DSL 쿼리를 이용한 조회 (전문검색예시)
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
        
        정리하자면 "lee jeongwon"이라는 데이터를 text 타입으로 저장할 경우 "jeongwon" 키워드로 검색할 수 있지만
        keyword 타입으로 저장할 경우 "jeongwon" 키워드로 검색할 수 없고 "lee jeongwon" 전문을 키워드로 사용해야 검색할 수 있다
    
5. 멀티필드 인덱스 생성 예시<br>
   fields 매핑 파라미터를 사용해 하나의 필드를 여러 용도로 사용할 수 있다<br>
   message 필드는 text타입이지만 keyword 타입도 가지게된다
    ```s
    PUT multifield_index
    {
        "mappings": {
            "properties": {
                "message": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                            }
                    }
                }
            }
        }
    }
    ```

6. 멀티필드 인덱스 keyword쿼리 예시
    ```s
    GET multifield_index/_search
    {
        "query": {
            "term": {
                "message.keyword": "jeongwon"
            }
        }
    }
    ```

7. 인덱스 템플릿 조회

    !!! warning
        
        _index_template API는 ElasticSearch 7.8 이상에서 동작
        https://www.elastic.co/guide/en/elasticsearch/reference/7.8/index-templates.html

    ```s
    GET _index_template/*
    ```

8. 인덱스 템플릿 생성
   
    !!! tip

        **ElasticSearch 7.8 이상에서** 인덱스 생성 시 여러개의 인덱스 템플릿 패턴에 매칭되는 경우, priority값이 가장 높은 하나의 인덱스 템플릿이 적용된다

    ```s
    PUT _index_template/garden_template
    {
    "index_patterns": ["garden_*"],
    "priority": 1,
    "template": {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas":1
        },
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "age": {"type": "short"},
                "gender": {"type": "keyword"}
            }
        }
    }
    }
    ```

9.  인덱스 템플릿 삭제

    !!! tip
        
        템플릿 생성/삭제시 기존 인덱스들은 영향받지 않는다. 이미 만들어진 인덱스가 변경되진 않는다.

    ```s
    DELETE _index_template/garden_template
    ```

10. 다이나믹 매핑 예시 1<br>
    -> string을 포함하는 모든 필드가 text가 아닌 keyword 타입으로 매핑된다
    
    ```s
    PUT garden_test1{
        "mappings": {
            "dynamic_templates": [
                {
                    "garden_string_fields": {
                        "match_mapping_type": "string",
                        "mapping": {"type": "keyword"}
                    }
                }
            ]
        }
    }
    ```

11. 다이나믹 매핑 예시 2<br>
    -> 필드 이름이 long으로 시작하면서 text로 끝나지 않는 필드들의 type을 long으로 매핑한다
    
    ```s
    PUT garden_test2{
        "mappings": {
            "dynamic_templates": [
                {
                    "garden_long_fields": {
                        "match": "long_*",
                        "unmatch": "*_text",
                        "mapping": {"type": "long"}
                    }
                }
            ]
        }
    }
    ```

12. 다이나믹 매핑에서 사용할 수 있는 조건식은 아래 페이지를 참조하자<br>
    [https://www.elastic.co/guide/en/elasticsearch/reference/master/dynamic-templates.html](https://www.elastic.co/guide/en/elasticsearch/reference/master/dynamic-templates.html)

13. 

---
참고: 엘라스틱 스택 개발부터 운영까지(책만)