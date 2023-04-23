# board app very very resistant to infrastructure failures

## Tech and tools
- Python + FastAPI + SQLAlchemy + MySQL 8 을 이용한 Backend server 2 EA
- Terraform을 활용한 형상관리 가능한 인프라
- CI/CD 적용 (솔류션 미정)
- Docker를 이용해 서버 이미지를 빌드하여 immutable server 적용
- AWS EKS를 이용한 Kubernetes기반 orchestration

## Structure
- 2개의 Backend API Server를 **MSA 아키텍쳐를 적용**해 분리하였습니다.
- 각 API Server는 **MVC 패턴**에 따라 코드를 작성하여 유지보수 효율성을 높였습니다.

## TODO
- [ ] 게시판 글을 담당할 post_server API server 생성
- [ ] 댓글을 담당할 comment_server API server 생성
- [ ] 주석, docstring 많이 달기
- [ ] Terraform 코드 생성
- [ ] atlantis를 사용한 인프라 CI/CD
- [ ] AWS EKS에서 comment_server blue/green 배포

## Key Features
- 


## Results & Implications
- 


## Conclusion
- 


