# Setup Guide for beInformed (macOS)

Follow these steps to get the beInformed application running on your Mac.

## 1. Prerequisites

Ensure you have the following installed:
- **Python 3.10+**: [Download here](https://www.python.org/downloads/macos/) or install via Homebrew.
- **PostgreSQL**: Install using Homebrew: `brew install postgresql@14`
- **Homebrew**: (Optional but recommended) [Install here](https://brew.sh/)

## 2. Database Configuration

1. **Start PostgreSQL**:
   ```bash
   brew services start postgresql@14
   ```

2. **Create the Database**:
   Open your terminal and create the database named `beInformed`:
   ```bash
   createdb beInformed
   ```

## 3. Environment Setup

1. **Clone/Navigate to the Project**:
   Ensure you are in the project root directory.

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Open `.env` in your editor and ensure `DATABASE_URL` is correct. The default is `postgresql://localhost/beInformed`.

## 4. Initializing the Database

Run the following command to create the necessary tables:
```bash
python3 main.py
```

## 5. Running the Application

Start the Flask development server:
```bash
python3 app.py
```

The application will be available at `http://localhost:5001`.

## Troubleshooting

- **Library Issues**: If `psycopg2` fails to install, try `pip install psycopg2-binary`.
- **Database Connection**: Ensure PostgreSQL is running and the `DATABASE_URL` matches your local config.
- **Port Conflict**: If port 5001 is in use, modify the port in the last line of `app.py`.
