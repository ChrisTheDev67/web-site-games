# My Game Portfolio

A personal game portfolio website built with **Python (Flask)** and **PyScript**.

## Features
- **Home**: About me and bio.
- **Gallery**: Showcase of your Python games.
- **Play**: Run Python games directly in the browser using PyScript.
- **Cabinet**: Admin interface to upload games (best used locally).

## How to Run Locally

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Server**:
    ```bash
    python3 api/index.py
    ```

3.  **Open in Browser**:
    Go to [http://localhost:3000](http://localhost:3000).

4.  **Upload Games**:
    -   Navigate to the **Cabinet** page.
    -   Upload a `.zip` file containing your Python game (must have a `main.py`) or a single `.py` file.
    -   The game will be added to the gallery.

## Deployment on Vercel

This project is configured for Vercel deployment.

1.  **Push to GitHub**: Commit your changes and push to a GitHub repository.
2.  **Import to Vercel**:
    -   Go to [Vercel Dashboard](https://vercel.com).
    -   Add New > Project.
    -   Import your repository.
    -   Vercel will detect the `vercel.json` and configure the Python runtime automatically.

### Imporant Note on Uploads
Vercel is a **Serverless** platform with a read-only filesystem. 
-   **Game Uploads**: The "Cabinet" upload feature works great **locally**. You should upload your games while running locally, then commit the new files in `static/games/` to GitHub.
-   When deployed, the "Cabinet" will not be able to permanently save new games because Vercel does not persist file changes.
