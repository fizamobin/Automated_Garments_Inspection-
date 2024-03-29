const adminButton = document.getElementById('admin-btn');

 // Function to handle login form submission
function handleLogin(event) {
    event.preventDefault();
  
    // Get user input values
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    // Retrieve user data from local storage
    const users = JSON.parse(localStorage.getItem('users') || '[]');
  
    // Check if the provided username and password match any user
    const user = users.find(user => user.username === username && user.password === password);
    if (user) {
      window.location.href = "../templates/ADMIN.html";
    } else {
      alert('Invalid credentials. Please try again.');
    }
  }
  
  // Add event listener to the login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }

  adminButton.addEventListener('click', function() {
    // Redirect to the admin panel (replace 'admin-panel.html' with actual admin panel URL)
    window.location.href = ("../templates/index.html");
  });
 