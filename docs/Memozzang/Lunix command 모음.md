## tar

1. 23-01-01 ~ 23-01-13 사이에 생성된 파일 tar 압축하기
    ```s
    sudo find ./ -name "*dump*" -type f -newerat 2023-01-01 ! -newerat 2023-02-01 -exec tar rf 202301.tar {} \;```
    ```

