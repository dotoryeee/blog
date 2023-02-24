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

3. 