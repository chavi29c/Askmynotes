from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests


app = FastAPI(
    title="Student Question API",
    description="FastAPI backend for AskMyNotes",
    version="1.0.0",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://askmynotes-frontend-tv9g.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def home():
    return {
        "message": "FastAPI backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):

    cleaned_question = request.question.strip()

    if not cleaned_question:
        return QuestionResponse(
            question="",
            answer="Please enter a question."
        )

    # Send question to classifier
    classifier_url = "https://askmynotes-classifier-xyh0.onrender.com/predict"

    try:
        classifier_response = requests.post(
            classifier_url,
            json={
                "question": cleaned_question
            },
            timeout=60
        )

        classifier_response.raise_for_status()

        classifier_data = classifier_response.json()

        predicted_category = classifier_data["predicted_category"]

        return QuestionResponse(
            question=cleaned_question,
            answer=f"Predicted category: {predicted_category}"
        )

    except requests.exceptions.RequestException as e:

        print("Classifier error:", e)

        return QuestionResponse(
            question=cleaned_question,
            answer="Unable to connect to the classifier."
        )