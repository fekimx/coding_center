
document.addEventListener('DOMContentLoaded', function() {
    // If any of the edit buttons is clicked, then get the post id
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = btn.dataset.post;
            // Get the content of the post
            const content = document.querySelector(`.content[data-post="${postId}"]`);
            // Display the textarea and save button
            document.querySelector(`.update[data-post="${postId}"]`).style.display = 'block';
            // Fill save button with the post
            document.querySelector(`.textarea[data-post="${postId}"]`).value = content.textContent;
            
            // When save button is clicked, call update function
            document.querySelector(`.save-btn[data-post="${postId}"]`).addEventListener('click', () => 
                updatePost(postId, content)
            );
            return false;
        })
    })

    //If any of the like buttons is clicked, then get the post id
    document.querySelectorAll('.like-btn').forEach(btn => {
        const postId = btn.dataset.post;
        // When like button is clicked, call updateLike function
        btn.addEventListener('click', () => updateLike(postId)); 
        return false;
    })
})
function updateLike(postId) {
    // Store the label element in label variable
    const label = document.querySelector(`.like-label[data-post="${postId}"]`);
    // Make a GET request
    fetch(`/like/${postId}`)
    // Convert the response to json format
    .then(response => response.json())
    // Change the text of the label to display the number of people that liked the post
    .then(data => {
        label.innerHTML = data["likers"].length
        return false;
    })
}

function updatePost(postId, content) {
    // Get the value of the current value of the textarea
    const new_content = document.querySelector(`.textarea[data-post="${postId}"]`).value;
    
    // Make a PUT request because content will change in the server side(database)
    fetch(`/update/${postId}`, {
        method: "PUT",
        body: JSON.stringify({
            'new_content': new_content
        })
    })
    // Convert to json format
    .then(response => response.json())
    // Change the content of the post and display on the page
    .then(data => {
        content.innerHTML = data["content"];
        return false;
    })
    // Hide the textarea and save buttons
    document.querySelector(`.update[data-post="${postId}"]`).style.display = 'none'; 
}