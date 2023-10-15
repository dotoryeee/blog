---
draft: true
date: 2021-05-01
authors:
  - dotoryeee
categories:
  - Python
---
# Python 정리

!!! notice
    파이썬 코드 작성 후 타인과 공유하다보니 클린코드의 필요성을 느껴 공부한것을 기억할 겸 정리했습니다

!!! warning
    아직 책을 읽으며 정리하는 중 입니다

1. PEP-8 Naming style 요약 [PEP-8 원문](https://peps.python.org/pep-0008/#descriptive-naming-styles)
    - `_single_leading_underscore`: weak “internal use” indicator. E.g. from M import * does not import objects whose names start with an underscore
    - `single_trailing_underscore_`: used by convention to avoid conflicts with Python keyword, e.g.
        ```py
        tkinter.Toplevel(master, class_='ClassName')
        ```
    - `__double_leading_underscore`: when naming a class attribute, invokes name mangling (inside class FooBar, __boo becomes _FooBar__boo; see below).
    - `__double_leading_and_trailing_underscore__`: “magic” objects or attributes that live in user-controlled namespaces. E.g. `__init__`, `__import__` or `__file__`. Never invent such names; only use them as documented.
2. PEP-8 Naming Convetions 요약 [PEP-8 원문](https://peps.python.org/pep-0008/#naming-conventions)
    - 단일 문자로 ‘l’ (lowercase letter el), ‘O’ (uppercase letter oh), or ‘I’ (uppercase letter eye) 사용 금지
    - classNames: CamelCase
    - Type Variable Names: 
    - Exception Names: 
    - Global Variable Names: 
    - Function and Variable Names: 
    - Function and Method Arguments: 
    - Method Names and Instance Variables: 
    - Constants: 
3. DataClass
    - Python < 3.6
        ```py
        class Human:
            def __init__(self, name, age):
                self.name = name
                self.age = age
        ```
    - Python >= 3.7
        ```py
        from dataclasses import dataclass
        @dataclass
        class Human:
            name: str
            age: int
        ```
4. Docstring
    함수 생성 바로 아랫줄에 " 3개를 사용하여 Docstring을 생성합니다
    ```py
    def make_alert(message: str) -> None:
        """
        Docstring here
        string타입을 message를 입력받아 화면에 출력합니다
        """
        print(message)
    ```
5. 훌륭한 코드란? -> 읽기 쉽고 이해하기 쉬운 코드
    1. 동료 개발자가 쉽게 이해할 수 있는지
    2. 팀에 새로 온보딩 하는 사람도 빠르게 이해하고 효과적으로 작업할 수 있는지
6. 파이썬 코드 검증 도구
    1. mypy
    2. pylint
    3. flake8
    4. black
7. PR시 불필요한 논쟁을 줄이기 위해 코딩 컨벤션을 강제하고 자동 포매팅 도구를 설정한다
    1. flake8 (PEP-8만 준수하면 됨, 엄격하지 않음)
    2. black (변수 타입이 중간에 변하면 안됨, 후행 쉼표 강제 등 매우 엄격)
8. 표준을 준수하도록 위 과정을 CI 빌드 과정에 포함해야 한다
9.  Makefile을 이용한 자동 검사 설정 예시 (CI에 활용 가능)<br>
   Makefile을 활용하여  CI도구가 가능한 적은 설정 옵션을 가지게 한다.

    ```s title="checklist"
    .PHONY: typehint
    typehint:
        mypy ./
    
    .PHONY: test
    test:
        pytest ./
    
    .PHONY: black
    black:
        black -l 79 ./*.py
    
    .PHONY: clean
    clean: 
        find ./ type -f -name "*.pyc" -exec rm -rf {} \;
    ```

    ```s
    make checklist
    ```

10. `Magic method`는 python에서 특수한 동작을 수행하기 위해 예약한 메서드로 이중 언더바로 둘러싸여있다(`__len__` 등)
11. Context manager (with구문) 사용 (PEP-343)
    ```py
    f = open(file)
    try:
        process(f)
    finally:
        f.close()
    ```
    
    위와 동일한 기능을 pythonic하게 구현할 수 있다
    ```py
    with open(file) as f:
        process(f)
    ```
    예외가 발생해도 블록이 완료되면 파일이 자동으로 닫힌다

12. Context manager는 블록 전/후로 로직을 분리함으로써 관심사를 분리하고 독립적으로 유지되어야하는 코드를 분리하는 좋은 방법이다.
13. with문은  `__enter__` method를 호출하고 context가 종료되면 `__exit__` method를 호출한다
14. Context manager를 활용한 postgre DB backup example
    ```py
    def stop_database():
        run("systemctl stop postgresql")
    
    def start_database():
        run("systemctl start postgresql")
    
    class DBHandler:
        def __enter__(self):
            stop_database()
            return self
        
        def __exit__(self, exc_type, ex_value, ex_traceback):
            """
            __exit__함수는 블록에서 발생한 예외를 파라미터로 받는다. 블록에 예외가 없으면 모두 None 이다.
            __exit__함수는 특별한 작업을 할 필요가 없다면 아무것도 반환하지 않아도 된다.
            __exit__에서 True로 반환하지 않도록 주의해야한다. True를 반환하는 경우 잠재적으로 발생한 예외를 호출자에게 전파하지 않고 멈추는 것을 뜻하기 때문이다.
            """
            start_database()

    def db_backup():
        run("pg_dump database")
    
    def main():
        """
        main함수는 db_backup함수에 오류가 발생하더라도 __exit__ 함수를 호출한다
        """
        with DBHandler():
            db_backup()
    ```

15. contextlib 모듈 사용 [Python >= 3.5](https://docs.python.org/3/library/contextlib.html)
    




---
참고: 파이썬 클린코드 2nd Edition(터닝포인트)<br>
.PHONY: [https://jusths.tistory.com/226](https://jusths.tistory.com/226)<br>
