# Kubernetes on WSL

## Enable kubernetes option on Docker Desktop
!!! tip
    Docker Desktop을 이용하는 경우 마우스 클릭 한 번으로 Kubernetes를 사용할 수 있습니다

1. Run 'docker desktop' and turn on 'Enable Kubetnetes' option.
    ![enable_kubernetes_0](Kubernetes%20on%20WSL/2023-02-12_14-40-41.png)
2. Click 'Apply & Restart' for restart docker desktop
3. 약 15분 정도 경과 Kubetnetes관련 컨테이너 설치가 완료되면 후 좌측 하단에 Kubetnetes가 잘 활성화 된 것을 확인할 수 있습니다
    ![enable_kubetnetes_1](Kubernetes%20on%20WSL/2023-02-12_14-57-43.png)
    ![enable_kubetnetes_2](Kubernetes%20on%20WSL/2023-02-12_14-59-46.png)
4. Docker desktop에서 Kubetnetes가 활성화 되면 바로 kubectl 명령이 사용 가능해집니다
    ![enable_kubernetes_3](Kubernetes%20on%20WSL/2023-02-12_15-04-07.png)
    ![enable_kubernetes_3](Kubernetes%20on%20WSL/2023-02-12_15-05-43.png)

## Install minikube on WSL2 Ubuntu
   
!!!tip
    Minikube는 로컬에서 단일 노드로 Kubernetes를 실행할 수 있게 도와주는 툴입니다. Production환경에 적용하기엔 제약이 많지만, 테스트 및 학습 목적으로 사용하기엔 충분합니다.

!!!notice
    Docker Desktop의 경우 재직자수 250명 이상의 회사에서 사용하면 비용을 지불해야하므로(개인사용자는 해당없음) Minikube를 이용하여 Docker Desktop을 대체할 수 있습니다.

1. 


## Install Kustomize
!!!tip
    Kubernetes 매니페스트파일(yaml) 파일의 효율적인 관리는 위해 Kustomize를 설치해봅니다

1. 


