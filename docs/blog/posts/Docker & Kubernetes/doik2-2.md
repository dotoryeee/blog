---
draft: true
date: 2023-10-29
authors:
  - dotoryeee
categories:
  - study
  - Kubernetes
  - Database
  - Cloudnet@
---
# Database on Kubernetes study / Week 2
---
스터디 커리큘럼, 강의 및 스크립트를 [Cloudnet@](http://gasidaseo.notion.site/gasidaseo/CloudNet-Blog-c9dfa44a27ff431dafdd2edacc8a1863)팀의 가시다님께서 제공해주셨습니다. 항상 감사드립니다.

## 목차
1. Kubernetes operator
2. MySQL 구성
3. MySQL Operator for Kubernetes
4. MySQL Operator for Kubernetes 배포
5. 테스트를 위한 Wordpress 배포
6. 장애 테스트
7. Scaling 테스트
8. MySQL 백업 및 복구

<!-- more -->

---
## 실습
1. Kubernetes Operator
    1. Kubernetes(이하 k8s)의 operator는 3가지 요소로 구성되어 있다.<br>
    ![](./doik2/crd-cd-operator.webp)<br>출처: [betterprogramming.pub](https://betterprogramming.pub/write-tests-for-your-kubernetes-operator-d3d6a9530840)
    2. CRD: Custom Resource Definition<br> operator를 사용하기 위해 먼저 k8s API를 확장하여 새로운 리소스 유형을 정의하는 CRD는 YAML형식의 파일로 새로운 Object의 Scheme를 정의한다.
    3. CR: Custom Resource<br> 앞서 정의한 CRD를 기반으로 생성할 수 있는 custom object로, 어플리케이션 상태, 구성, metadata를 저장하는데 사용한다. 당연히 YAML이다.
    4. Operator Controller<br> Operator의 로직을 담고 있는 컴포넌트이고, k8s api server와 직접 통신하여 CR의 상태를 감지하다가 생성, 업데이트, 삭제 등 실제 작업을 수행한다.
2. MySQL 구성
    1. MySQL구성은 Primary-Secondary구성과 NDB Cluster, InnoDB Cluster를 사용할 수 있다.
    2. MySQL Primary Secondary replication
        1. Primary: 모든 쓰기(INSERT, UPDATE, DELETE) 작업을 처리하고, 데이터 변경이 발생하면 변경사항을 바이너리 로그에 기록한다.
        2. Secondary: Primary 서버에서 발생한 변경사항을 복제하여 동기화하며, 읽기전용 복제본을 제공함으로써 읽기 작업에 대한 부하를 분산시켜준다.
        3. replication: Primary의 바이너리 로그에서 변경사항을 읽고 Secondary 이를 재실행하여 데이터를 동기화한다.
    3. MySQL NDB Cluster
        ![NDB-Cluster](./doik2/ndb-cluster.png)<br> 출처: [dev.mysql.com](https://dev.mysql.com/doc/refman/8.0/en/mysql-cluster-overview.html)
        1. 구성요소
            1. Data Node: 실제 데이터를 저장하며는 Data node는 여러 노드로 분산되어 있어 HA를 제공하고 Scale-Out이 가능하다.
            2. SQL Node: 클라이언트의 SQL 요청을 처리하며, 데이터를 Data Node에서 읽고 쓴다.
            3. Management Node: 클러스터의 구성과 상태를 관리하며, Data Node와 SQL Node의 연결을 관리한다
        2. 특징
            1. NDB Cluster는 빠른 읽기/쓰기와 Scaling 용이성에 초점을 맞추고 있다.
            2. NDB (Network Database) 스토리지 엔진을 사용한다.
            3. 데이터는 여러 Data Node에 자동으로 분산되어 저장된다.
            4. 데이터는 주로 메모리에 저장되며, 디스크에도 백업된다.
            5. 메모리 기반 스토리지와 데이터 분산으로 인해 높은 읽기/쓰기 성능을 제공한다.
            6. 데이터는 자동으로 샤딩되어 여러 노드에 분산된다.
            7. NDB Cluster의 설정과 관리는 복잡하다.
    4. MySQL InnoDB Cluster
        ![InnoDB-cluster](./doik2/mysql-operator-architecture-2.png)<br>MySQL with k8s operator (Primary-Secondary)상세 구조 / 출처: [dev.mysql.com](https://dev.mysql.com/doc/mysql-operator/en/mysql-operator-introduction.html)
        1. 구성요소
            1. MySQL Server Pod: InnoDB storage engine을 사용하는 MySQL pod는 서로 데이터를 복제하고 클라이언트의 읽기와 쓰기 요청을 처리한다.
            2. Group Replication: MySQL Group Replication은 MySQL pod들 사이에서 데이터를 동기화하는 역할을 수행하고 데이터의 일관성과 가용성을 유지하며 특정 pod가 실패하더라도 클러스터가 동작할 수 있게 유지한다.
            3. MySQL Router: 클라이언트 요청을 적절한 MySQL pod로 라우팅하는 역할을 하여 read request를 로드 밸런싱하고 write request를 적절한 pod 전달하여 클러스터의 가용성을 향상시킨다.
            4. MySQL Shell: 클러스터의 구성과 관리를 수행하는 도구로 사용자는 MySQL Shell을 통해 클러스터의 상태를 모니터링 및 구성 변경을 수행할 수 있다.
        2. 특징
            1. InnoDB Cluster는 쉬운 설정과 높은 데이터 일관성에 초점을 맞추고 있다.
            2. InnoDB 스토리지 엔진을 사용한다.
            3. 데이터는 MySQL Group Replication을 통해 서버 인스턴스(pod)간에 복제된다.
            4. 데이터는 주로 디스크에 저장된다.
            5. 동기식 복제와 트랜잭션 일관성을 통해 높은 데이터 일관성을 제공한다.
            6. InnoDB Cluster는 설정과 관리가 간편하다.
3. MySQL Operator for Kubernetes
    ![](./doik2/mysql-operator-architecture.jpg)<br>MySQL with k8s operator / 출처: [ronekins.com](https://ronekins.com/2021/08/31/getting-started-with-the-oracle-mysql-kubernetes-operator-and-portworx/)
    1. k8s에 MySQL cluster배포 시 operator를 사용하는 이유
        1. 복잡한 MySQL Cluster 구성을 간편하게 YAML 파일로 정의 하고 kubectl apply 명령으로 "쉽게 배포할 수 있다".
        2. Cluster의 Life cycle를 관리하며 백업, 복구, 업그레이드, 스케일링과 같은 "운영 작업을 자동화"한다.
        3. Node가 실패했을 때 자동으로 복구하고 필요에 따라 새 인스턴스를 생성하여 "서비스의 중단을 최소화"한다.(고가용성 확보)
        4. Cluster의 상태를 모니터링하고, 문제가 발생하면 "자동으로 복구 작업을 수행"할 수 있다.
        5. Cluster에 Node를 추가하거나 제거하는 작업을 자동화하여 "scaling을 쉽게 진행"할 수 있다.
4. MySQL Operator for Kubernetes 배포
    1. 
    ```sh 
    # Repo 추가
    helm repo add mysql-operator https://mysql.github.io/mysql-operator/
    helm repo update

    # MySQL operator 설치 
    helm install mysql-operator mysql-operator/mysql-operator --namespace mysql-operator --create-namespace --version 2.0.12
    helm get manifest mysql-operator -n mysql-operator
    ```
    ![](./doik2/2023-10-29%2009%2012%2048.png)
    ```sh
    # 설치 확인
    kubectl get deploy,pod -n mysql-operator
    ```
    ![](./doik2/2023-10-29%2009%2016%2035.png)
    ```sh

    # CRD 확인
    kubectl get crd | egrep 'mysql|zalando'
    ```
    ![](./doik2/2023-10-29%2009%2017%2035.png)
    ```sh

    ## (참고) CRD 상세 정보 확인
    kubectl describe crd innodbclusters.mysql.oracle.com

    # (참고) 삭제
    helm uninstall mysql-operator -n mysql-operator && kubectl delete ns mysql-operator
    ```
5. 테스트를 위한 Wordpress 배포
6.  장애 테스트
7.  Scaling 테스트
8.  MySQL 백업 및 복구