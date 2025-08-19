from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lang_app_module import app as lang_app
from langchain_core.messages import HumanMessage

app = FastAPI()

# Allow all origins for development (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QueryRequest):
    inputs = {"question": request.question, "messages": [HumanMessage(content=request.question)]}
    final_state = lang_app.invoke(inputs)
    # Return all relevant fields for your dashboard
    return {
        "question": final_state.get("question"),
        "sentiment": final_state.get("sentiment"),
        "initialResponse": final_state.get("initialResponse"),
        "finalResponse": final_state.get("finalResponse"),
        "selfCheckResult": final_state.get("selfCheckResult"),
    }