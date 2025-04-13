# LoreBoard
Project for Yardwork Hackathon 2025

## Setup Instructions

### Prerequisites

*   **Node.js & npm:** Required for the frontend. Download from [https://nodejs.org/](https://nodejs.org/)
*   **Python 3.10:** Required for the backend. Make sure you have Python 3.10 installed. You can use tools like `pyenv` to manage multiple Python versions.
*   **PostgreSQL:** Required for the backend database.
*   **Homebrew (macOS):** Used to install PostgreSQL on macOS. Install from [https://brew.sh/](https://brew.sh/)

### Backend Setup

1.  **Install PostgreSQL (macOS example):**
    ```bash
    brew install postgresql
    brew services start postgresql
    ```
    *(For other operating systems, follow the official PostgreSQL installation guides.)*

2.  **Create Database and User:**
    Open the PostgreSQL command-line tool (`psql`):
    ```bash
    psql postgres
    ```
    Inside `psql`, run the following commands (you can change the user and password):
    ```sql
    CREATE DATABASE loreboard_db;
    CREATE USER loreboard_user WITH PASSWORD 'your_secure_password';
    ALTER ROLE loreboard_user SET client_encoding TO 'utf8';
    ALTER ROLE loreboard_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE loreboard_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE loreboard_db TO loreboard_user;
    \\q
    ```

3.  **Create Database Tables:**
    Connect to your newly created database:
    ```bash
    psql -U loreboard_user -d loreboard_db
    ```
    Paste and run the following SQL commands:
    ```sql
    -- Characters table
    CREATE TABLE characters (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        physical TEXT DEFAULT '',
        personality TEXT DEFAULT '',
        background TEXT DEFAULT '',
        goals TEXT DEFAULT '',
        relationships TEXT DEFAULT '',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    -- Places table
    CREATE TABLE places (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        physical TEXT DEFAULT '',
        environment TEXT DEFAULT '',
        purpose TEXT DEFAULT '',
        history TEXT DEFAULT '',
        location TEXT DEFAULT '',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    -- Items table
    CREATE TABLE items (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        physical TEXT DEFAULT '',
        function TEXT DEFAULT '',
        origin TEXT DEFAULT '',
        ownership TEXT DEFAULT '',
        properties TEXT DEFAULT '',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    -- Aliases table
    CREATE TABLE aliases (
        id SERIAL PRIMARY KEY,
        entity_type VARCHAR(50) NOT NULL, -- 'character', 'place', 'item'
        entity_id INTEGER NOT NULL,
        alias VARCHAR(255) NOT NULL
        -- Consider adding foreign key constraints if needed
        -- FOREIGN KEY (entity_id) REFERENCES characters(id) ON DELETE CASCADE, -- Example for characters
    );
    ```
    Exit `psql`:
    ```sql
    \\q
    ```

4.  **Navigate to Backend Directory:**
    ```bash
    cd backend-2
    ```

5.  **Create and Activate Python 3.10 Virtual Environment:**
    ```bash
    python3.10 -m venv venv_py310
    source venv_py310/bin/activate
    ```
    *(Your shell prompt should now start with `(venv_py310)`)*

6.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

7.  **Set Up Environment Variables:**
    Create a file named `.env` in the `backend-2` directory (if it doesn't exist) and add the following, replacing placeholders with your actual values:
    ```dotenv
    OPENAI_API_KEY=your_openai_api_key_here
    DATABASE_URL=postgresql://loreboard_user:your_secure_password@localhost:5432/loreboard_db
    OPENAI_MODEL=gpt-4o-mini # Or your preferred model
    ```
    *   **`OPENAI_API_KEY`:** Get this from your OpenAI account.
    *   **`DATABASE_URL`:** Use the username, password, and database name you created in step 2.
    *   **`OPENAI_MODEL`:** Specify the OpenAI model to use (e.g., `gpt-4o-mini`, `gpt-3.5-turbo`).

8.  **Run the Backend Server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The backend API should now be running at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to Frontend Directory:**
    *(Open a new terminal window/tab)*
    ```bash
    cd frontend
    ```

2.  **Install Node Dependencies:**
    ```bash
    npm install
    ```
    *(This will install the versions specified in `package-lock.json`)*

3.  **Run the Frontend Development Server:**
    ```bash
    npm start
    ```
    This should automatically open the LoreBoard application in your default web browser, usually at `http://localhost:3000`.
