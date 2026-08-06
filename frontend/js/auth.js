const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const formData = new URLSearchParams();

        formData.append("username", email);
        formData.append("password", password);

        try {

            const response = await fetch(`${API_URL}/auth/login`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },

                body: formData

            });

            const data = await response.json();

            if (response.ok) {

                localStorage.setItem(
                    "token",
                    data.access_token
                );

                window.location.href = "dashboard.html";

            } else {

                document.getElementById("message").innerHTML =
                    data.detail || "Login failed";

            }

        }

        catch (error) {

            document.getElementById("message").innerHTML =
                "Server Error";

        }

    });

}