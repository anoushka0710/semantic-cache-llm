# semantic-cache-llm
# Smart LLM Router with Semantic Cache

##  Problem Statement

LLMs are powerful but expensive. Sending every query to large models increases cost and latency.

This project optimizes:

* Cost
* Latency
  using intelligent routing and semantic caching.

---

##  Solution

We built a system that:

* Routes queries to cheap/expensive models
* Reuses past responses using semantic similarity

---

##  Architecture

User → Streamlit UI → FastAPI Backend → Router → LLM (Groq) → Response
                            ↓
                          Cache Layer

---

##  Features

* Smart routing (cheap vs expensive model)
* Cost tracking
* Latency tracking
* Semantic caching (integration stage)
* Interactive UI

---

##  Current Output

* Response
* Model used
* Reason
* Latency
* Cost

---

##  Future Evaluation (Cache Phase)

* Hit rate vs repetition
* Cost vs repetition
* Latency improvement

---

##  Tech Stack

* Frontend: Streamlit
* Backend: FastAPI
* LLM: Groq (Llama models)
* Language: Python

---

##  How to Run

### Backend

```bash
python -m uvicorn main:app --reload
```

### Frontend

```bash
streamlit run app.py
```

---

##  Team

* Backend: Anoushka 
* Cache & Evaluation: Drishty
* Frontend & Integration: Kaavika Sri

---

##  Status

*  Routing system complete
*  UI complete
*  Cache integration in progress

---

##  Demo


