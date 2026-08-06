const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "index.html";
    });
}

async function loadJobSelect() {
    const select = document.getElementById("jobSelect");

    // Restore cached match result if present
    const cachedMatch = localStorage.getItem("last_match_result");
    if (cachedMatch) {
        try {
            displayMatchData(JSON.parse(cachedMatch));
        } catch (e) {
            console.error("Error restoring cached match:", e);
        }
    }

    // Auto check & load latest uploaded resume if missing in local storage
    if (!localStorage.getItem("resume_id")) {
        try {
            const latestRes = await fetch(`${API_URL}/resumes/latest`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (latestRes.ok) {
                const latestData = await latestRes.json();
                localStorage.setItem("resume_id", latestData.id);
            }
        } catch (e) {
            console.error("Error pre-fetching latest resume:", e);
        }
    }

    try {
        const response = await fetch(`${API_URL}/jobs/`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) return;

        const jobs = await response.json();
        select.innerHTML = '<option value="">-- Select a Job --</option>';

        jobs.forEach(job => {
            const opt = document.createElement("option");
            opt.value = job.id;
            opt.textContent = `${job.title} (${job.company})`;
            select.appendChild(opt);
        });

    } catch (err) {
        console.error("Error loading job options:", err);
    }
}

async function handleMatching(e) {
    if (e) e.preventDefault();

    let resumeId = localStorage.getItem("resume_id");
    const jobId = document.getElementById("jobSelect").value;
    const msgEl = document.getElementById("matchMessage");
    const matchBtn = document.getElementById("matchBtn");
    const resultBox = document.getElementById("resultBox");

    if (!jobId) {
        msgEl.style.color = "red";
        msgEl.textContent = "❌ Please select a job position.";
        return;
    }

    // Fallback: fetch latest resume_id if missing in localStorage
    if (!resumeId) {
        try {
            const latestRes = await fetch(`${API_URL}/resumes/latest`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (latestRes.ok) {
                const latestData = await latestRes.json();
                resumeId = latestData.id;
                localStorage.setItem("resume_id", resumeId);
            }
        } catch (e) {
            console.error("Error fetching latest resume:", e);
        }
    }

    if (!resumeId) {
        msgEl.style.color = "red";
        msgEl.textContent = "❌ Please upload a resume first before running job matching.";
        return;
    }

    matchBtn.disabled = true;
    matchBtn.innerText = "Matching with AI... ⏳";
    msgEl.style.color = "#4f46e5";
    msgEl.textContent = "Calculating match score & skills gap...";
    resultBox.style.display = "none";

    try {
        const response = await fetch(`${API_URL}/matching/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
                resume_id: parseInt(resumeId),
                job_id: parseInt(jobId)
            })
        });

        if (response.status === 401) {
            msgEl.style.color = "red";
            msgEl.textContent = "❌ Session expired. Please log in again.";
            localStorage.removeItem("token");
            setTimeout(() => { window.location.href = "index.html"; }, 1500);
            return;
        }

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            msgEl.style.color = "red";
            msgEl.textContent = err.detail || "Matching failed.";
            matchBtn.disabled = false;
            matchBtn.innerText = "Calculate ATS Match Score 🎯";
            return;
        }

        const data = await response.json();
        console.log("Job Match API response:", data);

        // Save last match result in localStorage so it survives page reloads
        localStorage.setItem("last_match_result", JSON.stringify(data));

        msgEl.textContent = "";
        displayMatchData(data);

        // Smooth scroll to result
        try {
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (e) {
            console.error("Scroll error:", e);
        }

    } catch (err) {
        console.error("Matching fetch error:", err);
        msgEl.style.color = "red";
        msgEl.textContent = `❌ Network/Client Error: ${err.message || err}`;
    } finally {
        matchBtn.disabled = false;
        matchBtn.innerText = "Calculate ATS Match Score 🎯";
    }
}

function displayMatchData(data) {
    if (!data) return;
    const resultBox = document.getElementById("resultBox");
    if (!resultBox) return;

    resultBox.style.display = "block";

    // 1. Score
    try {
        const scoreEl = document.getElementById("scoreValue");
        if (scoreEl) scoreEl.textContent = `${data.match_score ?? 0}%`;
    } catch (e) {
        console.error("Score render error:", e);
    }

    // 2. Strengths
    try {
        const matchBox = document.getElementById("matchingSkillsBox");
        if (matchBox) {
            let strengths = data.strengths || data.matching_skills || [];
            renderSkills(matchBox, strengths, "matched", "No direct skill matches found.");
        }
    } catch (e) {
        console.error("Strengths render error:", e);
    }

    // 3. Missing skills
    try {
        const missingBox = document.getElementById("missingSkillsBox");
        if (missingBox) {
            renderSkills(missingBox, data.missing_skills, "missing", "No missing skills identified!");
        }
    } catch (e) {
        console.error("Missing skills render error:", e);
    }

    // 4. Recommendations
    try {
        const recsBox = document.getElementById("recommendationsBox");
        if (recsBox) {
            renderList(recsBox, data.recommendations, "No specific recommendations provided.");
        }
    } catch (e) {
        console.error("Recommendations render error:", e);
    }
}

const matchBtn = document.getElementById("matchBtn");
if (matchBtn) {
    matchBtn.addEventListener("click", handleMatching);
}

function renderSkills(container, skills, typeClass, fallback) {
    container.innerHTML = "";
    let list = skills;
    if (typeof skills === "string") {
        try {
            list = JSON.parse(skills);
        } catch (e) {
            list = skills.split(",");
        }
    }

    if (Array.isArray(list) && list.length > 0) {
        list.forEach(s => {
            const span = document.createElement("span");
            span.className = `match-badge ${typeClass}`;
            span.style.marginRight = "6px";
            span.style.marginBottom = "6px";
            span.style.display = "inline-flex";
            span.style.alignItems = "center";
            span.style.gap = "6px";

            const iconClass = typeClass === "matched" ? "fa-solid fa-circle-check" : "fa-solid fa-circle-xmark";
            const textContent = typeof s === "object" ? JSON.stringify(s) : s;

            span.innerHTML = `<i class="${iconClass}"></i> ${escapeHtml(textContent)}`;
            container.appendChild(span);
        });
    } else {
        container.textContent = fallback;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function renderList(container, data, fallbackText) {
    container.innerHTML = "";
    let list = data;

    if (typeof data === "string") {
        try {
            list = JSON.parse(data);
        } catch (e) {
            list = [data];
        }
    }

    if (Array.isArray(list) && list.length > 0) {
        const ul = document.createElement("ul");
        ul.style.paddingLeft = "20px";
        ul.style.margin = "0";

        list.forEach(item => {
            const li = document.createElement("li");
            li.style.marginBottom = "6px";
            li.textContent = typeof item === "object" ? JSON.stringify(item) : item;
            ul.appendChild(li);
        });
        container.appendChild(ul);
    } else if (typeof data === "string" && data.trim()) {
        container.textContent = data;
    } else {
        container.textContent = fallbackText;
    }
}

document.addEventListener("DOMContentLoaded", loadJobSelect);
