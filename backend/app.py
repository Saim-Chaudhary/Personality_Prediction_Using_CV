import os
import json
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import aiofiles

from database.database import get_db, engine
from models import candidate, job
from models.schemas import CandidateCreate, JobCreate, CandidateResponse, JobResponse
from services.cv_parser import CVParser
from services.personality_analyzer import PersonalityAnalyzer
from services.ranking_system import RankingSystem

# Create database tables
candidate.Base.metadata.create_all(bind=engine)
job.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personality Prediction System", description="AI-powered CV analysis and personality prediction")

# Get the absolute path of the current directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Setup templates with absolute path
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend"))


# Add custom filter for JSON parsing
def from_json(value):
    if value:
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
    return {}


templates.env.filters["from_json"] = from_json

# Initialize services
cv_parser = CVParser()
personality_analyzer = PersonalityAnalyzer()
ranking_system = RankingSystem()

# OAuth2 scheme for authentication (optional)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload_cv", response_class=HTMLResponse)
async def upload_cv_page(request: Request):
    return templates.TemplateResponse("upload_cv.html", {"request": request})


@app.post("/upload_cv")
async def upload_cv(
        request: Request,
        cv_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    if not cv_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save the uploaded file
    upload_dir = os.path.join(BASE_DIR, "static/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, cv_file.filename)

    async with aiofiles.open(file_path, 'wb') as f:
        content = await cv_file.read()
        await f.write(content)

    # Parse CV
    cv_data = cv_parser.parse(file_path)

    # Analyze personality
    personality_traits = personality_analyzer.analyze(cv_data['text'])

    # Create candidate record
    candidate_data = CandidateCreate(
        name=cv_data.get('name', 'Unknown'),
        email=cv_data.get('email', 'unknown@example.com'),
        phone=cv_data.get('phone', 'Unknown'),
        skills=', '.join(cv_data.get('skills', [])),
        experience=cv_data.get('experience', ''),
        education=cv_data.get('education', ''),
        certifications=', '.join(cv_data.get('certifications', [])),
        interests=', '.join(cv_data.get('interests', [])),
        personality_traits=json.dumps(personality_traits),
        cv_filename=cv_file.filename
    )

    db_candidate = candidate.Candidate(**candidate_data.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return RedirectResponse(url=f"/personality_test/{db_candidate.id}", status_code=303)


@app.get("/personality_test/{candidate_id}", response_class=HTMLResponse)
async def personality_test_page(request: Request, candidate_id: int, db: Session = Depends(get_db)):
    db_candidate = db.query(candidate.Candidate).filter(candidate.Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return templates.TemplateResponse("personality_test.html", {"request": request, "candidate": db_candidate})


@app.post("/personality_test/{candidate_id}")
async def submit_personality_test(
        candidate_id: int,
        request: Request,
        db: Session = Depends(get_db),
        q1: str = Form(...),
        q2: str = Form(...),
        q3: str = Form(...),
        q4: str = Form(...),
        q5: str = Form(...)
):
    db_candidate = db.query(candidate.Candidate).filter(candidate.Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Process test answers
    answers = {'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4, 'q5': q5}
    test_traits = personality_analyzer.analyze_test_answers(answers)

    # Update candidate with test results
    db_candidate.test_personality_traits = json.dumps(test_traits)
    db.commit()

    return RedirectResponse(url="/candidates", status_code=303)


@app.get("/job_profile", response_class=HTMLResponse)
async def job_profile_page(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(job.Job).all()
    return templates.TemplateResponse("job_profile.html", {"request": request, "jobs": jobs})


@app.post("/job_profile")
async def create_job_profile(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        required_skills: str = Form(...),
        required_experience: str = Form(...),
        required_education: str = Form(...),
        required_certifications: str = Form(...),
        required_personality_traits: str = Form(...),
        db: Session = Depends(get_db)
):
    job_data = JobCreate(
        title=title,
        description=description,
        required_skills=required_skills,
        required_experience=required_experience,
        required_education=required_education,
        required_certifications=required_certifications,
        required_personality_traits=required_personality_traits
    )

    db_job = job.Job(**job_data.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return RedirectResponse(url="/job_profile", status_code=303)


@app.get("/candidates", response_class=HTMLResponse)
async def candidates_page(
        request: Request,
        job_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    if job_id:
        db_job = db.query(job.Job).filter(job.Job.id == job_id).first()
        if not db_job:
            raise HTTPException(status_code=404, detail="Job not found")

        all_candidates = db.query(candidate.Candidate).all()
        ranked_candidates = ranking_system.rank_candidates(all_candidates, db_job)
    else:
        ranked_candidates = [(c, 0.5) for c in db.query(candidate.Candidate).all()]

    jobs = db.query(job.Job).all()

    # Process candidates to ensure JSON data is properly handled
    processed_candidates = []
    for candidate_obj, score in ranked_candidates:
        # Parse personality traits if they exist
        personality_traits = None
        if candidate_obj.personality_traits:
            try:
                personality_traits = json.loads(candidate_obj.personality_traits)
            except (TypeError, ValueError):
                personality_traits = None

        # Parse test personality traits if they exist
        test_personality_traits = None
        if candidate_obj.test_personality_traits:
            try:
                test_personality_traits = json.loads(candidate_obj.test_personality_traits)
            except (TypeError, ValueError):
                test_personality_traits = None

        # Create a dictionary with all candidate data
        candidate_dict = {
            'id': candidate_obj.id,
            'name': candidate_obj.name,
            'email': candidate_obj.email,
            'phone': candidate_obj.phone,
            'skills': candidate_obj.skills,
            'experience': candidate_obj.experience,
            'education': candidate_obj.education,
            'certifications': candidate_obj.certifications,
            'interests': candidate_obj.interests,
            'personality_traits': personality_traits,
            'test_personality_traits': test_personality_traits,
            'cv_filename': candidate_obj.cv_filename
        }
        processed_candidates.append((candidate_dict, score))

    return templates.TemplateResponse(
        "candidates.html",
        {
            "request": request,
            "candidates": processed_candidates,
            "jobs": jobs,
            "selected_job_id": job_id
        }
    )


@app.get("/api/rank_candidates/{job_id}")
async def api_rank_candidates(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(job.Job).filter(job.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    all_candidates = db.query(candidate.Candidate).all()
    ranked_candidates = ranking_system.rank_candidates(all_candidates, db_job)

    result = []
    for candidate, score in ranked_candidates:
        result.append({
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'skills': candidate.skills,
            'experience': candidate.experience,
            'education': candidate.education,
            'certifications': candidate.certifications,
            'interests': candidate.interests,
            'personality_traits': json.loads(candidate.personality_traits) if candidate.personality_traits else {},
            'test_personality_traits': json.loads(
                candidate.test_personality_traits) if candidate.test_personality_traits else {},
            'score': score
        })

    return {"candidates": result}


@app.get("/debug/candidates")
async def debug_candidates(db: Session = Depends(get_db)):
    candidates = db.query(candidate.Candidate).all()
    result = []
    for c in candidates:
        result.append({
            'id': c.id,
            'name': c.name,
            'personality_traits': c.personality_traits,
            'test_personality_traits': c.test_personality_traits
        })
    return {"candidates": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)