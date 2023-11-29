
var openMenuButton = document.getElementsByClassName('open-menu-button')[0];
var menuContent = document.getElementsByClassName('dropdown-content')[0];

var modal = document.getElementById('modal');
var closeModal = document.getElementById('close-modal');

var editPhotoButton = document.getElementById('edit-photo-button');
var editThemeButton = document.getElementById('edit-theme-button')

// profile picture
var imageInput = document.getElementById('file-input');
var previewImage = document.getElementById('preview-img');

// handle drop down menu
openMenuButton.addEventListener('click', function () {
    menuContent.style.display = menuContent.style.display == 'block' ? 'none' : 'block';
});

imageInput.onchange = function (event) {
    const [file] = imageInput.files;
    if (file) {
        previewImage.src = URL.createObjectURL(file)
    }
}

// handle opening menu
function switchMenu(menu_id) {
    var menuElem = document.getElementById(menu_id);
    if (!menuElem) { return; }

    var contents = document.getElementsByClassName("menu");

    // clear menu
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = "none";
    }

    menuElem.style.display = "flex";
}

function openMenu(menu_id) {
    switchMenu(menu_id);
    modal.style.display = 'block';
}

document.addEventListener('click', function(event) {
    if (menuContent.style.display != 'none' && event.target != openMenuButton) {
        menuContent.style.display = 'none';
    }
})

closeModal.addEventListener('click', function() {
    modal.style.display = 'none';
});

editPhotoButton.onclick = () => openMenu("edit-photo-menu");
editThemeButton.onclick = () => openMenu("edit-theme-menu");

switchMenu("settings-menu");