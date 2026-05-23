---
title: CLAT Guide
emoji: ⚖️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 8000
---

# LexAI - CLAT Preparation Engine

LexAI is an AI-powered CLAT preparation system utilizing a RAG (Retrieval-Augmented Generation) pipeline and the NVIDIA Nemotron-3 120B model to solve study doubts, explain legal concepts, and structure personalized study plans.

## Local Running Configuration

To run locally on host using Python 3.12:
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

## Cloud Deployment

This project is configured to run out-of-the-box as a Docker Container on **Hugging Face Spaces** (requires **NO credit card** or payment details).

### Space Setup:
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Choose **Docker** as the SDK.
3. Select the **Blank** template.
4. Git push this repository directly to the Hugging Face Space remote (or link it to GitHub).
5. In the Space **Settings**, add the following **Variables and Secrets**:
   * `NVIDIA_API_KEY`: Your NVIDIA API Key (`nvapi-...`)
   * `DATABASE_URL`: `sqlite:///data/lexai.db` (to store SQLite data in a persistent directory, or leave blank to run locally)
   * `JWT_SECRET_KEY`: A secure random string for JWT hashing.
