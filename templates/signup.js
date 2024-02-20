// Function to handle sign-up form submission and save user information to local storage
function handleSignUp(event) {
    event.preventDefault();
  
    // Get user input values
    const fullName = document.getElementById('fullname').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
  
    // Validate if all fields are not empty
    if (!fullName || !username || !email || !password) {
      alert('Please fill in all fields to sign up.');
      return;
    }
  
    // Retrieve existing user data from local storage or initialize an empty array
    const users = JSON.parse(localStorage.getItem('users') || '[]');
  
    // Check if the username or email already exists
    if (users.some(user => user.username === username || user.email === email)) {
      alert('Username or email already exists. Please choose a different one.');
      return;
    }
  
    // Add the new user to the array
    users.push({ fullName, username, email, password });
  
    // Save the updated user data back to local storage
    localStorage.setItem('users', JSON.stringify(users));
  
    // Clear the form fields after successful sign-up
    document.getElementById('fullname').value = '';
    document.getElementById('username').value = '';
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
  
    alert('Sign up successful. Please log in using your credentials.');
    // Optionally, redirect to the login page after successful sign-up
    // window.location.href = 'login.html';
  }
  
  // Add event listener to the sign-up form
  document.getElementById('signup-form').addEventListener('submit', handleSignUp);