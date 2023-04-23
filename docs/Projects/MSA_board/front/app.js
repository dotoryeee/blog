const BASE_URL = "http://localhost";

// 모든 post 가져오기
function getPosts() {
    fetch(`${BASE_URL}:8000/posts`)
        .then(response => response.json())
        .then(posts => {
            const postList = document.querySelector("#post-list");
            // 게시물 목록 초기화
            postList.innerHTML = "";
            // 각 게시물을 순회하며 화면에 출력
            for (const post of posts) {
                const postId = post.id
                const row = document.createElement("tr");
                const titleCell = document.createElement("td");
                titleCell.textContent = post.title;
                const contentCell = document.createElement("td");
                contentCell.textContent = post.content;
                row.appendChild(titleCell);
                row.appendChild(contentCell);
                postList.appendChild(row);
                renderComments(postId, row);
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
    fetch(`${BASE_URL}:8000/posts`, {
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

async function renderComments(postId, row) {
    const comments = await getComments(postId);
    const commentsTd = document.createElement("td");
    const commentsUl = document.createElement("ul"); 
    for (const comment of comments) {
      const commentLi = document.createElement("li");
      commentLi.textContent = comment.comment;
      commentsUl.appendChild(commentLi);
    }
    
    const addCommentCell = document.createElement("td"); 
    
    const addCommentForm = document.createElement("form");
    addCommentForm.classList.add("d-flex", "flex-row", "form");
    
    const addCommentInput = document.createElement("input");
    addCommentInput.type = "text";
    addCommentInput.className = "form-control";
    addCommentInput.placeholder = "Add new comment";
    
    const addCommentButton = document.createElement("button");
    addCommentButton.type = "submit";
    addCommentButton.className = "btn btn-primary";
    addCommentButton.textContent = "ADD";
    
    row.appendChild(commentsTd);
    commentsTd.appendChild(commentsUl);
    commentsUl.appendChild(addCommentCell);
    addCommentCell.appendChild(addCommentForm);
    addCommentForm.appendChild(addCommentInput);
    addCommentForm.appendChild(addCommentButton);
    
    // row.appendChild(addCommentCell);

    addCommentForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const content = addCommentInput.value;
        submitComment(postId, content);
        renderComments(postId, row); // 새로고침
    });
}

async function submitComment(postId, content) {
    const comment = { postId, comment: content };
    try {
      await fetch(`${BASE_URL}:8001/comments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(comment),
      });
    } catch (error) {
      console.error(`error submitting comment:`, error);
    }
  }
  

// post에 해당하는 comment 가져오기
async function getComments(postId) {
    const comments = await fetch(`${BASE_URL}:8001/comments?postId=${postId}`).then(response => response.json())
    // console.log(comments);
    return comments;
}


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