# EKS에서 배포된 JVM의 Heap Dump 추출

- 명령어
```s
kubectl exec <pod_name> -- jmap -dump:live,format=b,file=/tmp/heapdump.hprof 1234
kubectl cp <pod_name>:/tmp/heapdump.hprof heapdump.hprof
```
- 옵션 설명
    - kubectl exec <pod_name>: 특정 파드에 접근하고 명령을 실행
    - --: kubectl exec 명령어 옵션과 파드 내에서 실행할 명령어를 구분
    - jmap: JVM memory map tool name
    - -dump: jmap의 heap dump 생성 옵션
    - live: GC에 의에 회수되지 않은 live object'만' 포함해서 덤프 생성. memory leak 분석에 용이해짐.
    - format=b: dump file format을 binary로 설정. 어차피 다른 선택지가 없다.
    - file=/tmp/heapdump.hprof: 파드의 /tmp 디렉토리에 heapdump.hprof 힙덤프 파일 생성
    - 1234: jmap으로 덤프 생성할 PID 입력