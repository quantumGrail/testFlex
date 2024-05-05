
// Add New Test
function addTest() {
    window.location.href = `/add_test`;
}

// Search Existing Tests and Descriptions
function searchTests() {
    var input, cards, card, i, testName, testDescription, noResultsMessage;
    input = document.getElementById("searchInput").value.toUpperCase();
    cards = document.getElementById("tests-list").getElementsByClassName("card");
    noResultsMessage = document.getElementById("noResultsMessage");

    var foundMatches = false;

    for (i = 0; i < cards.length; i++) {
        card = cards[i];
        let header = card.querySelector(".card-header h5");
        if (header) {
            testName = header.textContent.toUpperCase();
        } else {
            testName = ""; 
        }
    
        testDescriptionElement = card.querySelector(".scrollable-text");
        if (testDescriptionElement) {
            testDescription = testDescriptionElement.textContent.toUpperCase();
        } else {
            testDescription = ""; 
        }
        
        if (testName.indexOf(input) > -1 || testDescription.indexOf(input) > -1) {
            card.style.display = "";
            foundMatches = true; 
        } else {
            card.style.display = "none";
        }
    }
    
    if (foundMatches) {
        noResultsMessage.style.display = "none";
    } else {
        noResultsMessage.style.display = "block";
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

// Toggle Test Steps
function toggleTestSteps(testId) {
    var testSteps = document.getElementById('testSteps_' + testId);
    if (testSteps.style.display === 'none') {
        testSteps.style.display = 'block';
    } else {
        testSteps.style.display = 'none';
    }
}