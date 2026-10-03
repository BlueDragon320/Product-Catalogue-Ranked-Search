# Setup & Installation Guide

**Product Catalogue Ranked Search & Sponsored Placement Engine**  
**Runtime:** Python 3.10+ // Flask // SQLAlchemy  

---

## 1. Prerequisites

Before installing the application, ensure your host environment meets the following requirements:

- **Python**: Version 3.10 or higher (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported).
- **Package Manager**: `pip` (Python package installer).
- **Virtual Environment Tool**: `python3-venv` module (standard library) or `virtualenv`.
- **Database Engine**:
  - Development / Testing: SQLite3 (built into Python standard library).
  - Production (optional): PostgreSQL 14+ or compatible SQL database.
- **Operating System**: Linux (recommended), macOS, or Windows (via WSL or PowerShell).

To verify your Python and pip installations:
```bash
python3 --version
pip --version
```

---

## 2. Installation & Setup

### Step 1: Clone or Navigate to Repository

Clone the project repository or change into the project root directory:
```bash
git clone <repository-url>
cd Product-Catalogue-Ranked-Search
```

### Step 2: Create a Virtual Environment

Isolate application dependencies by creating a dedicated virtual environment:
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```

Once activated, your terminal prompt will be prefixed with `(venv)`.

### Step 4: Install Dependencies

Install all required production and testing packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### Core Package Breakdown:
- `Flask`: Core microframework.
- `Flask-SQLAlchemy`: Object-Relational Mapping (ORM) and database management.
- `Flask-Migrate`: Alembic database schema migrations.
- `Flask-Login`: User session authentication and access control.
- `Flask-WTF` & `WTForms`: Form validation and CSRF token handling.
- `Werkzeug`: Password hashing security and WSGI utilities.
- `pytest` & `pytest-flask`: Automated testing framework.

---

## 3. Environment Configuration

The application supports multiple operational configurations via the `FLASK_CONFIG` environment variable.

| Configuration Profile | `FLASK_CONFIG` Value | Database Target | Debug Mode | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Development** (Default) | `development` | SQLite file (`instance/ranking_engine.db`) | Enabled | Local development and interactive testing. |
| **Testing** | `testing` | In-memory SQLite (`sqlite:///:memory:`) | Disabled | CI/CD pipelines and automated Pytest execution. |
| **Production** | `production` | Connection URI from `DATABASE_URL` | Disabled | Production deployment behind reverse proxy. |

### Optional Environment Variables:
```bash
# Secret key for session security (defaults to fallback in development)
export SECRET_KEY="your-secure-production-random-key"

# Database URL override for development
export DEV_DATABASE_URL="sqlite:///instance/ranking_engine.db"

# Active configuration environment
export FLASK_CONFIG="development"
```

---

## 4. Running the Application

### Method A: Direct Execution via Entrypoint

Run the application using the standalone runner script:
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000/` with interactive debug reload enabled.

### Method B: Flask CLI

Alternatively, run through the Flask CLI:
```bash
export FLASK_APP=run.py
export FLASK_DEBUG=1
flask run --port 5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

You should see the **Product Catalogue Ranked Search & Sponsored Placement Engine** landing dashboard.

---

## 5. Database Initialization & Schema

When the application factory `create_app()` boots:
1. It creates the `instance/` folder if it does not already exist.
2. Inside the application context, `db.create_all()` is executed, generating all tables for:
   - `companies`
   - `users`
   - `categories`
   - `attributes`
   - `products`
   - `product_attr_values`
   - `sponsored_placements`
   - `search_logs`

### Schema Migration Management (Alembic / Flask-Migrate)

For tracking incremental database schema alterations:
```bash
# Initialize migration tracking repository (first time only)
flask --app run.py db init

# Generate migration revision script after modifying models.py
flask --app run.py db migrate -m "Describe schema changes"

# Apply pending migrations to database
flask --app run.py db upgrade
```

---

## 6. Running Automated Tests

The testing suite validates mathematical normalization, 100% weight allocation rules, 1:5 sponsored interleaving, and model integrity.

Execute tests using `pytest`:
```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

---

## 7. Troubleshooting & Common Issues

### Issue 1: Port 5000 is already in use
If another service (or AirPlay Receiver on macOS) occupies port 5000:
```bash
python -c "from run import app; app.run(port=5001, debug=True)"
```
Or specify the port using the Flask CLI:
```bash
flask --app run.py run --port 5001
```

### Issue 2: `ModuleNotFoundError: No module named 'app'`
Ensure you are executing commands from the project root directory (`/Product-Catalogue-Ranked-Search`), or ensure `PYTHONPATH=.` is present in your environment:
```bash
export PYTHONPATH=.
python run.py
```

### Issue 3: Missing instance folder permissions
If SQLite reports database file lock or permission errors, verify write permissions on the `instance/` directory:
```bash
mkdir -p instance
chmod 755 instance
```
