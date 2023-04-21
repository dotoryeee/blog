# Python 환경 관리: alternatives, poetry, conda

1. alternatives (심볼링 링크 자동화)
    - 장점:
        간단한 방식으로 시스템 전체에서 사용할 Python 버전을 쉽게 변경할 수 있습니다.
    - 단점:
        프로젝트별 가상 환경을 지원하지 않아, 여러 프로젝트에서 서로 다른 종속성을 가진 경우 관리가 어렵습니다.

2. poetry (가상환경)
    파이썬 내부의 venv를 사용해 가상환경을 생성하고 pip를 이용해 pypi에서 패키지를 가져옵니다.
    - 장점:
        프로젝트별 가상 환경을 지원하여 서로 다른 종속성을 가진 프로젝트를 관리할 수 있습니다.
        종속성의 버전을 자동으로 관리하며, 메타데이터와 종속성을 선언하는 pyproject.toml 파일을 사용하여 명시적으로 종속성을 기록합니다.
        프로젝트별 가상 환경 관리를 자동으로 지원합니다.
    - 단점:
        Python 버전 관리 기능이 약합니다. 별도의 버전 관리 도구를 함께 사용해야 할 수도 있습니다.
        기존의 requirements.txt로 종속성을 관리할 수 없습니다 (import는 가능 poetry import requirements.txt)
        
3. conda (가상환경)
    anaconda 자체 가상화 환경을 사용하고, conda 자체 저장소(anaconda cloud)를 사용해 패키지를 가져옵니다. (conda config --add channels <channel_name>로 외부 저장소를 추가할 수도 있음)
    - 장점:
        다양한 프로그래밍 언어의 패키지 및 종속성을 관리할 수 있습니다. (Python 외에 R, Ruby 등 사용가능)
        프로젝트별 가상 환경을 지원하며, 서로 다른 종속성을 가진 프로젝트를 쉽게 관리할 수 있습니다.
    - 단점:
        conda는 패키지 설치시 conda install 명령으로 설치해야 하지만 conda에서 지원하지 않는 패키지의 경우, pip와 함께 사용해야 할 수도 있어 관리가 복잡해집니다(의존성 충돌 발생 가능성 up). pip를 사용하고자 하는 경우 conda install pip로 pip 추가 후 pip install <package> 를 사용합니다.
        일부 패키지는 conda에서 사용할 수 없을 수도 있고, 최신버전을 사용하지 못 할 수도 있습니다.
