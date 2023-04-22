const BASE_URL = "http://localhost:8000";

function getPosts() {
    fetch(`${BASE_URL}/posts`)
        .then(response => response.json())
        .then(posts => {
            const postList = document.querySelector("#post-list");
            postList.innerHTML = "";
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

function submitPost() {
    const title = document.querySelector("#title").value;
    const content = document.querySelector("#content").value;
    const post = { title, content };
    fetch(`${BASE_URL}/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(post)
    })
        .then(response => response.json())
        .then(post => {
            getPosts();
        });
}

const form = document.querySelector("form");
form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitPost();
});

getPosts();
