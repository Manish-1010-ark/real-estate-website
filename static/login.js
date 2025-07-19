// login.js - Merged version

document.addEventListener("DOMContentLoaded", function () {
  // Configuration
  const BASE_URL = "https://wallstreetllp.com/api/auth"; // Production domain
  const ADMIN_EMAIL = "admin@kolkatahomes.com";
  const ADMIN_PASSWORD = "Admin@123";

  // Get stored authentication data
  const token = localStorage.getItem("access_token");
  const userRole = localStorage.getItem("user_role");
  
  // Get DOM elements
  const loginBtn = document.getElementById("login-btn");
  const profileBtn = document.getElementById("profile-btn");
  const profileLabel = document.getElementById("profile-label");
  const logoutBtn = document.getElementById("logout-btn");
  
  // Debug logging
  console.log("🔍 Login script loaded");
  console.log("Access_Token:", token);
  console.log("User Role:", userRole);
  
    // Handle UI state based on authentication status
  if (token) {
    // User is authenticated: hide login, show logout
    loginBtn && (loginBtn.style.display = "none");
    logoutBtn && (logoutBtn.style.display = "inline-block");
    
    // Only show profile-btn for admins
    if (userRole && userRole.toLowerCase() === "admin") {
      profileBtn && (profileBtn.style.display = "inline-block");
      profileBtn.href= "/admin/dashboard";
      profileLabel && (profileLabel.textContent = "Dashboard");
    } else {
      profileBtn && (profileBtn.style.display = "none");
    }
  } else {
    // Not authenticated: show login, hide profile & logout
    loginBtn && (loginBtn.style.display = "inline-block");
    profileBtn && (profileBtn.style.display = "none");
    logoutBtn && (logoutBtn.style.display = "none");
  }

  // Logout functionality
if (logoutBtn) {
  logoutBtn.addEventListener("click", function (e) {
    e.preventDefault();
    if (confirm("Are you sure you want to logout?")) {
      fetch('/api/logout', { method: 'POST', headers: getAuthHeaders() })
        .then(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("user_email");
          localStorage.removeItem("user_role");
          localStorage.clear();
          sessionStorage.clear();
          alert("Logged out successfully.");
          window.location.replace("/login");
        })
        .catch(err => {
          console.error("Logout error", err);
          localStorage.clear();
          sessionStorage.clear();
          window.location.replace("/login");
        });
    }
  });
}

// Add this function to login.js
function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`
  };
}

  
  // Login form submission handler (prioritizing login.js approach)
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      
      // Get form data - flexible ID detection
      const emailField = document.getElementById("email") || document.getElementById("login-email");
      const passwordField = document.getElementById("password") || document.getElementById("login-password");
      
      if (!emailField || !passwordField) {
        console.error("Login form fields not found");
        return;
      }
      
      const email = emailField.value.trim();
      const password = passwordField.value;
      
      try {
        // Send login request using BASE_URL from login.html
        const res = await fetch(`${BASE_URL}/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ email, password })
        });
        
        const result = await res.json();
        
        if (res.ok && result.success) {
          const accessToken = result.data.access_token || result.data.accessToken;
          const refreshToken = result.data.refresh_token || result.data.refreshToken;
          const userRole = result.data.user.role;
          
          // Store authentication data
          localStorage.setItem("access_token", accessToken);
          localStorage.setItem("refresh_token", refreshToken);
          localStorage.setItem("user_email", result.data.user.email || email);
          localStorage.setItem("user_role", userRole);
          
          alert("Login successful!");
          
          console.log("User role from server:", userRole);
          // Redirect based on user role
          if (userRole.toLowerCase() === "admin") {
            window.location.replace("/admin/dashboard");
          } else {
            console.log("Redirecting to /home");
            window.location.replace("/home");
          }
        } else {
          alert(result.error || "Login failed");
        }
      } catch (error) {
        console.error("Login error:", error);
        alert("Something went wrong during login.");
      }
    });
  }
  
  // Sign up form handler (from login.html)
  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      
      const name = this.name.value;
      const email = this.email.value;
      const password = this.password.value;
        const mobile = signupForm.elements["mobile"].value.trim(); // ✅ add this
      const role = "customer";
      
      // Check if trying to register with admin email
      if (email === ADMIN_EMAIL) {
        alert("This email is reserved for admin use only.");
        return;
      }
      
      try {
        const res = await fetch(`${BASE_URL}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password, mobile, role }),
        });
        
        const result = await res.json();
        
        if (res.ok && result.success) {
          alert("Signup successful! You can now log in.");
          this.reset();
        } else {
          alert(result.error || "Signup failed");
        }
      } catch (err) {
        console.error("Signup error:", err);
        alert("Something went wrong during signup.");
        window.addEventListener('DOMContentLoaded', () => {
        document.getElementById('login-email').value = '';
        document.getElementById('login-password').value = '';
});

      }
    });
  }
});