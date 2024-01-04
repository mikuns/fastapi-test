async function submitForm(event) {
    event.preventDefault(); // Prevent default form submission

    const email = document.querySelector('input[name="email"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const confirmPassword = document.querySelector('input[name="confirmPassword"]').value;

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    const accountInfo = {
        email: email,
        password: password
    };

    try {
        const response = await fetch('/signup_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(accountInfo)
        });

        if (response.ok) {
            window.location.href = '/basic_info';
            console.log('Account Info submitted successfully');
        } else {
            throw new Error('Submission failed');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function redirectToSignin() {
    window.location.href = '/';
}


// Function to perform an authenticated API request with the stored access token
async function performAuthenticatedRequest(url, method, body = {}) {
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        console.error('Access token not found!');
        return;
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error('Request failed!');
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example usage: Creating a new post
async function createPost() {
    const postData = {
        title: 'New Post Title',
        content: 'Post Content'
        // Include other necessary fields for post creation
    };

    const createdPost = await performAuthenticatedRequest('/api/create_post', 'POST', postData);
    console.log('Created Post:', createdPost);
    // Handle the response as needed
}

// Example usage: Updating a post
async function updatePost(postId) {
    const updatedData = {
        title: 'Updated Title',
        content: 'Updated Content'
        // Include other necessary fields for updating the post
    };

    const updatedPost = await performAuthenticatedRequest(`/api/update_post/${postId}`, 'PUT', updatedData);
    console.log('Updated Post:', updatedPost);
    // Handle the response as needed
}

// Example usage: Deleting a post
async function deletePost(postId) {
    const deletedPost = await performAuthenticatedRequest(`/api/delete_post/${postId}`, 'DELETE');
    console.log('Deleted Post:', deletedPost);
    // Handle the response as needed
}


function togglePostForm() {
    var postForm = document.getElementById("postForm");
if (postForm.style.display === "none") {
    postForm.style.display = "block";
    } else {
    postForm.style.display = "none";
    }
}


    // Define the toggleDropdown function
function toggleDropdown() {
    var dropdownContent = document.getElementById('dropdownContent');
    if (dropdownContent.style.display === 'none') {
        dropdownContent.style.display = 'block';
    } else {
        dropdownContent.style.display = 'none';
    }
}

