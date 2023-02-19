# ElasticSearch 정리

!!! tip
    
    변경 가능한 변수 부분은 "garden" keyword를 포함하고 있다

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
    2. DSL 쿼리를 이용한 조회 예시. match를 사용해 전문 검색하는 예시로 역인덱싱된 garden term을 검색하는 중이다.
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

5. 클러스터 내부 인덱스 목록 조회
    ```s
    GET _cat/indices?v
    ```

7. 클러스터 내부 인덱스 목록 조회(cURL)
    ```s
    curl -X GET "localhost:9200/_cat/indices?v"
    ```
8. bulk API 사용(cURL)
    ```s
    curl -H "Content-Type: application/x-ndjson" \
    -X POST localhost:9200/_bulk \
    --data-binary "@./bulk_file"
    ```

    !!! warning

        bulk_file은 json이 아닌 ndjson 문법임에 주의할 것 (delimeter로 개행문자 \n을 사용)

9. 인덱스 매핑 확인
    ```s
    GET ljw_index/_mapping
    ```
10. 인덱스 명시적 매핑 (ljw_index 인덱스의 gender 필드 타입을 keyword로 변경하는 예시)
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

11. text타입의 경우 ElasticSearch analyzer에 의해 토큰으로 분리 후 인덱싱되어, 향후 토큰(단어) 단위로 검색이 가능한데, token으로 잘 분리되었는지 analyze API를 사용해 확인해볼 수 있다<br>
    상세 내용은 13번 항목 참조

    ```s
    POST _analyze
    {
        "analyzer": "starndard",
        "text": "the token test"
    }

    ```s
    POST _analyze
    {
        "analyzer": "stop",
        "text": "the token test"
    }
    ```

    !!! tip
        
        정리하자면 "lee jeongwon"이라는 데이터를 text 타입으로 저장할 경우 "jeongwon" 키워드로 검색할 수 있지만
        keyword 타입으로 저장할 경우 "jeongwon" 키워드로 검색할 수 없고 "lee jeongwon" 전문을 키워드로 사용해야 검색할 수 있다
    
12. 멀티필드 인덱스 생성 예시<br>
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

13. 멀티필드 인덱스 keyword쿼리 예시
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

14. 인덱스 템플릿 조회

    !!! warning
        
        _index_template API는 ElasticSearch 7.8 이상에서 동작
        https://www.elastic.co/guide/en/elasticsearch/reference/7.8/index-templates.html

    ```s
    GET _index_template/*
    ```

15. 인덱스 템플릿 생성
   
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

16.  인덱스 템플릿 삭제

    !!! tip
        
        템플릿 생성/삭제시 기존 인덱스들은 영향받지 않는다. 이미 만들어진 인덱스가 변경되진 않는다.

    ```s
    DELETE _index_template/garden_template
    ```

17. 다이나믹 매핑 예시 1<br>
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

18. 다이나믹 매핑 예시 2<br>
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

19. 다이나믹 매핑에서 사용할 수 있는 조건식은 아래 페이지를 참조하자<br>
    [https://www.elastic.co/guide/en/elasticsearch/reference/master/dynamic-templates.html](https://www.elastic.co/guide/en/elasticsearch/reference/master/dynamic-templates.html)

20. ElasticSearch Analyzer Flow
    
    ```mermaid
    graph LR
      A[캐릭터 필터] --> |문자열 변경/제거| B[토크나이저];
      B --> |문자열을 토큰으로 분리| C[토큰 필터];
      C --> |대소문자/형태소 분석 등| D[(인덱스에 저장)];
    ```

    아래 링크 참조:<br>
    - [Built-in Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html#analysis-analyzers)<br>
    - [Character filter list](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-charfilters.html)<br>
    - [Tokenizer List](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenizers.html)<br>
    - [Token filter list](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenfilters.html)<br>

21. Custom analyzer 예시<br>
    - 캐릭터 필터: 사용 안함<br>
    - 토크나이저: Elastic standard tokenizer<br>
    - 토큰 필터: 소문자화 필터 사용 후 "garden"문자를 불용어로 처리하는 garden_stopwords 커스텀 필터 적용. garden_stopwords 필터링 리스트에 소문자만 필터링 되고 있으므로 lowercase filter -> garden_stopwords 필터 적용하도록 **순서 주의**<br>

    ```s
    PUT garden_analyzer
    {
        "settings": {
            "analysis": {
                "filter": {
                    "garden_stopwords": {
                        "type": "stop",
                        "stopwords": ["garden"]
                    }
                },
                "analyzer": {
                    "garden_analyzer": {
                        "type": "custom",
                        "char_filter": [],
                        "tokenizer": "standard",
                        "filter": ["lowercase", "garden_stopwords"]
                    }
                }
            }
        }
    }
    ```

22. 엘라스틱서치 검색은 2종류로 나뉜다
    1.  쿼리 컨텍스트: 연관성에 따른 스코어 결과를 제공
    2.  필터 컨텍스트: Yes or No 결과를 제공 - 캐시O 스코어링X 검색이 빠르다

23. 쿼리 컨텍스트 검색 예시<br>
    garden_index 인덱스에서 message에 "garden" term이 존재하는 document를 검색하는 예시
    
    ```s
    GET garden_index/_search
    {
        "query": {
            "match": {
                "message": "garden"
            }
        }
    }
    ```

24. 필터 컨텍스트 검색 예시

    ```s
    GET garden_index/_search
    {
        "query": {
            "bool": {
                "filter": {
                    "term": {
                        "day_of_week": "friday"
                    }
                }
            }
        }
    }
    ```

25. ElasticSearch에서 Query를 사용하는 방법은 2가지이다<br>
    1. Query String: URI를 이용한 간결한 쿼리
    2. Query DSL (Domain Specific Language): JSON 기반의 복잡한 쿼리

26. Query String 예시
    
    ```s
    GET garden_index/_search?q=name:garden
    ```

27. Query DSL 예시

    ```s
    {
        "query": {
            "match": {
                "message.keyword": "garden"
            }
        }
    }
    ```

    Query 컨텍스트의 경우 BM25 알고리즘에 의해 Document 별로 스코어링 후 가장 유사한 Docu를 찾아내는데, 아래와 같이 explain 옵션을 사용할 경우 각 Docu에 대한 스코어링 상세 내역을 알 수 있다.

    ```s
    {
        "query": {
            "match": {
                "message.keyword": "garden"
            }
        },
        "explain": true
    }
    ```

28. 인덱스 Rollover API
    
    !!! tip
    
        Rollover API를 사용해 인덱스의 생명주기를 관리할 수 있다

    !!! warning

        1. Rollover API로 관리하고자 하는 인덱스의 이름은 반드시 -<숫자> 형태로 끝나야한다
        2. 위와 같이 rollover API를 요청하는 경우 "rollover-garden" alias를 가지는 인덱스 중 하나의 인덱스만 "is_write_index"를 true로 설정할 수 있다.

    ```s title="인덱스 생성 시 alias(별칭) 부여"
    PUT garden-001
    {
        "aliases": {
            "rollover-garden": {
                "is_write_index": true
            }
        }
    }
    ```

    ```s title="rollover API 요청"
    POST rollover-garden/_rollover
    {
        "conditions": {
            "max_age": "14d",
            "max_docs": 1,
            "max_size": "10gb"
        }
    }
    ```

29. Index Health status
    
    | Status   | Primary shard                  | Replica shard                 |
    | :--------| :----------------------------- | :---------------------------- | 
    | `GREEN`  | :material-check: Healthy       | :material-check: Healthy      |
    | `YELLOW` | :material-check: Healthy       | :material-close: Fail         |
    | `RED`    | :material-close: Fail          |  -                            |

    !!! tip

        싱글노드인 경우 Replica shard가 할당되지 않은 인덱스들은 YELLOW 상태로 표시된다

30. ElasticSearch node role은 elasticsearch.yml에서 변경할 수 있다
    
    | Node role                | node.roles value              |
    | ------------------------ | ----------------------------- |
    | Master node              | [ master ]                    |
    | Voting-only data node    | [ data, master, voting_only ] |
    | Voting-only master node  | [ master, voting_only ]       |
    | Data node                | [ data ]                      |
    | Content data node        | [ data_content ]              |
    | Hot data node            | [ data_hot ]                  |
    | Warm data node           | [ data_warm ]                 |
    | Cold data node           | [ data_cold ]                 |
    | Frozen data node         | [ data_frozen ]               |
    | Ingest node              | [ ingest ]                    |
    | Coordinating only node   | [ ]                           |

    !!! warning

        투표전용노드를 생성할 때 master node / date node 상관없이 node.roles value에 반드시 `master`가 포함되어야 한다

    이 외에 remote-eligible node, Machine learning node, Transform node 등도 존재한다. 다음 링크 참조 : [ElasticSearch node roles](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-node.html)

31. 





---
참고: <br>
1. 엘라스틱 스택 개발부터 운영까지(책만)<br>
2. 리눅스 리소스 제한 해제 가이드: [https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-system-settings.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-system-settings.html)<br>
3. 