
  // ======================
  // SIDEBAR TOGGLE
  // ======================
  const sidebar = document.getElementById("sidebar");
  const main = document.getElementById("main");
  const toggleBtn = document.getElementById("toggleSidebar");
  const dropdowns = document.querySelectorAll(".sidebar-item.dropdown");
  const user_id = localStorage.getItem("user_id");


  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("hidden");
    main.classList.toggle("expanded");
  });

  // Sidebar Dropdowns
  dropdowns.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      item.classList.toggle("dropdown-open");

      // Close other dropdowns
      dropdowns.forEach((other) => {
        if (other !== item) other.classList.remove("dropdown-open");
      });
    });
  });

  // Profile Dropdown
  const profile = document.querySelector(".profile");
  profile.addEventListener("click", (e) => {
    e.stopPropagation();
    profile.classList.toggle("active");
  });

  document.addEventListener("click", () => {
    profile.classList.remove("active");
  });
  // BUTTON CLICK → open file picker
document.getElementById("btnChangePhoto").addEventListener("click", function () {
    document.getElementById("profileFileInput").click();
});

// ON FILE SELECTED
document.getElementById("profileFileInput").addEventListener("change", async function (event) {
    const file = event.target.files[0];
    if (!file) return;

    //  Show preview instantly
    const imgPreview = document.getElementById("imgprofile");
    imgPreview.src = URL.createObjectURL(file);

    //  Send image to backend using PUT
    const formData = new FormData();
    formData.append("image", file);

    try {
        const userId = localStorage.getItem("user_id");

        const response = await fetch(`http://127.0.0.1:8000/update/profile/image/${userId}`, {
            method: "PUT",
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            //  Replace frontend image with new backend image URL
            imgPreview.src = result.imageUrl;

            // Save new image path locally (so all HTML pages update)
            localStorage.setItem("profileImage", result.imageUrl);

            alert("Photo mise à jour avec succès !");
        } else {
            alert("Erreur : " + result.message);
        }

    } catch (error) {
        console.error("Upload error:", error);
        alert("Impossible de télécharger l'image");
    }
});

//  Load saved image on every page
window.addEventListener("DOMContentLoaded", () => {
    const savedImg = localStorage.getItem("profileImage");
    if (savedImg) {
        document.getElementById("imgprofile").src = savedImg;
    }
});


  const fileInput = document.getElementById("profileFileInput").value;
  console.log(fileInput,'Image path')

  // ======================
  // FETCH USER INFO
  // ======================
  async function fetchUsers(user_id) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/user/by/${user_id}`);

      if (!response.ok) throw new Error("Failed to fetch user");

      const data = await response.json();
      const user = data.users;

      console.log("Fetched User:", user);

      if (!user) {
        console.warn("Invalid response:", data);
        return;
      }

      // Store minimal credentials
      const user_credential = {
        username: user.Username,
        role: user.Roles,
        image: user.Profile_link
      };
      console.log(user_credential);

      localStorage.setItem("user-form", JSON.stringify(user_credential));
      // Update HTML UI
      document.getElementById("user-email").textContent = user.Email || "example@gmail.com";
      document.getElementById("user-username").textContent = user.Username || "User";
      document.getElementById("user-username1").textContent = user.Username || "User1";
      document.getElementById("user-role").textContent = user.Roles || "role";
      document.getElementById("user-role1").textContent = user.Roles || "role1";

      document.getElementById("imgprofile").src =
        user.Profile_link || "image/person_1.jpg";

      document.getElementById("user-profile_link").src =
        user.Profile_link || "image/person_1.jpg";

      //  REMOVE INFINITE CALL
      // fetchUsers(user.UserID); (Removed)

    } catch (error) {
      console.error("Error fetching user:", error);
    }
  }

  // ======================
  // INIT
  // ======================
  console.log('the user id',user_id)
  if ( user_id) {
    fetchUsers(user_id);
  } else {
    console.warn("No user found in localStorage");
  }

async function logout() {
    // If no user ID, redirect immediately
    if (!user_id) {
        console.warn("No user found — redirecting to login");
        window.location.href = "login.html";
        return;
    }

    try {
        // Call backend logout API (send cookies)
        const response = await fetch(`http://127.0.0.1:8000/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include"  // important to send cookies
        });

        if (!response.ok) {
            console.error("Logout API failed:", response.statusText);
        }

    } catch (error) {
        console.error("Logout request error:", error);
    } finally {
        // Always clear localStorage and redirect
        localStorage.removeItem("user_id");
        localStorage.removeItem("user-form"); // optional
        // localStorage.clear(); // optional, clears everything

        window.location.href = "login.html";
    }
}
// Here is for the profile
const popup = document.getElementById("pass-change");
const btnOpen = document.getElementById("passchange");
const btnCancel = document.getElementById("cancelPass");
const btnSave = document.getElementById("savePass");

// Show popup
btnOpen.addEventListener("click", () => {
  popup.style.display = "flex";
});

// Hide popup
btnCancel.addEventListener("click", () => {
  popup.style.display = "none";
});

// SAVE password
btnSave.addEventListener("click", async () => {
  const currentPass = document.getElementById("currentPass").value;
  const newPass = document.getElementById("newPass").value;
  // <<< replace with real logged-in user id

  const data = {
    Password: currentPass,   // old password
    NewPassword: newPass     // new password
  };
  try {
    let res = await fetch(`http://127.0.0.1:8000/change/password/${user_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    alert(result.message);
    popup.style.display = "none";
    
  } catch (error) {
    alert("Error changing password");
  }
});
