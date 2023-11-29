
const postList = document.getElementById("post-list");

// populate the list of posts
function populatePosts(data) {
    // clear posts first
    postList.innerHTML = '';

    console.log(data);

    for (var i = 0; i < data.length; i++) {
        var post = data[i];

        var html = `
        <a href="/forum/post/${post.post_id}">
            <h4 class="title">
                ${post.title}
            </h4>
            <div class="bottom">
                <p class="timestamp">
                    ${new Date(post.created_at).toLocaleString()}
                </p>
                <p class="comment-count">
                    ${post.comments.length} comments
                </p>
                <p class="author">
                    Posted by: ${post.author_name}
                </p>
            </div>
        </a>
        `
        postList.insertAdjacentHTML('beforeend', html);
    }
}

// --on load--

// handle searching
var searchButton = document.getElementById('search-button');
var searchInput = document.getElementById('search-input');

searchButton.addEventListener('click', function () {
    var searchTerm = searchInput.value.toLowerCase();

    changePage(page, sort_by, searchTerm);
});

if (loggedIn) {

    // to display form for making a new post
    var newPostButton = document.getElementById('new-post-button');
    var newPostModal = document.getElementById('new-post-modal');
    var closeModal = document.getElementById('close-modal');
    
    newPostButton.addEventListener('click', function () {
        // Show the modal
        newPostModal.style.display = 'block';
    });
    
    // Close the modal when the close button is clicked
    closeModal.addEventListener('click', function () {
        newPostModal.style.display = 'none';
    });
    
    // Close the modal when clicking outside the modal content
    window.addEventListener('click', function (event) {
        if (event.target === newPostModal) {
            newPostModal.style.display = 'none';
        }
    });
}

// handle pagination
function changePage(page, sort_by, search) {
    var url = "/forum?page=" + page + "&" + "sort_by=" + sort_by;
    if (search != undefined) { url += "&search=" + search; }

    window.location.href = url;
}

// handle sorting
var sortTopButton = document.getElementById('sort-top');
var sortRecentButton = document.getElementById('sort-recent');
var sortOldButton = document.getElementById('sort-old');

function sortPostsByComments() {
    changePage(page, "top");
}

function sortPostsByRecent() {
    changePage(page, "recent");
}

function sortPostsByOld() {
    changePage(page, "old");
}

sortTopButton.addEventListener('click', sortPostsByComments);
sortRecentButton.addEventListener('click', sortPostsByRecent);
sortOldButton.addEventListener('click', sortPostsByOld);


populatePosts(posts);