const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

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


async function loadJobs(queryParams = {}) {
    const jobsListEl = document.getElementById("jobsList");

    try {
        let url = `${API_URL}/jobs/`;
        
        // Build search URL if any parameters provided
        const params = new URLSearchParams();
        if (queryParams.q) params.append("q", queryParams.q);
        if (queryParams.location) params.append("location", queryParams.location);
        if (queryParams.experience_level) params.append("experience_level", queryParams.experience_level);

        if ([...params].length > 0) {
            url = `${API_URL}/jobs/search?${params.toString()}`;
        }

        const response = await fetch(url, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {
            jobsListEl.innerHTML = "<p style='color:red;'>Failed to load jobs.</p>";
            return;
        }

        const jobs = await response.json();

        if (!jobs || jobs.length === 0) {
            jobsListEl.innerHTML = "<p style='color:#666;'>No jobs matching your filter criteria.</p>";
            return;
        }

        jobsListEl.innerHTML = "";

        jobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "job-card";

            let skillsHtml = "";
            if (job.required_skills) {
                const skillsArr = typeof job.required_skills === "string" 
                    ? job.required_skills.split(",") 
                    : job.required_skills;
                
                skillsHtml = skillsArr
                    .map(s => `<span class="skill-tag">${s.trim()}</span>`)
                    .join("");
            }

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <h3>${job.title}</h3>
                    <span style="background:#eeeffe; color:#4f46e5; font-size:12px; font-weight:700; padding:4px 10px; border-radius:12px;">${job.experience_level || 'Junior'}</span>
                </div>
                <div class="company">🏢 ${job.company} • 📍 ${job.location || 'Remote'}</div>
                <p style="margin-bottom:12px; color:#475569; font-size:14px;">${job.description || ''}</p>
                <div class="skills">${skillsHtml}</div>
            `;

            jobsListEl.appendChild(card);
        });

    } catch (err) {
        console.error("Error loading jobs:", err);
        jobsListEl.innerHTML = "<p style='color:red;'>Network error while loading jobs.</p>";
    }
}

// Setup search & filter listeners
function setupSearchListeners() {
    const searchBtn = document.getElementById("searchBtn");
    const qInput = document.getElementById("searchQuery");
    const locInput = document.getElementById("searchLocation");
    const levelSelect = document.getElementById("searchLevel");

    const triggerSearch = () => {
        const queryParams = {
            q: qInput ? qInput.value.trim() : "",
            location: locInput ? locInput.value.trim() : "",
            experience_level: levelSelect ? levelSelect.value : ""
        };
        loadJobs(queryParams);
    };

    if (searchBtn) searchBtn.addEventListener("click", triggerSearch);
    if (qInput) qInput.addEventListener("keyup", (e) => { if (e.key === "Enter") triggerSearch(); });
    if (locInput) locInput.addEventListener("keyup", (e) => { if (e.key === "Enter") triggerSearch(); });
    if (levelSelect) levelSelect.addEventListener("change", triggerSearch);
}

const createJobForm = document.getElementById("createJobForm");
if (createJobForm) {
    createJobForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const msgEl = document.getElementById("jobFormMessage");
        const submitBtn = document.getElementById("createJobBtn");

        const payload = {
            title: document.getElementById("jobTitle").value,
            company: document.getElementById("company").value,
            location: document.getElementById("location").value,
            experience_level: document.getElementById("experienceLevel")?.value || "Junior",
            required_skills: document.getElementById("requiredSkills").value,
            description: document.getElementById("description").value
        };

        submitBtn.disabled = true;
        msgEl.style.color = "#4f46e5";
        msgEl.textContent = "Creating job listing...";

        try {
            const response = await fetch(`${API_URL}/jobs/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.status === 401) {
                msgEl.style.color = "red";
                msgEl.textContent = "❌ Session expired. Please log in again.";
                localStorage.removeItem("token");
                setTimeout(() => { window.location.href = "index.html"; }, 1500);
                return;
            }

            if (response.ok) {
                msgEl.style.color = "green";
                msgEl.textContent = "✅ Job created successfully!";
                createJobForm.reset();
                loadJobs();
            } else {
                const err = await response.json().catch(() => ({}));
                msgEl.style.color = "red";
                let errorMsg = "Failed to create job.";
                if (typeof err.detail === "string") {
                    errorMsg = err.detail;
                } else if (Array.isArray(err.detail)) {
                    errorMsg = err.detail.map(d => d.msg || JSON.stringify(d)).join(", ");
                }
                msgEl.textContent = `❌ ${errorMsg}`;
            }
        } catch (err) {
            console.error(err);
            msgEl.style.color = "red";
            msgEl.textContent = "Network error. Failed to post job.";
        } finally {
            submitBtn.disabled = false;
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadJobs();
    setupSearchListeners();
});
