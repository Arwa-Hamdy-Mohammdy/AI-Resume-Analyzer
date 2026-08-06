const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const formData = new URLSearchParams();

    formData.append(
        "username",
        document.getElementById("email").value
    );

    formData.append(
        "password",
        document.getElementById("password").value
    );

    const response = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        }
    );

    const data = await response.json();

    if (response.ok) {

        localStorage.setItem(
            "token",
            data.access_token
        );

        document.getElementById("message").style.color = "green";
        document.getElementById("message").innerHTML =
            "Login Successful";

        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 1000);

    } else {

        document.getElementById("message").style.color = "red";
        document.getElementById("message").innerHTML =
            data.detail;

    }

});