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
        window.location.href = "index.html";
    });
}

async function loadAnalysis() {
    const resumeId = localStorage.getItem("resume_id");
    const loadingEl = document.getElementById("loading");
    const errorEl = document.getElementById("errorState");
    const contentEl = document.getElementById("analysisContent");
    const errorText = document.getElementById("errorText");

    try {
        let response;
        if (resumeId) {
            response = await fetch(`${API_URL}/resumes/${resumeId}/analysis`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
        }

        // Fallback to latest analysis if resumeId wasn't found or returned error
        if (!response || !response.ok) {
            response = await fetch(`${API_URL}/resumes/latest/analysis`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
        }

        if (response && response.status === 401) {
            loadingEl.style.display = "none";
            errorEl.style.display = "block";
            errorText.textContent = "Session expired. Please log in again.";
            localStorage.removeItem("token");
            setTimeout(() => { window.location.href = "index.html"; }, 1500);
            return;
        }

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            loadingEl.style.display = "none";
            errorEl.style.display = "block";
            errorText.textContent = errData.detail || "No uploaded resume analysis found. Please upload a PDF resume first.";
            return;
        }

        const data = await response.json();

        loadingEl.style.display = "none";
        contentEl.style.display = "block";

        // Summary
        document.getElementById("summaryBox").textContent = data.summary || "No summary provided.";

        // Skills (can be JSON array or JSON string or string)
        const skillsContainer = document.getElementById("skillsBox");
        skillsContainer.innerHTML = "";
        let skillsList = parseJsonOrArray(data.skills);

        if (Array.isArray(skillsList) && skillsList.length > 0) {
            skillsList.forEach(skill => {
                const badge = document.createElement("span");
                badge.className = "badge";
                badge.textContent = skill;
                skillsContainer.appendChild(badge);
            });
        } else if (typeof skillsList === "string" && skillsList.trim()) {
            const badge = document.createElement("span");
            badge.className = "badge";
            badge.textContent = skillsList;
            skillsContainer.appendChild(badge);
        } else {
            skillsContainer.textContent = "No skills extracted.";
        }

        // Education
        const eduContainer = document.getElementById("educationBox");
        let eduList = parseJsonOrArray(data.education);
        renderListOrText(eduContainer, eduList, "No education history listed.");

        // Experience
        const expContainer = document.getElementById("experienceBox");
        let expList = parseJsonOrArray(data.experience);
        renderListOrText(expContainer, expList, "No work experience listed.");

    } catch (err) {
        console.error("Error loading analysis:", err);
        loadingEl.style.display = "none";
        errorEl.style.display = "block";
        errorText.textContent = "Network error. Failed to connect to server.";
    }
}

function parseJsonOrArray(val) {
    if (!val) return [];
    if (Array.isArray(val)) return val;
    if (typeof val === "object") return val;
    try {
        return JSON.parse(val);
    } catch (e) {
        return val;
    }
}

function renderListOrText(container, data, fallbackText) {
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
        ul.style.listStyle = "none";
        ul.style.paddingLeft = "0";

        list.forEach(item => {
            const li = document.createElement("li");
            li.style.marginBottom = "10px";
            li.style.padding = "10px 14px";
            li.style.background = "#ffffff";
            li.style.borderRadius = "8px";
            li.style.borderLeft = "4px solid #4f46e5";
            li.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)";
            li.innerHTML = formatItemHtml(item);
            ul.appendChild(li);
        });
        container.appendChild(ul);
    } else if (typeof data === "string" && data.trim()) {
        container.textContent = data;
    } else {
        container.textContent = fallbackText;
    }
}

function formatItemHtml(item) {
    if (typeof item === "string") {
        try {
            item = JSON.parse(item);
        } catch (e) {
            return escapeHtml(item);
        }
    }

    if (typeof item !== "object" || item === null) {
        return escapeHtml(String(item));
    }

    // Education formatting
    if (item.degree || item.institution || item.field) {
        let titleParts = [];
        if (item.degree && item.field) {
            titleParts.push(`${item.degree} in ${item.field}`);
        } else if (item.degree) {
            titleParts.push(item.degree);
        } else if (item.field) {
            titleParts.push(item.field);
        }

        let html = `<strong>🎓 ${escapeHtml(titleParts.join(" ") || "Education")}</strong>`;
        if (item.institution) {
            html += ` — <span style="color:#334155;">${escapeHtml(item.institution)}</span>`;
        }
        if (item.graduation_date || item.year || item.date) {
            html += ` <span style="color:#64748b; font-weight:500;">(${escapeHtml(item.graduation_date || item.year || item.date)})</span>`;
        }
        return html;
    }

    // Work Experience formatting
    if (item.title || item.role || item.position || item.company) {
        const title = item.title || item.role || item.position || "Position";
        let html = `<strong>💼 ${escapeHtml(title)}</strong>`;

        if (item.company || item.organization) {
            html += ` — <span style="color:#334155;">${escapeHtml(item.company || item.organization)}</span>`;
        }
        if (item.duration || item.dates || item.period) {
            html += ` <span style="color:#64748b; font-weight:500;">(${escapeHtml(item.duration || item.dates || item.period)})</span>`;
        }
        if (item.project && item.project.trim()) {
            const proj = item.project.trim();
            if (proj.startsWith("http://") || proj.startsWith("https://")) {
                html += `<div style="margin-top:4px; font-size:13px; color:#4f46e5;">🔗 Project: <a href="${escapeHtml(proj)}" target="_blank" style="color:#4f46e5; text-decoration:underline;">${escapeHtml(proj)}</a></div>`;
            } else {
                html += `<div style="margin-top:4px; font-size:13px; color:#475569;">🔗 Project: ${escapeHtml(proj)}</div>`;
            }
        } else if (item.description && item.description.trim()) {
            html += `<div style="margin-top:4px; font-size:13px; color:#475569;">${escapeHtml(item.description.trim())}</div>`;
        }
        return html;
    }

    // Generic Object formatting
    const entries = Object.entries(item).filter(([k, v]) => v);
    return entries.map(([k, v]) => `<strong>${escapeHtml(k.replace(/_/g, ' '))}:</strong> ${escapeHtml(String(v))}`).join(" | ");
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", loadAnalysis);
