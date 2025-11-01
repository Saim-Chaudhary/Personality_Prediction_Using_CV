

# Personality Prediction System

An AI-powered HR tool that analyzes CVs and personality tests to rank candidates for specific job profiles. This system combines natural language processing, sentiment analysis, and machine learning techniques to create a comprehensive picture of candidates, helping HR departments make more informed hiring decisions.

## Features

- 📄 CV upload and text extraction
- 🧠 Personality trait analysis from CV text
- 📝 Online personality test
- 💼 Job profile creation
- 📊 Candidate ranking based on job requirements
- 📈 Visual representation of personality traits

## Technology Stack

### Backend
- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database for storing candidate and job data
- **Pydantic** - Data validation and serialization

### Frontend
- **HTML5** - Structure and content
- **Tailwind CSS** - Styling and responsive design
- **JavaScript** - Client-side interactivity
- **Jinja2** - Template engine for dynamic content

### AI/ML Libraries
- **Transformers (Hugging Face)** - For sentiment analysis
- **NLTK** - Natural language processing
- **pdfplumber** - PDF text extraction

## Installation

### Prerequisites
- Python 3.13
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/personality-prediction-system.git
cd personality-prediction-system
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

4. Install the required packages:
```bash
cd backend
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
uvicorn app:app --reload
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000
```

3. Follow these steps to use the system:
   - Upload a CV in PDF format
   - Take the personality test
   - Create a job profile
   - View ranked candidates

## Project Structure

```
personality_prediction_system/
├── backend/
│   ├── app.py                     # Main FastAPI application
│   ├── requirements.txt           # Python dependencies
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── job.py
│   │   └── schemas.py
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── cv_parser.py
│   │   ├── personality_analyzer.py
│   │   └── ranking_system.py
│   ├── database/                  # Database configuration
│   │   ├── __init__.py
│   │   └── database.py
│   ├── static/                    # Static files
│   │   └── uploads/               # Uploaded CVs
│   └── frontend/                  # HTML templates
│       ├── index.html
│       ├── upload_cv.html
│       ├── job_profile.html
│       ├── personality_test.html
│       └── candidates.html
```

## How It Works

### CV Analysis
1. **Text Extraction**: The system extracts text from uploaded PDF CVs using pdfplumber
2. **Information Parsing**: It identifies and extracts key information like skills, experience, education, etc.
3. **Personality Analysis**: The text is analyzed for personality indicators using:
   - Keyword spotting for trait-related terms
   - Sentiment analysis using Hugging Face's DistilBERT model
   - NLTK's VADER sentiment analyzer

### Personality Test
After CV analysis, candidates take a simple 5-question test that maps to the Big Five personality traits:
- Openness
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism

### Candidate Ranking
The system ranks candidates based on their match with job requirements using a weighted scoring system:
- Skills match (30% weight)
- Experience match (20% weight)
- Education match (10% weight)
- Certifications match (10% weight)
- Personality traits match (30% weight)

## AI Models Used

### Hugging Face's DistilBERT Model
- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Purpose**: Sentiment analysis of CV text
- **Architecture**: Transformer-based neural network

### NLTK's VADER Sentiment Analyzer
- **Type**: Rule-based sentiment analysis tool
- **Purpose**: Additional sentiment analysis for CV text

## API Documentation

Once the application is running, you can access the interactive API documentation at:
```
http://127.0.0.1:8000/docs
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hugging Face for the pre-trained sentiment analysis model
- NLTK team for the natural language processing toolkit
- FastAPI team for the modern web framework

## Contact

 - Saim Chaudhary

Project Link: [[https://github.com/Saim-Chaudhary/Personality_Prediction_Using_CV](https://github.com/Saim-Chaudhary/Personality_Prediction_Using_CV)]
