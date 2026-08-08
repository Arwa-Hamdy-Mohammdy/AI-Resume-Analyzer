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

        // Check if redirected with a target job ID from dashboard
        const targetJobId = localStorage.getItem("target_job_id");
        if (targetJobId) {
            localStorage.removeItem("target_job_id");
            select.value = targetJobId;
            handleMatching();
        }

    } catch (err) {
        console.error("Error loading job options:", err);
    }

    loadAutoRecommendations();
}

async function loadAutoRecommendations() {
    const container = document.getElementById("autoRecsList");
    const wrapper = document.getElementById("recommendationsWrapper");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/matching/recommendations`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
            if (wrapper) wrapper.style.display = "none";
            return;
        }

        const recommendations = await response.json();
        if (!Array.isArray(recommendations) || recommendations.length === 0) {
            if (wrapper) wrapper.style.display = "none";
            return;
        }

        container.innerHTML = "";
        recommendations.forEach(rec => {
            const card = document.createElement("div");
            card.style.cssText = "min-width: 220px; background: white; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 18px; cursor: pointer; transition: var(--transition); flex-shrink: 0;";
            
            const scoreColor = rec.match_score >= 70 ? '#16a34a' : (rec.match_score >= 40 ? '#d97706' : '#dc2626');
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 12px; font-weight: 700; color: ${scoreColor}; background: ${scoreColor}15; padding: 2px 8px; border-radius: 10px;">${rec.match_score}% Match</span>
                    <i class="fa-solid fa-chevron-right" style="font-size: 11px; color: var(--text-light);"></i>
                </div>
                <h4 style="font-size: 14px; font-weight: 700; color: var(--text-dark); margin-bottom: 2px;">${escapeHtml(rec.title)}</h4>
                <p style="font-size: 12px; color: var(--text-muted);">${escapeHtml(rec.company)}</p>
            `;

            card.addEventListener("click", () => {
                document.getElementById("jobSelect").value = rec.job_id;
                handleMatching();
            });

            card.addEventListener("mouseenter", () => { card.style.borderColor = "var(--primary)"; card.style.transform = "translateY(-2px)"; });
            card.addEventListener("mouseleave", () => { card.style.borderColor = "var(--border-color)"; card.style.transform = "none"; });

            container.appendChild(card);
        });

    } catch (e) {
        console.error("Error loading auto recommendations:", e);
        if (wrapper) wrapper.style.display = "none";
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

    // 1. Score & Chart
    const scoreVal = data.match_score ?? 0;
    try {
        const scoreEl = document.getElementById("scoreValue");
        if (scoreEl) scoreEl.textContent = `${scoreVal}%`;
        renderMatchRatioChart(scoreVal);
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

let matchChartInstance = null;
function renderMatchRatioChart(score) {
    const canvas = document.getElementById("matchRatioChart");
    if (!canvas) return;
    if (matchChartInstance) matchChartInstance.destroy();

    const color = score >= 70 ? '#16a34a' : (score >= 40 ? '#d97706' : '#dc2626');

    matchChartInstance = new Chart(canvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, '#e2e8f0'],
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

function handleExportMatchPDF() {
    const element = document.getElementById("resultBox");
    if (!element || element.style.display === "none") {
        alert("Please calculate an ATS match score first before exporting PDF.");
        return;
    }

    const opt = {
        margin: 0.5,
        filename: `ATS_Match_Report.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save();
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

document.addEventListener("DOMContentLoaded", () => {
    loadJobSelect();

    const genBulletsBtn = document.getElementById("generateBulletsBtn");
    if (genBulletsBtn) {
        genBulletsBtn.addEventListener("click", handleGenerateBullets);
    }

    const genRoadmapBtn = document.getElementById("generateRoadmapBtn");
    if (genRoadmapBtn) {
        genRoadmapBtn.addEventListener("click", handleGenerateRoadmap);
    }

    const exportMatchPdfBtn = document.getElementById("exportMatchPdfBtn");
    if (exportMatchPdfBtn) {
        exportMatchPdfBtn.addEventListener("click", handleExportMatchPDF);
    }
});


async function handleGenerateBullets() {
    let resumeId = localStorage.getItem("resume_id");
    const jobId = document.getElementById("jobSelect")?.value;
    const statusMsg = document.getElementById("ragStatusMsg");
    const wrapper = document.getElementById("ragBulletsWrapper");
    const container = document.getElementById("ragBulletsList");
    const btn = document.getElementById("generateBulletsBtn");

    if (!jobId) {
        if (statusMsg) {
            statusMsg.style.color = "red";
            statusMsg.textContent = "❌ Please select a target job position first.";
        }
        return;
    }

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
        } catch (e) { console.error("Error fetching latest resume:", e); }
    }

    if (!resumeId) {
        if (statusMsg) {
            statusMsg.style.color = "red";
            statusMsg.textContent = "❌ Please upload a resume first.";
        }
        return;
    }

    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Bullets via RAG...'; }
    if (statusMsg) { statusMsg.style.color = "#4f46e5"; statusMsg.textContent = "Searching Knowledge Base & optimizing ATS bullet points..."; }
    if (wrapper) wrapper.style.display = "none";

    try {
        const response = await fetch(`${API_URL}/rag/optimize-bullets`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ resume_id: parseInt(resumeId), job_id: parseInt(jobId) })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            if (statusMsg) { statusMsg.style.color = "red"; statusMsg.textContent = err.detail || "RAG Optimization failed."; }
            return;
        }

        const data = await response.json();
        if (statusMsg) statusMsg.textContent = "";
        renderBullets(container, data);
        if (wrapper) wrapper.style.display = "block";
    } catch (e) {
        console.error("RAG Bullets error:", e);
        if (statusMsg) { statusMsg.style.color = "red"; statusMsg.textContent = `Error: ${e.message}`; }
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-file-pen"></i> Generate ATS Bullet Points'; }
    }
}

function renderBullets(container, data) {
    if (!container) return;
    container.innerHTML = "";
    const bullets = data.optimized_bullets || [];

    if (Array.isArray(bullets) && bullets.length > 0) {
        bullets.forEach(bullet => {
            const div = document.createElement("div");
            div.style.cssText = "background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; gap: 12px;";
            
            div.innerHTML = `
                <div style="font-size: 14px; color: #1e293b; font-weight: 500;">
                    <i class="fa-solid fa-angles-right" style="color: #16a34a; margin-right: 6px;"></i> ${escapeHtml(bullet)}
                </div>
                <button type="button" class="copy-bullet-btn" style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; font-size: 12px; font-weight: 600; cursor: pointer; color: #475569; flex-shrink: 0;">
                    <i class="fa-regular fa-copy"></i> Copy
                </button>
            `;

            const copyBtn = div.querySelector(".copy-bullet-btn");
            copyBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(bullet);
                copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: #16a34a;"></i> Copied!';
                setTimeout(() => { copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy'; }, 2000);
            });

            container.appendChild(div);
        });
    } else {
        container.textContent = "No bullet points generated.";
    }
}

async function handleGenerateRoadmap() {
    let resumeId = localStorage.getItem("resume_id");
    const jobId = document.getElementById("jobSelect")?.value;
    const statusMsg = document.getElementById("ragStatusMsg");
    const wrapper = document.getElementById("ragRoadmapWrapper");
    const container = document.getElementById("ragRoadmapList");
    const btn = document.getElementById("generateRoadmapBtn");

    if (!jobId) {
        if (statusMsg) {
            statusMsg.style.color = "red";
            statusMsg.textContent = "❌ Please select a target job position first.";
        }
        return;
    }

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
        } catch (e) { console.error("Error fetching latest resume:", e); }
    }

    if (!resumeId) {
        if (statusMsg) {
            statusMsg.style.color = "red";
            statusMsg.textContent = "❌ Please upload a resume first.";
        }
        return;
    }

    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Retrieving Roadmap via RAG...'; }
    if (statusMsg) { statusMsg.style.color = "#0284c7"; statusMsg.textContent = "Retrieving skill roadmaps and course recommendations..."; }
    if (wrapper) wrapper.style.display = "none";

    try {
        const response = await fetch(`${API_URL}/rag/skill-roadmap`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ resume_id: parseInt(resumeId), job_id: parseInt(jobId) })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            if (statusMsg) { statusMsg.style.color = "red"; statusMsg.textContent = err.detail || "Roadmap generation failed."; }
            return;
        }

        const data = await response.json();
        if (statusMsg) statusMsg.textContent = "";
        renderRoadmap(container, data);
        if (wrapper) wrapper.style.display = "block";
    } catch (e) {
        console.error("RAG Roadmap error:", e);
        if (statusMsg) { statusMsg.style.color = "red"; statusMsg.textContent = `Error: ${e.message}`; }
    } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-graduation-cap"></i> Skill Gap Roadmap'; }
    }
}

function renderRoadmap(container, data) {
    if (!container) return;
    container.innerHTML = "";
    const items = data.roadmap || [];

    if (Array.isArray(items) && items.length > 0) {
        items.forEach(item => {
            const card = document.createElement("div");
            card.style.cssText = "background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 12px;";
            
            const concepts = Array.isArray(item.key_concepts) ? item.key_concepts.join(", ") : item.key_concepts || "N/A";
            const resources = Array.isArray(item.recommended_resources) ? item.recommended_resources.map(r => `<li style="margin-bottom: 4px;">${escapeHtml(r)}</li>`).join("") : `<li>${escapeHtml(item.recommended_resources || 'N/A')}</li>`;

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h5 style="font-size: 15px; font-weight: 700; color: #0284c7;">${escapeHtml(item.skill || 'Skill')}</h5>
                    <span style="font-size: 12px; font-weight: 600; background: #e0f2fe; color: #0369a1; padding: 3px 10px; border-radius: 12px;">${escapeHtml(item.estimated_time || '1-2 weeks')}</span>
                </div>
                <p style="font-size: 13px; color: #334155; margin-bottom: 8px;"><strong>Key Concepts:</strong> ${escapeHtml(concepts)}</p>
                <div style="font-size: 13px; color: #334155; margin-bottom: 8px;">
                    <strong>Recommended Free Resources:</strong>
                    <ul style="padding-left: 18px; margin-top: 4px;">${resources}</ul>
                </div>
                ${item.practice_project ? `<p style="font-size: 13px; color: #15803d; background: #f0fdf4; padding: 8px 12px; border-radius: 6px; border: 1px solid #dcfce7;"><strong>💡 Practice Project:</strong> ${escapeHtml(item.practice_project)}</p>` : ''}
            `;

            container.appendChild(card);
        });
    } else {
        container.textContent = "No specific roadmap generated.";
    }
}

