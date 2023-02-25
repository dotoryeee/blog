# Python 정리

!!! notice
    파이썬 코드 작성 후 타인과 공유하다보니 클린코드의 필요성을 느껴 공부한것을 기억할 겸 정리했습니다

1. DataClass
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
2. Docstring
    함수 생성 바로 아랫줄에 " 3개를 사용하여 Docstring을 생성합니다
    ```py
    def make_alert(message: str) -> None:
        """
        Docstring here
        string타입을 message를 입력받아 화면에 출력합니다
        """
        print(message)
    ```
3. 훌륭한 코드란? -> 읽기 쉽고 이해하기 쉬운 코드
    1. 동료 개발자가 쉽게 이해할 수 있는지
    2. 팀에 새로 온보딩 하는 사람도 빠르게 이해하고 효과적으로 작업할 수 있는지
4. 파이썬 코드 검증 도구
    1. mypy
    2. pylint
    3. flake8
    4. black
5. PR시 불필요한 논쟁을 줄이기 위해 코딩 컨벤션을 강제하고 자동 포매팅 도구를 설정한다
    1. flake8 (PEP-8만 준수하면 됨, 엄격하지 않음)
    2. black (변수 타입이 중간에 변하면 안됨, 후행 쉼표 강제 등 매우 엄격)
6. 표준을 준수하도록 위 과정을 CI 빌드 과정에 포함해야 한다
7. Makefile을 이용한 자동 검사 설정 예시 (CI에 활용 가능)
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
    clean: find ./ type -f -name "*.pyc" -exec rm -rf {} \;
    ```

    ```s
    make checklist
    ```
8. 


---
참고: 파이썬 클린코드 2nd Edition(터닝포인트)<br>
.PHONY: [https://jusths.tistory.com/226](https://jusths.tistory.com/226)<br>
