# Quick Start

## 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

## 2. Backend setup
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Add your Gemini API key
Copy the example env file and add your own key (get one at https://aistudio.google.com):
```bash
cp ../.env.example ../.env
```
Then edit `.env` (in the project root, one level above `backend/`) so it contains:
```
GEMINI_API_KEY=your_own_key_here
```

## 4. Run the backend
```bash
uvicorn main:app --reload --port 8000
```
Confirm it's working: open http://localhost:8000/api/health — you should see `"gemini_key_configured": true`.

## 5. Run the frontend
```bash
cd ../frontend
npm install
npm run dev
```
Open http://localhost:5173

## Data
Sample reconciliation data (2,000 synthetic orders) ships in `/data`. To regenerate fresh synthetic data instead:
```bash
python legacy/generate_data.py
python legacy/reconcile.py
```
