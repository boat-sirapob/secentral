
var bodyElement = document.getElementById("challenges-body");
var sortKey = "title";
var ascending = true;

var data;

// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function fetchChallenges(difficulty) {
    // call internal API to get challenges by difficulty
    const apiURL = "/api/challenges/";
    const response = await fetch(apiURL + difficulty);
    data = await response.json();
}

async function populateChallenges() {
    const difficultyElement = document.getElementById("difficulty")
    const difficulty = difficultyElement.value;

    await fetchChallenges(difficulty);

    sortData(sortKey);

    populateTable();
}

function populateTable() {
    // clear table
    bodyElement.innerHTML = "";
    
    // fill table with data
    for (i in data) {
        var challenge = data[i];
        var row = bodyElement.insertRow();

        for (detail in challenge) {
            var content = document.createTextNode(challenge[detail]);
            if (detail === "_id") { content = document.createTextNode(parseInt(i)+1); }
            if (detail === "difficulty") {
                content = document.createElement("meter");
                content.appendChild(document.createTextNode(challenge["difficulty"]));
                content.setAttribute("min", 0);
                content.setAttribute("max", 5);
                content.setAttribute("low", 1.5);
                content.setAttribute("high", 3.5)
                content.setAttribute("optimum", 0);
                content.setAttribute("value", challenge["difficulty"]);
            }
            if (detail == "completed") {
                if (challenge["completed"] === false) {
                    content = document.createTextNode("");
                } else {
                    content = document.createTextNode(challenge["completed"] + "/" + challenge["score"]);
                }
            }

            var cell = row.insertCell();
            cellContents = document.createElement("a");
            cellContents.setAttribute("href", "/challenges/" + challenge["_id"])
            cellContents.appendChild(content)
            cell.appendChild(cellContents);
        }
    }
}

function sortData(key, reverse=false) {
    data.sort((a, b) => {
        if (a[key] > b[key]) { return 1; }
        else { return -1; }
    })
    if (reverse) { data.reverse(); }
}

var tableHeaderElements = document.querySelectorAll("th");
for (var i = 0; i < tableHeaderElements.length; i++) {
    var header = tableHeaderElements[i];

    if (header.innerHTML == "#") { continue; }

    header.addEventListener("click", (event) => {
        tempSortKey = event.target.innerHTML.toLowerCase();
        if (sortKey == tempSortKey) {
            ascending = !ascending;
        } else {
            ascending = true;
        }
        sortKey = tempSortKey;
        sortData(sortKey, !ascending);
        populateTable();
    });
}

populateChallenges()