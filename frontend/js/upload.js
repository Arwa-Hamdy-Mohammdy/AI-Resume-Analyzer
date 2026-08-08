const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

// Setup Logout
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("token");
        localStorage.removeItem("resume_id");
        localStorage.removeItem("last_match_result");
        localStorage.removeItem("target_job_id");
        window.location.href = "index.html";
    });
}


const form = document.getElementById("uploadForm");

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById("submitBtn") || form.querySelector("button");
        const messageEl = document.getElementById("message");
        const fileInput = document.getElementById("resume");

        if (!fileInput.files || fileInput.files.length === 0) {
            messageEl.style.color = "red";
            messageEl.textContent = "Please select a PDF file.";
            return;
        }

        const file = fileInput.files[0];

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            messageEl.style.color = "red";
            messageEl.textContent = "Only PDF files are supported.";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerText = "Analyzing Resume... ⏳";
        }
        messageEl.style.color = "#4f46e5";
        messageEl.innerHTML = "⏳ Uploading resume & running AI analysis... Please wait.";

        try {
            const response = await fetch(`${API_URL}/resumes/upload`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.status === 401) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Upload & Analyze Resume";
                }
                messageEl.style.color = "red";
                messageEl.innerHTML = "❌ Session expired. Please login again.";
                localStorage.removeItem("token");
                setTimeout(() => { window.location.href = "index.html"; }, 1500);
                return;
            }

            if (response.ok) {
                messageEl.style.color = "green";
                messageEl.innerHTML = "✅ Resume Uploaded & Analyzed Successfully! Redirecting...";

                if (data.id) {
                    localStorage.setItem("resume_id", data.id);
                }

                setTimeout(() => {
                    window.location.href = "analysis.html";
                }, 1000);
            } else {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Upload & Analyze Resume";
                }
                messageEl.style.color = "red";

                let errorMsg = "Upload failed.";
                if (typeof data.detail === "string") {
                    errorMsg = data.detail;
                } else if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(err => err.msg).join(", ");
                } else if (data.message) {
                    errorMsg = data.message;
                }
                messageEl.innerHTML = `❌ ${errorMsg}`;
            }
        } catch (error) {
            console.error("Upload error:", error);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = "Upload & Analyze Resume";
            }
            messageEl.style.color = "red";
            messageEl.innerHTML = "❌ Network error. Please ensure the backend server is running.";
        }
    });
}