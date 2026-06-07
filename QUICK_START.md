# Quick Start Guide - Expense Tracker

Get the expense tracker running in **5 minutes**.

---

## ⚡ Quick Start (30 seconds)

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate

# 2. Run the app
python src/main.py

# Done! Use the interactive menu
```

**Expected Output:**
```
============================================================
   Expense Tracker CLI - Phase 1
============================================================

Menu:
1. Add Expense
2. View All Expenses
3. Filter by Category
4. Monthly Summary
5. Set Budget
6. View Budget Status
7. View All Budgets
8. Export Expenses to CSV
9. Export Summary to CSV
0. Exit

Enter your choice (0-9): _
```

---

## 🔧 Setup (if first time)

### Step 1: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**Windows PowerShell:**
```bash
.\.venv\Scripts\Activate
```

**If blocked:**
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run
```bash
python src/main.py
```

---

## 📋 Project Structure

```
src/
├── main.py                    # Entry point (run this!)
├── models/expense.py          # Data structures
├── services/                  # Business logic
│   ├── expense_tracker.py
│   ├── budget_service.py
│   └── export_service.py
├── storage/json_storage.py    # Data persistence
├── cli/                       # User interface
│   ├── menu.py
│   └── commands.py
└── utils/                     # Helpers
    ├── validators.py
    └── formatters.py
```

---

## ✨ Key Features

✅ Add/view/filter expenses  
✅ Monthly summaries  
✅ Budget tracking & alerts  
✅ Export to CSV  
✅ Full data persistence  
✅ 35+ automated tests  

---

## 🎯 Common Tasks

### Add an Expense
```
Menu choice: 1
Date (YYYY-MM-DD) [Enter for today]: 2026-06-07
Amount ($): 50.00
Category: food
Description: Lunch
```

### View All Expenses
```
Menu choice: 2
```

### Filter by Category
```
Menu choice: 3
Enter category: food
```

### Check Budget Status
```
Menu choice: 6
```

### Set a Budget
```
Menu choice: 5
Category: food
Amount: 300
```

### Export to CSV
```
Menu choice: 8
```

---

## 🧪 Run Tests

```bash
python -m pytest tests/ -v
```

Or direct:
```bash
python tests/test_expense_tracker.py
```

**Coverage:** 35+ tests, 100% pass rate

---

## 📚 Documentation

- **README.md** - Full project overview
- **STRUCTURE.md** - Detailed architecture
- **docs/ARCHITECTURE.md** - System design
- **docs/BUILD_SUMMARY.md** - Implementation details

---

## ✅ You're Ready!

Start tracking expenses:
```bash
python src/main.py
```

**Have questions?** Check `STRUCTURE.md` for architecture details.
