// 기본 URL 설정
const BASE_URL = "http://localhost:8000";

// 모든 게시물 가져오기
function getPosts() {
    // 게시물 API 호출
    fetch(`${BASE_URL}/posts`)
        .then(response => response.json())
        .then(posts => {
            // 게시물 목록 DOM 요소 찾기
            const postList = document.querySelector("#post-list");
            // 게시물 목록 초기화
            postList.innerHTML = "";
            // 게시물 목록 생성 및 출력
            for (let post of posts) {
                const row = document.createElement("tr");
                const titleCell = document.createElement("td");
                titleCell.textContent = post.title;
                const contentCell = document.createElement("td");
                contentCell.textContent = post.content;
                row.appendChild(titleCell);
                row.appendChild(contentCell);
                postList.appendChild(row);
            }
        });
}

// 새로운 게시물 등록
function submitPost() {
    // 입력된 제목 및 내용 가져오기
    const title = document.querySelector("#title").value;
    const content = document.querySelector("#content").value;
    const post = { title, content };
    // 새로운 게시물 API 호출
    fetch(`${BASE_URL}/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(post)
    })
        .then(response => response.json())
        .then(post => {
            // 게시물 등록 후 목록 새로고침
            getPosts();
        });
}

// 게시물에 해당하는 댓글 가져오기
function getComments(postId) {
    return fetch(`${BASE_URL}:8081/comment?postId=${postId}`)
        .then(response => response.json());
}

// 댓글 DOM 요소 생성
function createCommentElement(comment) {
    const commentElement = document.createElement("div");
    commentElement.textContent = comment.content;
    commentElement.className = "comment";
    return commentElement;
}

/**
 *  comments API 서버로부터 응답이 없는 경우에도 post는 표시 가능하도록 try catch 구문 사용
 *  -> 댓글은 빈 배열로 전달
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

// 게시물과 댓글을 함께 렌더링
function renderPost(post) {
    const row = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.textContent = post.title;
    const contentCell = document.createElement("td");
    contentCell.textContent = post.content;
    const commentsCell = document.createElement("td");
    // 댓글 출력
    for (let comment of post.comments) {
        const commentElement = createCommentElement(comment);
        commentsCell.appendChild(commentElement);
    }
    row.appendChild(titleCell);
    row.appendChild(contentCell);
    row.appendChild(commentsCell);
    return row;
}

// 댓글 렌더링 함수
async function renderComments() {
    // 게시물 목록 DOM 요소 찾기
    const postList = document.querySelector("#post-list");
    // 게시물 목록 초기화
    postList.innerHTML = "";
    // 게시물과 댓글을 포함한 게시물 목록 가져오기
    const posts = await getPostsWithComments();
    // 게시물과 댓글을 함께 출력
    for (let post of posts) {
    const row = renderPost(post);
    postList.appendChild(row);
    }
    }
    
    // 폼 제출 이벤트 리스너
    const form = document.querySelector("form");
    form.addEventListener("submit", (event) => {
    // 기본 제출 동작 중지
    event.preventDefault();
    // 게시물 등록
    submitPost();
    // 댓글이 포함된 게시물 목록 새로고침
    renderComments();
    });
    
    // 초기 게시물 목록 불러오기
    getPosts();