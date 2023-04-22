const postList = document.getElementById("post-list");

async function getPosts() {
  const response = await fetch("http://localhost:8000/posts");
  const data = await response.json();
  return data;
}

function renderPost(post) {
  const item = document.createElement("li");
  const title = document.createElement("a");
  title.textContent = post.title;
  title.href = `/posts/${post.id}`;
  item.appendChild(title);
  return item;
}

async function renderPosts() {
  const posts = await getPosts();
  postList.innerHTML = "";
  posts.forEach(post => {
    const item = renderPost(post);
    postList.appendChild(item);
  });
}

renderPosts();
