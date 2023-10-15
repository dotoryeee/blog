---
draft: true
date: 2021-05-01
authors:
  - dotoryeee
categories:
  - study
  - java
---
# JVM Options

## JVM options 정리

- Xms<br>
Xms 옵션은 JVM 시작 시 할당할 초기 메모리 크기를 설정합니다. 이 옵션을 사용하면 시작 시 할당되는 메모리 크기를 제한할 수 있습니다. 값을 지정하지 않으면 JVM이 설정한 기본 초기 메모리 크기를 사용합니다.

- Xmx<br>
Xmx 옵션은 JVM에서 사용할 수 있는 최대 메모리 크기를 설정합니다. 이 옵션을 사용하면 JVM이 사용할 수 있는 메모리 크기를 제한할 수 있습니다. 값을 지정하지 않으면 JVM이 설정한 기본 최대 메모리 크기를 사용합니다.

- Xmn<br>
Xmn 옵션은 객체가 처음 생성되는 영역인 Young 영역에 할당할 메모리 크기를 설정합니다. 이 옵션 값을 적절히 설정하면 성능이 영향을 받을 수 있습니다.

- XX:PermSize<br>
Java 8부터는 PermGen 공간이 Metaspace로 변경되어 이 옵션을 사용하지 않습니다.

- XX:MaxDirectMemorySize<br>
이 옵션은 Direct 메모리의 크기를 제한하는 데 사용됩니다. Direct 메모리는 JVM의 힙 외부에서 운영 체제에 의해 할당되는 메모리입니다.

- XX:+UseCompressedOops<br>
이 옵션은 64비트 JVM에서 작은 객체의 메모리 사용량을 줄입니다. 객체 포인터가 32비트 정수로 저장됩니다.

- XX:+UseG1GC (Java 7 이상)<br>
이 옵션은 새로운 가비지 컬렉터인 G1(Garbage First)를 사용하도록 지정합니다. G1 GC는 큰 힙 크기에 최적화되어 있습니다.

- XX:+UseConcMarkSweepGC<br>
이 옵션은 CMS(Concurrent Mark and Sweep) 가비지 컬렉터를 사용하도록 지정합니다. 이 가비지 컬렉터는 중단 시간을 줄이고 응답성을 높이는 데 사용됩니다. 그러나 최근에는 G1 GC와 같은 새로운 가비지 컬렉터가 도입되어 사용되지 않습니다.

- XX:ThreadStackSize<br>
이 옵션은 스레드 스택의 크기를 설정하는 데 사용됩니다. 기본값은 운영 체제에 따라 다릅니다. 이 값을 작게 설정하면 스택 오버플로우가 발생할 수 있습니다.

- XX:MaxTenuringThreshold<br>
이 옵션은 새로 생성된 객체가 Survivor 영역에 남는 시간을 설정하는 데 사용됩니다. 이 옵션은 G1 GC에서 주로 사용됩니다.

## CMS GC에서 G1 GC로 전환할 때 주의할 점

- Xmn, -XX:NewRatio를 사용하지 않습니다.<br>
G1 GC는 Young 영역과 Old 영역이 동시에 존재하지 않고, 전체 힙을 여러 영역으로 나누고 각 영역에 대해 Young, Mixed, Old 단계를 수행하기 때문에, -Xmn, -XX:NewRatio와 같은 Young 영역 크기 설정 옵션을 사용할 수 없습니다.

- XX:+UseG1GC 옵션을 추가합니다.<br>
G1 GC를 사용하려면 -XX:+UseG1GC 옵션을 추가해야 합니다. 이 옵션을 추가하지 않으면 기존의 CMS GC가 사용됩니다.

- XX:MaxGCPauseMillis 옵션을 적절히 설정합니다.<br>
G1 GC의 주요 목표 중 하나는 일괄 처리 시간을 최소화하는 것입니다. 이를 위해 -XX:MaxGCPauseMillis 옵션을 사용하여 GC 일괄 처리 시간의 최대 지연 시간을 설정할 수 있습니다.

- XX:G1HeapRegionSize 옵션을 적절히 설정합니다.<br>
G1 GC에서는 전체 힙을 일정한 크기의 region으로 분할합니다. 이때 region의 크기는 -XX:G1HeapRegionSize 옵션을 통해 설정할 수 있습니다. 이 값을 적절히 설정하면 성능에 영향을 미칩니다.

- XX:InitiatingHeapOccupancyPercent 옵션을 적절히 설정합니다.<br>
G1 GC에서는 일괄 처리 작업을 수행하기 전에 Old 영역의 사용률을 모니터링합니다. 이때 사용되는 옵션이 XX:InitiatingHeapOccupancyPercent입니다. 이 값을 적절히 설정하여 Old 영역의 수집이 필요한 시점을 조절할 수 있습니다.

- XX:ConcGCThreads 옵션을 적절히 설정합니다.<br>
G1 GC에서는 수집 작업과 일괄 처리 작업을 병렬로 처리합니다. 이때 사용되는 스레드 수는 -XX:ConcGCThreads 옵션을 통해 설정할 수 있습니다. 이 값을 적절히 조정하여 병렬 처리의 성능을 개선할 수 있습니다.

## G1 GC에서 ZGC로 전환시 장단점 (JAVA 11~)

- 장점<br>
    - 짧은 정지 시간: ZGC는 큰 힙 크기에서도 수 밀리 초에서 최대 수십 밀리 초로 정지 시간을 제어할 수 있습니다.
    - 확장성 향상: ZGC는 대규모 시스템에서 수천 개의 CPU와 수백 GB 힙 크기를 지원합니다.
    - GC 처리량 향상: ZGC는 메모리 압축 과정에서 CPU를 덜 사용하기 때문에 다른 GC보다 더 높은 처리량을 얻을 수 있습니다.
    - 동시 수행 작업에 대한 응답성 향상: ZGC는 애플리케이션에서 동시 작업과 GC 작업을 모두 처리하기 때문에, 다른 GC보다 애플리케이션의 응답성이 높아집니다.

- 단점<br>
    - 메모리 오버헤드 발생: ZGC는 매우 큰 메모리 영역을 관리하기 때문에 메모리 오버헤드가 발생할 수 있습니다.
    - 성능이 약간 저하될 수 있음: ZGC는 동시 GC의 특성 때문에, 힙의 특정 영역이 여러 번 GC되는 상황이 발생할 수 있으며, 이는 약간의 성능 저하를 초래할 수 있습니다.