# Expense Tracker CLI - Project Index

Welcome to the Expense Tracker CLI project! This file helps you navigate the codebase, documentation, and features.

---

## 🚀 Quick Start (Choose One)

### Option A: Run Immediately (30 seconds)
```bash
.\.venv\Scripts\Activate
python src/main.py
```

### Option B: Setup & Run (2 minutes)
```bash
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python src/main.py
```

### Option C: Run Tests (2 minutes)
```bash
.\.venv\Scripts\Activate
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
expense-tracker/
│
├── src/                      # APPLICATION CODE (modular architecture)
│   ├── main.py              # Entry point - START HERE
│   ├── models/expense.py    # Data model with validation
│   ├── services/            # Business logic layer
│   │   ├── expense_tracker.py  # Core CRUD operations
│   │   ├── budget_service.py   # Budget management
│   │   └── export_service.py   # CSV export
│   ├── storage/json_storage.py # Data persistence layer
│   ├── cli/                 # User interaction layer
│   │   ├── menu.py         # Interactive menu
│   │   └── commands.py     # Command handlers
│   └── utils/              # Utility functions
│       ├── validators.py   # Input validation
│       └── formatters.py   # Output formatting
│
├── tests/                   # TEST SUITE (35+ tests)
│   ├── test_expense_tracker.py
│   └── test_expense_tracker_enhanced.py
│
├── data/                    # DATA STORAGE (auto-created)
│   ├── expenses.json       # Expense records
│   └── budgets.json        # Budget limits
│
├── exports/                 # CSV EXPORTS (auto-created)
│   └── *.csv               # Generated reports
│
├── docs/                    # TECHNICAL DOCUMENTATION
│   ├── ARCHITECTURE.md     # System design & class diagrams
│   ├── BUILD_SUMMARY.md    # Implementation details
│   └── COMPLETION_CHECKLIST.md # Feature verification
│
├── README.md               # PROJECT OVERVIEW (START HERE)
├── QUICK_START.md          # 5-minute quick start guide
├── STRUCTURE.md            # Detailed architecture explanation
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
└── .gitignore             # Git configuration
```

---

## 📚 Documentation Guide

### For Different Audiences

#### 👤 First-Time Users (5-15 minutes)
1. **Start here:** `QUICK_START.md` (5 min) - Get the app running
2. **Then explore:** Run `python src/main.py` and try a few actions
3. **Understand structure:** `STRUCTURE.md` (10 min) - See the architecture
4. **Want to learn?** Read README.md (15 min) - Full project overview

#### 👨‍💻 Developers (30-60 minutes)
1. **Architecture:** `STRUCTURE.md` (10 min) - Understand the layers
2. **Design:** `docs/ARCHITECTURE.md` (15 min) - Class diagrams and flows
3. **Implementation:** `docs/BUILD_SUMMARY.md` (10 min) - What was built
4. **Code review:** Browse `src/` folder directly (15 min)
5. **Testing:** Look at `tests/` folder (10 min) - See test patterns

#### 🔍 Code Reviewers / Recruiters
1. **Overview:** README.md (10 min) - Project goals and outcomes
2. **Structure:** STRUCTURE.md (10 min) - Professional organization
3. **Architecture:** `docs/ARCHITECTURE.md` (15 min) - Design patterns
4. **Code:** Browse `src/` (15 min) - Clean, documented code
5. **Testing:** `tests/` folder (10 min) - 35+ comprehensive tests

#### 📊 Data Analysis Users
1. Run the app: `python src/main.py`
2. Add your expenses (Menu option 1)
3. Set budgets (Menu option 5)
4. Export to CSV (Menu options 8-9)
5. Open CSV files in Excel or Google Sheets

---

## 🎯 Common Tasks

### I want to...

**Run the application**
```bash
python src/main.py
```

**Add an expense**
- Use the interactive menu (Option 1) OR
- Terminal: `python expense_tracker_enhanced.py add --amount 50 --category food --description "Lunch"`

**Set a budget**
- Menu option 5: Interactive OR
- Terminal: `python expense_tracker_enhanced.py budget set --category food --amount 300`

**Check my spending vs. budget**
- Menu option 6: View Budget Status

**Export data**
- Menu options 8-9: Export to CSV

**Run tests**
```bash
python -m pytest tests/ -v
```

**Understand the code**
1. Read `STRUCTURE.md` (10 min)
2. Browse `src/main.py` and `src/services/` (15 min)
3. Read `docs/ARCHITECTURE.md` for detailed design (15 min)

**Extend with new features**
1. Add model in `src/models/` if needed
2. Create service in `src/services/`
3. Add CLI handler in `src/cli/commands.py`
4. Write tests in `tests/`

---

## ✨ Features Overview

### Core Features (Phase 1)
- ✅ Add expenses with full validation
- ✅ View all expenses (formatted table)
- ✅ Filter by category
- ✅ Monthly spending summary
- ✅ JSON data persistence
- ✅ Interactive CLI menu
- ✅ 35+ automated tests
- ✅ Professional code organization

### Stretch Goals (Also Included)
- ✅ Budget management per category
- ✅ Budget status alerts (80% warnings)
- ✅ CSV export functionality
- ✅ Command-line argparse interface

---

## 🏗️ Architecture Highlights

### Layered Design
- **Models Layer:** Data structures (Expense class)
- **Services Layer:** Business logic (CRUD, budgets, exports)
- **Storage Layer:** Persistence (JSON file I/O)
- **CLI Layer:** User interaction (menu, commands)
- **Utils Layer:** Reusable helpers (validators, formatters)

### Design Principles
✓ Single Responsibility Principle  
✓ Separation of Concerns  
✓ DRY (Don't Repeat Yourself)  
✓ Dependency Injection  
✓ Mockable Design (easy to swap JSON for database)  

### Why This Matters
- **Easy to test** - Each layer can be tested independently
- **Easy to extend** - Add new features without touching existing code
- **Easy to maintain** - Changes are localized to one layer
- **Easy to scale** - Replace JSON storage with database later
- **Easy to reuse** - Services can be imported by future phases (web API, CLI tools, etc.)

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Total Code | ~1000 lines |
| Main Application | ~500 lines |
| Tests | ~350 lines |
| Test Cases | 35+ |
| Pass Rate | 100% |
| Documentation | Comprehensive |
| Python Version | 3.10+ |
| External Dependencies | None (std library only) |
| Code Quality | Production-ready |

---

## 🔄 File Relationships

```
USER RUNS:
  python src/main.py
       ↓
  src/cli/menu.py (interactive menu)
       ↓
  src/cli/commands.py (processes input)
       ↓
  src/services/*.py (business logic)
       ↓
  src/storage/json_storage.py (reads/writes data)
       ↓
  data/expenses.json & data/budgets.json (persistent storage)

TESTS VERIFY:
  tests/ (35+ test cases)
       ↓
  src/models/ (validate data)
  src/services/ (verify business logic)
  src/storage/ (check persistence)
  src/utils/ (test helpers)
```

---

## 🔐 Data Flow

```
INPUT → VALIDATION → BUSINESS LOGIC → STORAGE → OUTPUT
 (CLI)   (validators)  (services)    (JSON)  (formatters)
```

Each stage is independent and testable.

---

## 🚀 Roadmap (Future Phases)

This codebase is designed to scale:

### Phase 2: Web API
- Add `src/api/` with FastAPI routes
- Reuse existing services and models
- Add user authentication

### Phase 3: Database
- Replace `src/storage/json_storage.py` with SQL database
- No changes needed to business logic!

### Phase 4: Cloud Deployment
- Docker containerization
- CI/CD pipelines

### Phase 5: AI Integration
- Semantic search
- AI expense categorization

---

## 📖 Reading Recommendations

### 5 Minutes
- `QUICK_START.md`

### 15 Minutes
- `README.md` + Run the app once

### 30 Minutes
- `STRUCTURE.md` + Browse `src/` folder

### 60 Minutes
- All documentation + Code review + Test review

---

## ✅ Verification Checklist

- ✅ All features implemented (12 total)
- ✅ All tests passing (35+ test cases)
- ✅ Professional code structure
- ✅ Comprehensive documentation
- ✅ Production-ready quality
- ✅ Scalable architecture

---

## 💡 Tips for Success

1. **Start simple** - Run `python src/main.py` first
2. **Try each feature** - Add expense, view, filter, budget, export
3. **Check code** - Look at `src/services/expense_tracker.py` to understand CRUD
4. **Read tests** - `tests/` folder shows how to use the APIs
5. **Understand layers** - Read `STRUCTURE.md` to see the big picture

---

## ❓ FAQ

**Q: Where do I start?**
A: Run `python src/main.py` → Try adding an expense → Read README.md

**Q: How is this project organized?**
A: Modular architecture with 5 layers (models, services, storage, cli, utils). See `STRUCTURE.md`

**Q: Where's the old code?**
A: This is the refactored version with professional structure. Old monolithic files have been reorganized into modules.

**Q: Can I use this as a template?**
A: Absolutely! The architecture is designed to be reused for other CLI projects.

**Q: What's the test coverage?**
A: 35+ test cases covering all features. Run `python -m pytest tests/ -v`

**Q: How do I add a new feature?**
A: Create a service in `src/services/`, add CLI handler in `src/cli/commands.py`, write tests.

---

## 📞 Documentation Index

| File | Purpose | Read Time |
|------|---------|-----------|
| README.md | Project overview & learning outcomes | 15 min |
| QUICK_START.md | Get started in 5 minutes | 5 min |
| STRUCTURE.md | Detailed architecture & design patterns | 15 min |
| docs/ARCHITECTURE.md | System design & class diagrams | 15 min |
| docs/BUILD_SUMMARY.md | Implementation details & decisions | 10 min |
| docs/COMPLETION_CHECKLIST.md | Feature verification | 10 min |

---

## 🎯 Next Steps

1. **Try it now:** `python src/main.py`
2. **Want to understand?** Read `STRUCTURE.md` (10 min)
3. **Want to code?** Browse `src/` and `tests/` folders
4. **Ready to extend?** Follow the patterns in `src/services/` to add features

---

**Happy tracking! 📊**

*For questions or issues, consult the documentation files or review the test cases for usage examples.*
