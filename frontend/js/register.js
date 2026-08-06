const API_URL = "http://127.0.0.1:8000";

const registerForm = document.getElementById("registerForm");

registerForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const body = {

        full_name: document.getElementById("name").value,

        email: document.getElementById("email").value,

        password: document.getElementById("password").value

    };

    const response = await fetch(
        `${API_URL}/auth/register`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    const data = await response.json();

    if (response.ok) {

        document.getElementById("message").style.color = "green";
        document.getElementById("message").innerHTML =
            "Registration Successful";

        setTimeout(() => {
            window.location.href = "index.html";
        }, 1500);

    } else {

        document.getElementById("message").style.color = "red";

        document.getElementById("message").innerHTML =
            JSON.stringify(data.detail);

    }

});