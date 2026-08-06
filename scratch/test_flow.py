import requests
import os

API_URL = "http://127.0.0.1:8000"

# 1. Register / Login
user_data = {
    "email": "testuser@example.com",
    "password": "password123",
    "full_name": "Test User"
}

# Try registering
reg_res = requests.post(f"{API_URL}/auth/register", json=user_data)
print("Register status:", reg_res.status_code)

# Login
login_res = requests.post(
    f"{API_URL}/auth/login",
    data={"username": "testuser@example.com", "password": "password123"}
)
print("Login status:", login_res.status_code, login_res.json())

token = login_res.json().get("access_token")

# 2. Upload Resume
with open("AI_Resume_Analyzer.pdf", "rb") as f:
    upload_res = requests.post(
        f"{API_URL}/resumes/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("AI_Resume_Analyzer.pdf", f, "application/pdf")}
    )

print("Upload status:", upload_res.status_code)
print("Upload response:", upload_res.json())

if upload_res.status_code == 200:
    resume_id = upload_res.json()["id"]
    
    # 3. Get Analysis by ID
    analysis_res = requests.get(
        f"{API_URL}/resumes/{resume_id}/analysis",
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Analysis status:", analysis_res.status_code)
    print("Analysis response:", analysis_res.json())

    # 4. Get Latest Analysis
    latest_res = requests.get(
        f"{API_URL}/resumes/latest/analysis",
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Latest Analysis status:", latest_res.status_code)
    print("Latest Analysis response:", latest_res.json())

    # 5. Get Job & Match
    jobs_res = requests.get(f"{API_URL}/jobs/")
    print("Jobs status:", jobs_res.status_code, jobs_res.json())
    jobs = jobs_res.json()
    if jobs:
        job_id = jobs[0]["id"]
        match_res = requests.post(
            f"{API_URL}/matching/",
            headers={"Authorization": f"Bearer {token}"},
            json={"resume_id": resume_id, "job_id": job_id}
        )
        print("Match status:", match_res.status_code)
        print("Match response:", match_res.json())
