# Transaction on GCP Spanner

## μλ΄

---

!!! notice
    π‘ λ€μ μμ μ κ³΅λΆνλ©° μμ½νμμ΅λλ€


![Transaction on GCP Spanner/Untitled.png](Transaction on GCP Spanner/Untitled.png)

## Spannerλ₯Ό μ μ¬μ©ν΄μΌ ν κΉ

---

κ°λ¨νκ² μμ½νμλ©΄, μλκ° λ°μ ν¨μ λ°λΌ μ»΄ν¨ν°κ° κ°μ§κ² λλ λ°μ΄ν°μ μμ΄ λλ¬΄ λμκ³  μ΄λ ν΅μ κ° λ§€μ° μ΄λ ΅μ΅λλ€. μ΄λ₯Ό μν΄ κΈ°μ‘΄ RDBμ νΈλμ­μ, κ°λ ₯ν μΌκ΄μ±, μννμ₯μ± λ± λ€μν κΈ°λ₯μ μ§μνλ NewSQL DBκ° λ±μ₯νμκ³ , Spannerλ μ΄λ₯Ό μ§μνκ³  μμ΅λλ€.

μ΄λ¬ν Spannerλ SQLμ κΈ°λ₯μ μ¬μ©ν  μ μμμ λ¬Όλ‘  μΏΌλ¦¬λ³΅μ‘λ, λ΄κ΅¬μ±, μλ, μ²λ¦¬λ λΆλΆμμ λ§€μ° μ°μνκΈ°λλ¬Έμ λκ·λͺ¨ μ€μκ° μ²λ¦¬κ° νμν κ²½μ° κ³ λ €ν  μ μλ μλ¨ μ€ νλμλλ€.

## μ€μ΅

---

1. Spanner μ¬μ©μ μμν©λλ€
    
    ![Transaction on GCP Spanner/Untitled%201.png](Transaction on GCP Spanner/Untitled%201.png)
    
2. SpannerμΈμ€ν΄μ€λ₯Ό μμ±ν©λλ€.
μ΄λ Instance IDλ API νΈμΆμ νμν κ³΅μ ID μλλ€
    
    ![Transaction on GCP Spanner/Untitled%202.png](Transaction on GCP Spanner/Untitled%202.png)
    
3. μ€ν¨λμμ μ¬μ©ν  DBλ₯Ό μμ±ν©λλ€.
    
    ![Transaction on GCP Spanner/Untitled%203.png](Transaction on GCP Spanner/Untitled%203.png)
    
4. SQLμ μ΄μ©ν΄ DBλ΄ νμ΄λΈμ μμ±ν©λλ€
    
    ![Transaction on GCP Spanner/Untitled%204.png](Transaction on GCP Spanner/Untitled%204.png)
    
5. νμ΄λΈμ΄ μ μμ±λμμ΅λλ€.  sqlλ‘ μκ°νλ©΄ 'desc employees' μλλ€
    
    ![Transaction on GCP Spanner/Untitled%205.png](Transaction on GCP Spanner/Untitled%205.png)
    
6. google cloud SDK(μ΄ν SDK)μμ μ μνκΈ° μν΄ λ€μ λͺλ Ήμ μ€νν©λλ€
    
    ```s
    gcloud auth application-default login {Project ID}
    ```
    
7. 6.3 μ½λλ₯Ό μ΄μ©ν΄ νμ΄λΈμ κ°μ μΆκ°ν©λλ€.
μ΄λ 6.3 μ½λλ JSONμ μ΄μ©ν΄ λ°μ΄ν°λ₯Ό μ½μν©λλ€[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.3.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.3.js)
8. λ°μ΄ν°κ° μ μ½μλλ©΄ λ€μκ³Ό κ°μ΄ νμΈν  μ μμ΅λλ€
9. @SDK
    
    ![Transaction on GCP Spanner/Untitled%206.png](Transaction on GCP Spanner/Untitled%206.png)
    
10. @μ½μ
    
    ![Transaction on GCP Spanner/Untitled%207.png](Transaction on GCP Spanner/Untitled%207.png)
    
11. 6.4 μ½λλ₯Ό μ΄μ©ν΄ KEYκ°μ΄ '1'μΈ νμ μ λ³΄λ₯Ό κ°μ Έμ΅λλ€
 [https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.4.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.4.js)
12. μ μ€νλλ κ²μ νμΈν  μ μμ΅λλ€
    
    ![Transaction on GCP Spanner/Untitled%208.png](Transaction on GCP Spanner/Untitled%208.png)
    
13. 6.5 μ½λλ₯Ό μ¬μ©ν΄ λͺ¨λ  μ λ³΄λ₯Ό λΆλ¬μ¬ μλ μμ΅λλ€
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.5.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.5.js)
    
    ![Transaction on GCP Spanner/Untitled%209.png](Transaction on GCP Spanner/Untitled%209.png)
    
14. SDKμ½λκ° μλ SQLκ΅¬λ¬Έμ μ΄μ©ν΄ μ λ³΄λ₯Ό λΆλ¬μ¬ μλ μμ΅λλ€.
SDKμ½λμ SQLκ΅¬λ¬Έμ μ½μνμ¬ μ€ννλ 6.6μ½λλ₯Ό μ€νν΄λ΄λλ€
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.6.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.6.js)
    
    ![Transaction on GCP Spanner/Untitled%2010.png](Transaction on GCP Spanner/Untitled%2010.png)
    
15. μ΄λ whereμ μ μ΅μμ λ£κ³  μΆμΌλ©΄ 6.7μ½λμ κ°μ΄ νλΌλ©ν°λ₯Ό μ½μν©λλ€
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.7.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.7.js)
    
    ![Transaction on GCP Spanner/Untitled%2011.png](Transaction on GCP Spanner/Untitled%2011.png)
    
16. νμ΄λΈμ μ€ν€λ§λ λ€μκ³Ό κ°μ΄ λ κ°μ§ λ°©λ²μΌλ‘ λ³κ²½ν  μ μμ΅λλ€
17. β  μ½μμμ DDLμ μ΄μ©ν΄ μ§μ  λ³κ²½νκΈ°
    
    ![Transaction on GCP Spanner/Untitled%2012.png](Transaction on GCP Spanner/Untitled%2012.png)
    
18. λ€μκ³Ό κ°μ΄ μ μ©λ κ²μ νμΈν  μ μμ΅λλ€
    
    ![Transaction on GCP Spanner/Untitled%2013.png](Transaction on GCP Spanner/Untitled%2013.png)
    
19. β‘ SDKμ SQLκ΅¬λ¬Έ μ§μ  μ€μ΄λ³΄λ΄κΈ°

    ```sql
    gcloud spanner databases ddl update test-database --instance=test-instance --ddl="ALTER TABLE employees ALTER COLUMN name STRING(MAX) NOT NULL;"
    ```
    
20. μμΈμ μ¬μ©νκΈ° μν΄ μμΈνμ΄λΈμ μμ±ν©λλ€
        
    ```sql
    CREATE INDEX employees_by_name ON employees (name)
    ```

    ![Transaction on GCP Spanner/Untitled%2014.png](Transaction on GCP Spanner/Untitled%2014.png)
    
21. μμΈ ν λ€μ λ°μ΄ν°λ‘ λμκ° μΆκ° λ°μ΄ν°λ₯Ό κ°μ Έμ€λ κ²μ λΉν¨μ¨μ μ΄κΈ° λλ¬Έμ μ μ΄μ μμΈνμ΄λΈμ λ€λ₯Έ λ°μ΄ν°λ μΆκ°λ‘ μ½μν΄λ μ μμ΅λλ€
    
    ```sql
    CREATE INDEX employees_by_name ON employees (name) STORING (start_date)
    ```
    
22. μμΈνμ΄λΈμ λ€λ₯Έλ°μ΄ν° μ΄μ΄ μΆκ°λ‘ μ§μ λ λͺ¨μ΅μλλ€
    
    ![Transaction on GCP Spanner/Untitled%2015.png](Transaction on GCP Spanner/Untitled%2015.png)
    
23. νΈλμ­μμ κ²½νν΄λ³΄κΈ° μν΄ 6.18μ½λλ₯Ό μ¬μ©ν©λλ€
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.18.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.18.js)
μ½λλ₯Ό μ΄ν΄λ³΄λ©΄ νΈλμ­μ μΈλΆμμ μμν ν μ μ©μ μλν©λλ€
    
    ![Transaction on GCP Spanner/Untitled%2016.png](Transaction on GCP Spanner/Untitled%2016.png)
    
24. μ½κΈ°/μ°κΈ° νΈλμ­μμ μμ½μ΄ λΆκ°λ₯ νλ―λ‘ μμ μ μμ±λ κΈμ λͺ¨λ μ½μ΄μΌ ν©λλ€
25. λμΌνμ μ²λ¦¬νλ νΈλμ­μμ 6.20μ½λλ₯Ό μ΄ν΄λ³΄λ©΄ λ©λλ€
[https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.20.js](https://github.com/Jpub/GCP/blob/master/Chapter_6/list6.20.js)
