// 기본 URL 설정
const BASE_URL = "http://localhost:8000";

// 모든 post 가져오기
function getPosts() {
    // post API 호출
    fetch(`${BASE_URL}/posts`)
        .then(response => response.json())
        .then(posts => {
            // post 목록 DOM 요소 찾기
            const postList = document.querySelector("#post-list");
            // post 목록 초기화
            postList.innerHTML = "";
            // post 목록 생성 및 출력
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

// 새로운 post 등록
function submitPost() {
    // 입력된 제목 및 내용 가져오기
    const title = document.querySelector("#title").value;
    const content = document.querySelector("#content").value;
    const post = { title, content };
    // 새로운 post API 호출
    fetch(`${BASE_URL}/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(post)
    })
        .then(response => response.json())
        .then(post => {
            // post 등록 후 목록 새로고침
            getPosts();
        });
}

// post에 해당하는 comment 가져오기
function getComments(postId) {
    return fetch(`${BASE_URL}:8081/comment?postId=${postId}`)
        .then(response => response.json());
}

// comment DOM 요소 생성
function createCommentElement(comment) {
    const commentElement = document.createElement("div");
    commentElement.textContent = comment.content;
    commentElement.className = "comment";
    return commentElement;
}

/**
 *  comments API 서버로부터 응답이 없는 경우에도 post는 표시 가능하도록 try catch 구문 사용
 *  -> comment은 빈 배열로 전달
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
    const row = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.textContent = post.title;
    const contentCell = document.createElement("td");
    contentCell.textContent = post.content;
    const commentsCell = document.createElement("td");
    // comment 출력
    for (let comment of post.comments) {
        const commentElement = createCommentElement(comment);
        commentsCell.appendChild(commentElement);
    }
    row.appendChild(titleCell);
    row.appendChild(contentCell);
    row.appendChild(commentsCell);
    return row;
}

// comment 렌더링 함수
async function renderComments() {
    // post 목록 DOM 요소 찾기
    const postList = document.querySelector("#post-list");
    // post 목록 초기화
    postList.innerHTML = "";
    // post과 comment을 포함한 post 목록 가져오기
    const posts = await getPostsWithComments();
    // post과 comment을 함께 출력
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
    // post 등록
    submitPost();
    // comment이 포함된 post 목록 새로고침
    renderComments();
    });
    
    // 초기 post 목록 불러오기
    getPosts();