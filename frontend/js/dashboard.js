const API_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

// Unified Logout Event Handler
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("token");
        localStorage.removeItem("resume_id");
        localStorage.removeItem("last_match_result");
        window.location.href = "index.html";
    });
}

// Fetch Current User
async function loadUserData() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            const userNameEl = document.getElementById("userName");
            if (userNameEl) {
                userNameEl.innerHTML = `Welcome back, <strong>${user.email || 'User'}</strong>! Manage your resumes & job opportunities below.`;
            }
        }
    } catch (e) {
        console.error("Error fetching user profile:", e);
    }
}

// Fetch & Render Auto Job Recommendations
async function loadJobRecommendations() {
    const container = document.getElementById("recommendationsContainer");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/matching/recommendations`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 404) {
            container.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: var(--radius-md); border: 1px dashed #cbd5e1; text-align: center;">
                    <i class="fa-solid fa-file-circle-exclamation" style="font-size: 36px; color: #f59e0b; margin-bottom: 10px;"></i>
                    <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 6px;">No Resume Uploaded Yet</h3>
                    <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">Upload your PDF resume to unlock personalized AI job recommendations & ATS scores.</p>
                    <a href="upload.html" class="btn-primary" style="display: inline-flex; width: auto; padding: 10px 22px; text-decoration: none; font-size: 14px;">
                        <i class="fa-solid fa-cloud-arrow-up"></i> Upload Resume Now
                    </a>
                </div>
            `;
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load recommendations.");
        }

        const recommendations = await response.json();

        if (!Array.isArray(recommendations) || recommendations.length === 0) {
            container.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: var(--radius-md); border: 1px solid var(--border-color); text-align: center;">
                    <p style="color: var(--text-muted); font-size: 14px;">No jobs available in the system yet. Add jobs in the <a href="jobs.html" style="color: var(--primary); font-weight:700;">Jobs section</a>.</p>
                </div>
            `;
            return;
        }

        // Show top 3 recommended jobs on dashboard
        const topJobs = recommendations.slice(0, 3);
        let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">';

        topJobs.forEach(job => {
            const scoreColor = job.match_score >= 70 ? '#16a34a' : (job.match_score >= 40 ? '#d97706' : '#dc2626');
            const scoreBg = job.match_score >= 70 ? '#f0fdf4' : (job.match_score >= 40 ? '#fffbeb' : '#fef2f2');

            const matchedBadgeHtml = job.matched_skills.slice(0, 4).map(s => 
                `<span class="match-badge matched" style="font-size:11px; padding:3px 8px;"><i class="fa-solid fa-check"></i> ${escapeHtml(s)}</span>`
            ).join(' ');

            html += `
                <div class="card-box" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px;">
                            <div>
                                <h3 style="font-size: 17px; margin-bottom: 4px;">${escapeHtml(job.title)}</h3>
                                <p style="color: var(--primary); font-weight: 600; font-size: 13px;">
                                    <i class="fa-solid fa-building"></i> ${escapeHtml(job.company)} &bull; ${escapeHtml(job.location)}
                                </p>
                            </div>
                            <div style="background: ${scoreBg}; color: ${scoreColor}; font-weight: 800; font-size: 15px; padding: 6px 12px; border-radius: var(--radius-full); border: 1px solid ${scoreColor}40;">
                                ${job.match_score}% Match
                            </div>
                        </div>

                        <div style="margin-bottom: 14px;">
                            <span style="font-size: 12px; font-weight: 700; color: var(--text-muted); display: block; margin-bottom: 6px;">MATCHING SKILLS:</span>
                            <div>${matchedBadgeHtml || '<span style="font-size:12px; color:var(--text-muted);">No direct skill matches</span>'}</div>
                        </div>
                    </div>

                    <button onclick="selectAndMatchJob(${job.job_id})" class="btn-primary" style="margin-top: 15px; width: 100%; padding: 10px 16px; font-size: 13px; background: var(--primary-gradient);">
                        <i class="fa-solid fa-bullseye"></i> View Full ATS Analysis
                    </button>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch (e) {
        console.error("Error loading job recommendations:", e);
        container.innerHTML = `
            <div style="background: white; padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border-color); color: #dc2626; font-size: 14px;">
                ❌ Unable to load job recommendations at this time.
            </div>
        `;
    }
}

async function loadMatchHistory() {
    const container = document.getElementById("matchHistoryContainer");
    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/matching/history`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">No past match evaluations recorded yet.</p>';
            return;
        }

        const history = await response.json();
        if (!Array.isArray(history) || history.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">No match evaluations found. Try matching a job in the Job Matching section!</p>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
        history.forEach(item => {
            const scoreColor = item.match_score >= 70 ? '#16a34a' : (item.match_score >= 40 ? '#d97706' : '#dc2626');
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 8px; border: 1px solid var(--border-color); flex-wrap: wrap; gap: 10px;">
                    <div>
                        <h4 style="font-size: 15px; font-weight: 700; color: var(--text-dark); margin: 0;">${escapeHtml(item.job_title)}</h4>
                        <p style="font-size: 13px; color: var(--text-muted); margin: 2px 0 0 0;">${escapeHtml(item.company)}</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 14px; font-weight: 800; color: ${scoreColor}; background: ${scoreColor}15; padding: 4px 12px; border-radius: 12px;">
                            ${item.match_score}% ATS Match
                        </span>
                        <button onclick="selectAndMatchJob(${item.job_id})" style="background: white; border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 12px; font-size: 12px; font-weight: 600; cursor: pointer; color: var(--primary);">
                            View Match <i class="fa-solid fa-arrow-right"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;

    } catch (e) {
        console.error("Error loading match history:", e);
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">Unable to load match history.</p>';
    }
}

function selectAndMatchJob(jobId) {
    localStorage.setItem("target_job_id", jobId);
    window.location.href = "matching.html";
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
    loadUserData();
    loadJobRecommendations();
    loadMatchHistory();
});
