# YouTube Income Commander Mini

This is an MVP (Minimum Viable Product) application designed for rapid identification of commercially viable YouTube video ideas and initiation of the main YouTube AI content platform.

## Purpose

- **Earliest Earnings Focus**: Quickly generate and evaluate video ideas with high potential for monetization (e.g., high CPM niches, affiliate marketing, sponsorships).
- **Market Validation**: Test commercial viability of certain topics or angles before committing full resources from the main platform.
- **Initiation Extension**: Act as a "chair" or starting point, feeding validated ideas into the main `youtube_ai_app_clean` system for full content creation.

## Features

- Generate commercial video ideas based on niche and focus.
- Simple revenue projection for ideas.
- API endpoint to initiate the main content creation pipeline with a selected idea.

## Local Setup

1.  **Navigate to the mini-app directory:**
    ```bash
    cd path/to/youtube_ai_app_clean/youtube-income-commander-mini
    ```

2.  **Create and populate `.env` file:**
    Copy the contents from the provided `.env` example and fill in your `OPENAI_API_KEY`.
    ```
    APP_PORT=8080
    MAIN_PLATFORM_URL="http://localhost:8000"
    OPENAI_API_KEY="your_openai_api_key_here"
    SERPER_API_KEY="your_serper_api_key_here" # Optional
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload --port 8080
    ```
    The application will be available at `http://localhost:8080`.
    API documentation at `http://localhost:8080/docs`.

## How it Initiates the Main Platform

The mini-app includes an endpoint (`/api/mini/v1/initiate-main-pipeline`) that, when called with a `CommercialIdea`, will send a formatted request to the main `youtube_ai_app_clean` platform (expected to be running on `MAIN_PLATFORM_URL`, typically `http://localhost:8000`). The main platform must have a corresponding endpoint (e.g., `/api/v1/initiate-video-from-brief`) to receive this request and start its video creation process.