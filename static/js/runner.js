
var editor = ace.edit("editor");
var result = ace.edit("result");
var tests = ace.edit("tests-display");

editor.setOption("useSoftTabs", false);

editor.session.setMode("ace/mode/python");
tests.session.setMode("ace/mode/python");

result.setTheme("ace/theme/dawn")
result.setShowPrintMargin(false);
result.setHighlightActiveLine(false);
result.setReadOnly(true);
result.renderer.setShowGutter(false);

tests.setTheme("ace/theme/dawn")
tests.setShowPrintMargin(false);
tests.setHighlightActiveLine(false);
tests.setReadOnly(true);
tests.renderer.setShowGutter(false); 

document.getElementById("editor").style.fontSize = "16px";
document.getElementById("result").style.fontSize = "16px";

// handle code running
var running = false; // to prevent multiple threads from running at the same time

async function apiCall(url) {
    var code = editor.getValue();

    const response = await fetch(url, {
        method: "POST",
        body: code,
    });
    const data = await response.json();

    return data
}

async function run() {
    if (running) { return; }
    running = true;
    data = await apiCall("/api/challenges/run/" + challengeID);
    running = false;
    result.setValue(data["run_stage"]["output"]);
}

async function submit() {
    if (running) { return; }
    running = true;
    const data = await apiCall("/api/challenges/submit/" + challengeID);
    running = false;
    
    displaySubmit(data);
}

const modalElem = document.getElementById("modal");

const statusElem = document.getElementById("submit-result-status");
const scoreElem = document.getElementById("submit-result-score");

const stayButton = document.getElementById("stay-button");
const backButton = document.getElementById("back-button");

function getStatusText(userScore) {
    
    if (userScore === totalScore) {
        return "Excellent!";
    } else if (userScore === 0) {
        return "Try again?";
    } else {
        return "Well done";
    }
}

function displaySubmit(userScore) {

    if (!userScore) { userScore = 0; }
    
    statusElem.innerHTML = getStatusText(userScore);

    scoreElem.innerHTML = "You got " + userScore + " out of " + totalScore + ".";

    showModal();
}

function showModal() {
    modalElem.style.display = 'block';
}

stayButton.addEventListener('click', function() {
    modalElem.style.display = 'none';
});

backButton.addEventListener('click', function() {
    window.location = "/challenges";
});

// handle editor tools
const fileInputElem = document.getElementById("file-input");

fileInputElem.addEventListener("change", () => {
    const [file] = fileInputElem.files;
    const reader = new FileReader();

    reader.addEventListener(
        "load",
        () => {
            editor.setValue(reader.result);
            saveToLocalSorage();
        },
        false,
    );

    if (file) {
        reader.readAsText(file);
    }
})

function importCode() {
    fileInputElem.click();
}

function exportCode() {
    var downloadElem = document.createElement("a");
    downloadElem.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(editor.getValue()));
    downloadElem.setAttribute("download", "challenge.py")

    downloadElem.style.display = "none";
    document.body.appendChild(downloadElem);
    downloadElem.click();
    document.body.removeChild(downloadElem);
}

function resetCode() {
    editor.setValue(defaultCode);
    saveToLocalSorage();
}

function clearCode() {
    editor.setValue("");
    saveToLocalSorage();
}

// handle localstorage
if (localStorage.getItem(challengeID)) {
    editor.setValue(localStorage.getItem(challengeID));
}

function saveToLocalSorage() {
    localStorage.setItem(challengeID, editor.getValue());
}

document.getElementById("editor").onchange = saveToLocalSorage;

// handle tabs
function openTab(clickedElement) {
    var targetTab = clickedElement.innerHTML.toLowerCase();
    var tabElem = document.getElementById(targetTab);
    if (!tabElem) { return; }

    var contents = document.getElementsByClassName("tab-contents");
    var tabs = document.getElementsByClassName("tab");

    // clear tabs
    for (var tab = 0; tab < contents.length; tab++) {
        contents[tab].style.display = "none";
        tabs[tab].className = tabs[tab].className.replace(" active", "");
    }

    // set tab to active
    clickedElement.className += " active";
    tabElem.style.display = "flex";
}

document.addEventListener("mousedown", (event) => {
    openTab(event.target);
});

var defaultElem = document.getElementById("default");
openTab(defaultElem);
