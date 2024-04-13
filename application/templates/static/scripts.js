
// Add New Test
function addTest() {
    window.location.href = `/add_test`;
}

// Search Tests
function searchTests() {
    console.log("Search function called");
    var input, filter, cards, card, i, testName, testDescription;
    input = document.getElementById("searchInput").value.toUpperCase();
    cards = document.getElementById("tests-list").getElementsByClassName("card");
    for (i = 0; i < cards.length; i++) {
        card = cards[i];
        testName = card.querySelector(".card-title").textContent.toUpperCase();
        testDescription = card.querySelector(".card-text").textContent.toUpperCase();
        if (testName.indexOf(input) > -1 || testDescription.indexOf(input) > -1) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
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