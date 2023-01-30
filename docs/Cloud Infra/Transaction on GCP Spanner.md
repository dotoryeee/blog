# Transaction on GCP Spanner

## 안내

---

!!! notice
    💡 다음 서적을 공부하며 요약하였습니다


![Transaction on GCP Spanner/Untitled.png](Transaction on GCP Spanner/Untitled.png)

## Spanner를 왜 사용해야 할까

---

간단하게 요약하자면, 시대가 발전함에 따라 컴퓨터가 가지게 되는 데이터의 양이 너무 늘었고 이는 통제가 매우 어렵습니다. 이를 위해 기존 RDB에 트랙잭션, 강력한 일관성, 수평확장성 등 다양한 기능을 지원하는 NewSQL DB가 등장하였고, Spanner는 이를 지원하고 있습니다.

이러한 Spanner는 SQL의 기능을 사용할 수 있음은 물론 쿼리복잡도, 내구성, 속도, 처리량 부분에서 매우 우수하기때문에 대규모 실시간 처리가 필요한 경우 고려할 수 있는 수단 중 하나입니다.

## 실습

---

1. Spanner 사용을 시작합니다
    
    ![Transaction on GCP Spanner/Untitled%201.png](Transaction on GCP Spanner/Untitled%201.png)
    
2. Spanner인스턴스를 생성합니다.
이때 Instance ID는 API 호출에 필요한 공식 ID 입니다
    
    ![Transaction on GCP Spanner/Untitled%202.png](Transaction on GCP Spanner/Untitled%202.png)
    
3. 스패너에서 사용할 DB를 생성합니다.
    
    ![Transaction on GCP Spanner/Untitled%203.png](Transaction on GCP Spanner/Untitled%203.png)
    
4. SQL을 이용해 DB내 테이블을 생성합니다
    
    ![Transaction on GCP Spanner/Untitled%204.png](Transaction on GCP Spanner/Untitled%204.png)
    
5. 테이블이 잘 생성되었습니다.  sql로 생각하면 'desc employees' 입니다
    
    ![Transaction on GCP Spanner/Untitled%205.png](Transaction on GCP Spanner/Untitled%205.png)
    
6. google cloud SDK(이하 SDK)에서 접속하기 위해 다음 명령을 실행합니다
    
    ```s
    gcloud auth application-default login {Project ID}
    ```
    
7. 6.3 코드를 이용해 테이블에 값을 추가합니다.
이때 6.3 코드는 JSON을 이용해 데이터를 삽입합니다[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.3.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.3.js)
8. 데이터가 잘 삽입되면 다음과 같이 확인할 수 있습니다
9. @SDK
    
    ![Transaction on GCP Spanner/Untitled%206.png](Transaction on GCP Spanner/Untitled%206.png)
    
10. @콘솔
    
    ![Transaction on GCP Spanner/Untitled%207.png](Transaction on GCP Spanner/Untitled%207.png)
    
11. 6.4 코드를 이용해 KEY값이 '1'인 행의 정보를 가져옵니다
 [https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.4.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.4.js)
12. 잘 실행되는 것을 확인할 수 있습니다
    
    ![Transaction on GCP Spanner/Untitled%208.png](Transaction on GCP Spanner/Untitled%208.png)
    
13. 6.5 코드를 사용해 모든 정보를 불러올 수도 있습니다
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.5.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.5.js)
    
    ![Transaction on GCP Spanner/Untitled%209.png](Transaction on GCP Spanner/Untitled%209.png)
    
14. SDK코드가 아닌 SQL구문을 이용해 정보를 불러올 수도 있습니다.
SDK코드에 SQL구문을 삽입하여 실행하는 6.6코드를 실행해봅니다
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.6.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.6.js)
    
    ![Transaction on GCP Spanner/Untitled%2010.png](Transaction on GCP Spanner/Untitled%2010.png)
    
15. 이때 where절에 옵션을 넣고 싶으면 6.7코드와 같이 파라메터를 삽입합니다
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.7.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.7.js)
    
    ![Transaction on GCP Spanner/Untitled%2011.png](Transaction on GCP Spanner/Untitled%2011.png)
    
16. 테이블의 스키마는 다음과 같이 두 가지 방법으로 변경할 수 있습니다
17. ① 콘솔에서 DDL을 이용해 직접 변경하기
    
    ![Transaction on GCP Spanner/Untitled%2012.png](Transaction on GCP Spanner/Untitled%2012.png)
    
18. 다음과 같이 적용된 것을 확인할 수 있습니다
    
    ![Transaction on GCP Spanner/Untitled%2013.png](Transaction on GCP Spanner/Untitled%2013.png)
    
19. ② SDK에 SQL구문 직접 실어보내기

    ```sql
    gcloud spanner databases ddl update test-database --instance=test-instance --ddl="ALTER TABLE employees ALTER COLUMN name STRING(MAX) NOT NULL;"
    ```
    
20. 색인을 사용하기 위해 색인테이블을 생성합니다
        
    ```sql
    CREATE INDEX employees_by_name ON employees (name)
    ```

    ![Transaction on GCP Spanner/Untitled%2014.png](Transaction on GCP Spanner/Untitled%2014.png)
    
21. 색인 후 다시 데이터로 돌아가 추가 데이터를 가져오는 것을 비효율적이기 때문에 애초에 색인테이블에 다른 데이터도 추가로 삽입해둘 수 있습니다
    
    ```sql
    CREATE INDEX employees_by_name ON employees (name) STORING (start_date)
    ```
    
22. 색인테이블에 다른데이터 열이 추가로 지정된 모습입니다
    
    ![Transaction on GCP Spanner/Untitled%2015.png](Transaction on GCP Spanner/Untitled%2015.png)
    
23. 트랜잭션을 경험해보기 위해 6.18코드를 사용합니다
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.18.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.18.js)
코드를 살펴보면 트랜잭션 외부에서 작업한 후 적용을 시도합니다
    
    ![Transaction on GCP Spanner/Untitled%2016.png](Transaction on GCP Spanner/Untitled%2016.png)
    
24. 읽기/쓰기 트랜잭션은 요약이 불가능 하므로 서적에 작성된 글을 모두 읽어야 합니다
25. 동일행을 처리하는 트랜잭션은 6.20코드를 살펴보면 됩니다
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.20.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.20.js)
