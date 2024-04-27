
// Add New Test
function addTest() {
    window.location.href = `/add_test`;
}

function searchTests() {
    var input, cards, card, i, testName, testDescription, noResultsMessage;
    input = document.getElementById("searchInput").value.toUpperCase();
    cards = document.getElementById("tests-list").getElementsByClassName("card");
    noResultsMessage = document.getElementById("noResultsMessage");

    // Flag to keep track of whether any matches are found
    var foundMatches = false;

    for (i = 0; i < cards.length; i++) {
        card = cards[i];
        testName = card.querySelector(".card-header strong").textContent.toUpperCase();
        testDescription = card.querySelector(".card-body .card-text:first-of-type").textContent.toUpperCase();
        if (testName.indexOf(input) > -1 || testDescription.indexOf(input) > -1) {
            card.style.display = "";
            foundMatches = true; // Set foundMatches to true if at least one match is found
        } else {
            card.style.display = "none";
        }
    }

    // Display or hide the "No results found" message based on whether any matches were found
    if (!foundMatches) {
        noResultsMessage.style.display = "block"; // Show the message
    } else {
        noResultsMessage.style.display = "none"; // Hide the message
    }
}

// Edit Existing Test
function editTest(testId) {
    window.location.href = `/edit_test/${testId}`;
}

// Delete Existing Test
function deleteTest(testId) {
    fetch(`/delete_test/${testId}`, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            console.error('Failed to delete test');
        }
    })
    .catch(error => {
        console.error('Error:', error)
    });
}