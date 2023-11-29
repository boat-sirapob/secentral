
var modal = document.getElementById('modal');
var closeModal = document.getElementById('close-modal');

function switchMenu(menu_id, comment_id) {
    var menuElem = document.getElementById(menu_id);
    if (!menuElem) { return; }

    var contents = document.getElementsByClassName("menu");

    // clear menu
    for (var i = 0; i < contents.length; i++) {
        var menu = contents[i];
        menu.querySelector("input[name='comment_id']").value = comment_id;
        menu.style.display = "none";
    }

    if (menu_id === "edit-comment-menu") {
        var comment = document.querySelector(`[id='${comment_id}']`);
        menuElem.querySelector("textarea[name='new_content']").value = comment.querySelector(".comment-content p").innerText;
    }

    menuElem.style.display = "flex";
}

function openMenu(menu_id, comment_id) {
    switchMenu(menu_id, comment_id);
    modal.style.display = 'block';
}

// handle buttons for each comment
document.addEventListener('click', function (event) {
    if (event.target.closest('.open-menu-button')) {
        var comment = event.target.closest('.comment');
        var menuContent = comment.querySelector('.dropdown-content');
        menuContent.style.display = menuContent.style.display == 'block' ? 'none' : 'block';
    }
});

closeModal.addEventListener('click', function() {
    modal.style.display = 'none';
});