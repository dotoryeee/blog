const BASE_URL = "http://localhost:8000";

// 모든 post 가져오기
function getPosts() {
    // 게시물 목록을 요청하는 fetch API 호출
    fetch(`${BASE_URL}/posts`)
        // 응답 객체를 JSON 형태로 파싱
        .then(response => response.json())
        // 파싱된 게시물 데이터를 이용하여 화면에 출력
        .then(posts => {
            // 게시물 목록을 출력할 DOM 요소를 선택
            const postList = document.querySelector("#post-list");
            // 게시물 목록 초기화
            postList.innerHTML = "";
            // 각 게시물을 순회하며 화면에 출력
            for (const post of posts) {
                // 테이블 행 생성
                const row = document.createElement("tr");
                // 제목 셀 생성
                const titleCell = document.createElement("td");
                // 제목 셀에 게시물 제목 설정
                titleCell.textContent = post.title;
                // 내용 셀 생성
                const contentCell = document.createElement("td");
                // 내용 셀에 게시물 내용 설정
                contentCell.textContent = post.content;
                // 행에 제목 셀 추가
                row.appendChild(titleCell);
                // 행에 내용 셀 추가
                row.appendChild(contentCell);
                // 게시물 목록에 행 추가
                postList.appendChild(row);
            }
        });
}


// 새로운 post 등록
function submitPost() {
    // 입력된 제목 값을 가져옴
    const title = document.querySelector("#title").value;
    // 입력된 내용 값을 가져옴
    const content = document.querySelector("#content").value;
    // 제목과 내용을 포함한 객체 생성
    const post = { title, content };
    // 게시물 추가 요청을 위한 fetch API 호출
    fetch(`${BASE_URL}/posts`, {
        method: "POST", // HTTP 메소드 설정
        headers: {
            "Content-Type": "application/json" // 요청 헤더 설정
        },
        body: JSON.stringify(post) // 객체를 JSON 형태로 변환하여 요청 본문에 포함
    })
        // 응답 객체를 JSON 형태로 파싱
        .then(response => response.json())
        // 게시물 추가가 완료되면 화면에 게시물 목록을 갱신
        .then(post => {
            getPosts();
        });
}

// post에 해당하는 comment 가져오기
function getComments(postId) {
    // postId에 해당하는 댓글을 API에서 가져오기 위해 fetch 요청 수행
    return fetch(`${BASE_URL}:8081/comment?postId=${postId}`)
        .then(response => response.json()); // 응답을 JSON 형태로 변환하여 반환
}

// comment DOM 요소 생성
function createCommentElement(comment) {
    // 새로운 div 엘리먼트를 생성
    const commentElement = document.createElement("div");
    // 생성한 div 엘리먼트에 댓글 내용을 추가
    commentElement.textContent = comment.content;
    // 생성한 div 엘리먼트에 'comment' 클래스를 추가
    commentElement.className = "comment";
    // 완성된 댓글 엘리먼트 반환
    return commentElement;
}


/**
 *  comments API 서버로부터 응답이 없는 경우에도 post는 표시 가능하도록 try catch 구문 사용
 *  -> API 호출 실패시 comment는 빈 배열로 전달
 */
async function getPostsWithComments() {
    const posts = await fetch(`${BASE_URL}/posts`).then(response => response.json());
    for (let post of posts) {
        try {
            post.comments = await getComments(post.id);
        } catch (error) {
            console.error(`Error fetching comments fro ${post.id}:`, error);
            post.comments = [];
        }
    }
    return posts;
}

// post과 comment을 함께 렌더링
function renderPost(post) {
    // 새로운 행(row) 엘리먼트를 생성
    const row = document.createElement("tr");
    // 제목 셀(title cell) 엘리먼트를 생성
    const titleCell = document.createElement("td");
    // 제목 셀에 게시물의 제목 텍스트를 추가
    titleCell.textContent = post.title;
    // 내용 셀(content cell) 엘리먼트를 생성
    const contentCell = document.createElement("td");
    // 내용 셀에 게시물의 내용 텍스트를 추가
    contentCell.textContent = post.content;
    // 댓글 셀(comments cell) 엘리먼트를 생성
    const commentsCell = document.createElement("td");
    // 게시물의 댓글 목록을 순회하며 댓글 엘리먼트를 생성하고 댓글 셀에 추가
    for (let comment of post.comments) {
        const commentElement = createCommentElement(comment);
        commentsCell.appendChild(commentElement);
    }
    // 제목 셀, 내용 셀, 댓글 셀을 행에 추가
    row.appendChild(titleCell);
    row.appendChild(contentCell);
    row.appendChild(commentsCell);
    // 완성된 행(row) 엘리먼트 반환
    return row;
}


// comment rendering
async function renderComments() {
    // post 목록 DOM 요소 찾기
    const postList = document.querySelector("#post-list");
    // post 목록 초기화
    postList.innerHTML = "";
    // post와 comment를 포함한 post 목록 가져오기
    const posts = await getPostsWithComments();
    // post와 comment를 함께 출력
    for (let post of posts) {
    const row = renderPost(post);
    postList.appendChild(row);
        }
    }
    
    // form submit event listener
    const form = document.querySelector("form");
    form.addEventListener("submit", (event) => {
    // submit의 기본 동작(페이지를 새로고침 또는 다른 페이지로 이동) 삭제
    event.preventDefault();
    submitPost();
    // comment가 포함된 post목록 새로고침
    renderComments();
    });
    
// 페이지 최초 로드시 post목록 불러오기
getPosts();