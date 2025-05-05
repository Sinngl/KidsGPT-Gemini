from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional
import uvicorn

from config import settings
from services.gemini import get_gemini_response

app = FastAPI(title="KidsGPT", description="A child-friendly AI assistant")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask", response_class=HTMLResponse)
async def ask_question(
        request: Request,
        question: str = Form(...),
        age: int = Form(...),
        language: str = Form("en")
):

    if not question.strip():
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Please enter a question", "language": language}
        )

    if age < 8 or age > 13:
        error_msg = "Bu uygulama 8-13 yaş arası çocuklar için tasarlanmıştır" if language == "tr" else "This application is designed for children aged 8-13"
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": error_msg, "language": language}
        )

    try:
        response = await get_gemini_response(question, age, language)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "question": question,
                "response": response,
                "age": age,
                "language": language
            }
        )
    except Exception as e:
        error_msg = "Üzgünüm, bu soruyu şu anda cevaplayamıyorum" if language == "tr" else f"Sorry, I couldn't answer that question"
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": error_msg, "language": language}
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)