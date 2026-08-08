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

let currentAnalysisData = null;
let currentResumeId = null;
let scoreChart = null;

async function loadAnalysis() {
    currentResumeId = localStorage.getItem("resume_id");
    const loadingEl = document.getElementById("loading");
    const errorEl = document.getElementById("errorState");
    const contentEl = document.getElementById("analysisContent");
    const errorText = document.getElementById("errorText");

    try {
        let response;
        if (currentResumeId) {
            response = await fetch(`${API_URL}/resumes/${currentResumeId}/analysis`, {
                method: "GET",
                headers: { Authorization: `Bearer ${token}` }
            });
        }

        if (!response || !response.ok) {
            response = await fetch(`${API_URL}/resumes/latest/analysis`, {
                method: "GET",
                headers: { Authorization: `Bearer ${token}` }
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

        currentAnalysisData = await response.json();
        if (currentAnalysisData && currentAnalysisData.resume_id) {
            currentResumeId = currentAnalysisData.resume_id;
            localStorage.setItem("resume_id", currentResumeId);
        }

        loadingEl.style.display = "none";
        contentEl.style.display = "block";

        renderAnalysisUI(currentAnalysisData);

    } catch (err) {
        console.error("Error loading analysis:", err);
        loadingEl.style.display = "none";
        errorEl.style.display = "block";
        errorText.textContent = "Network error. Failed to connect to server.";
    }
}

function renderAnalysisUI(data) {
    // Summary
    document.getElementById("summaryBox").textContent = data.summary || "No summary provided.";

    // Score
    const scoreVal = data.overall_score || 75;
    const scoreEl = document.getElementById("scoreVal");
    if (scoreEl) scoreEl.textContent = scoreVal;
    renderScoreGaugeChart(scoreVal);

    // Technical & Soft Skills
    renderEditableBadges(document.getElementById("techSkillsBox"), parseJsonOrArray(data.technical_skills), "tech");
    renderEditableBadges(document.getElementById("softSkillsBox"), parseJsonOrArray(data.soft_skills), "soft");

    // Strengths & Weaknesses
    renderListOrText(document.getElementById("strengthsBox"), parseJsonOrArray(data.strengths), "No specific strengths listed.");
    renderListOrText(document.getElementById("weaknessesBox"), parseJsonOrArray(data.weaknesses), "No critical weaknesses found.");

    // Education & Experience
    renderListOrText(document.getElementById("educationBox"), parseJsonOrArray(data.education), "No education history listed.");
    renderListOrText(document.getElementById("experienceBox"), parseJsonOrArray(data.experience), "No work experience listed.");
}

function renderScoreGaugeChart(score) {
    const canvas = document.getElementById("scoreGaugeChart");
    if (!canvas) return;
    if (scoreChart) scoreChart.destroy();

    const color = score >= 75 ? '#10b981' : (score >= 50 ? '#f59e0b' : '#ef4444');

    scoreChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: ['#ffffff', 'rgba(255, 255, 255, 0.2)'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { tooltip: { enabled: false }, legend: { display: false } }
        }
    });
}

function renderEditableBadges(container, skillsList, category) {
    if (!container) return;
    container.innerHTML = "";
    const list = Array.isArray(skillsList) ? skillsList : [skillsList];

    if (list.length > 0 && list[0]) {
        list.forEach(skill => {
            const badge = document.createElement("span");
            badge.style.cssText = "display: inline-flex; align-items: center; gap: 6px; background: white; border: 1px solid var(--border-color); padding: 4px 12px; border-radius: 16px; font-size: 13px; font-weight: 600; color: var(--text-dark); margin-right: 6px; margin-bottom: 6px;";
            badge.innerHTML = `<span>${escapeHtml(skill)}</span> <i class="fa-solid fa-xmark remove-skill-btn" style="color: #ef4444; cursor: pointer; font-size: 11px;"></i>`;

            const removeBtn = badge.querySelector(".remove-skill-btn");
            removeBtn.addEventListener("click", () => handleRemoveSkill(skill, category));

            container.appendChild(badge);
        });
    } else {
        container.innerHTML = `<span style="color:#64748b; font-size:13px;">No ${category} skills added.</span>`;
    }
}

async function handleRemoveSkill(skillToRemove, category) {
    if (!currentAnalysisData || !currentResumeId) return;

    let techSkills = parseJsonOrArray(currentAnalysisData.technical_skills);
    let softSkills = parseJsonOrArray(currentAnalysisData.soft_skills);

    if (category === "tech") {
        techSkills = techSkills.filter(s => s !== skillToRemove);
    } else {
        softSkills = softSkills.filter(s => s !== skillToRemove);
    }

    await saveUpdatedSkills(techSkills, softSkills);
}

async function handleAddSkill(category) {
    const newSkill = prompt(`Enter new ${category === 'tech' ? 'Technical' : 'Soft'} skill:`);
    if (!newSkill || !newSkill.trim()) return;

    let techSkills = parseJsonOrArray(currentAnalysisData.technical_skills);
    let softSkills = parseJsonOrArray(currentAnalysisData.soft_skills);

    if (category === "tech") {
        if (!techSkills.includes(newSkill.trim())) techSkills.push(newSkill.trim());
    } else {
        if (!softSkills.includes(newSkill.trim())) softSkills.push(newSkill.trim());
    }

    await saveUpdatedSkills(techSkills, softSkills);
}

async function saveUpdatedSkills(techSkills, softSkills) {
    try {
        const response = await fetch(`${API_URL}/resumes/${currentResumeId}/skills`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
                technical_skills: techSkills,
                soft_skills: softSkills
            })
        });

        if (response.ok) {
            currentAnalysisData = await response.json();
            renderAnalysisUI(currentAnalysisData);
        } else {
            alert("Failed to update skills in database.");
        }
    } catch (e) {
        console.error("Error saving skills:", e);
        alert("Network error updating skills.");
    }
}

function handleExportPDF() {
    const element = document.getElementById("analysisContent");
    if (!element) return;

    const opt = {
        margin: 0.5,
        filename: `Resume_Analysis_Report_${currentResumeId || 'Report'}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save();
}

function parseJsonOrArray(val) {
    if (!val) return [];
    if (Array.isArray(val)) return val;
    if (typeof val === "object") return val;
    try { return JSON.parse(val); } catch (e) { return [val]; }
}

function renderListOrText(container, data, fallbackText) {
    if (!container) return;
    container.innerHTML = "";
    let list = data;

    if (typeof data === "string") {
        try { list = JSON.parse(data); } catch (e) { list = [data]; }
    }

    if (Array.isArray(list) && list.length > 0) {
        const ul = document.createElement("ul");
        ul.style.cssText = "list-style: none; padding-left: 0; margin: 0;";

        list.forEach(item => {
            const li = document.createElement("li");
            li.style.cssText = "margin-bottom: 8px; padding: 8px 12px; background: #ffffff; border-radius: 6px; border-left: 3px solid #4f46e5; box-shadow: 0 1px 2px rgba(0,0,0,0.04); font-size: 13px;";
            li.innerHTML = formatItemHtml(item);
            ul.appendChild(li);
        });
        container.appendChild(ul);
    } else {
        container.textContent = fallbackText;
    }
}

function formatItemHtml(item) {
    if (typeof item === "string") {
        try { item = JSON.parse(item); } catch (e) { return escapeHtml(item); }
    }
    if (typeof item !== "object" || item === null) return escapeHtml(String(item));

    if (item.degree || item.institution || item.field) {
        let titleParts = [];
        if (item.degree && item.field) titleParts.push(`${item.degree} in ${item.field}`);
        else if (item.degree) titleParts.push(item.degree);
        else if (item.field) titleParts.push(item.field);

        let html = `<strong>🎓 ${escapeHtml(titleParts.join(" ") || "Education")}</strong>`;
        if (item.institution) html += ` — <span style="color:#334155;">${escapeHtml(item.institution)}</span>`;
        if (item.graduation_date || item.year || item.date) html += ` <span style="color:#64748b;">(${escapeHtml(item.graduation_date || item.year || item.date)})</span>`;
        return html;
    }

    if (item.title || item.role || item.position || item.company) {
        const title = item.title || item.role || item.position || "Position";
        let html = `<strong>💼 ${escapeHtml(title)}</strong>`;
        if (item.company || item.organization) html += ` — <span style="color:#334155;">${escapeHtml(item.company || item.organization)}</span>`;
        if (item.duration || item.dates || item.period) html += ` <span style="color:#64748b;">(${escapeHtml(item.duration || item.dates || item.period)})</span>`;
        return html;
    }

    return Object.entries(item).filter(([k, v]) => v).map(([k, v]) => `<strong>${escapeHtml(k.replace(/_/g, ' '))}:</strong> ${escapeHtml(String(v))}`).join(" | ");
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
    loadAnalysis();

    const addTechBtn = document.getElementById("addTechSkillBtn");
    if (addTechBtn) addTechBtn.addEventListener("click", () => handleAddSkill("tech"));

    const addSoftBtn = document.getElementById("addSoftSkillBtn");
    if (addSoftBtn) addSoftBtn.addEventListener("click", () => handleAddSkill("soft"));

    const exportBtn = document.getElementById("exportPdfBtn");
    if (exportBtn) exportBtn.addEventListener("click", handleExportPDF);
});

