# Expense Tracker CLI

A professional, modular expense tracking application built with Python, demonstrating clean architecture principles and best practices for scalable software design.

**Status:** ✅ Phase 1 Complete (Core Python Mastery)

This project represents the foundation of a Python Full-Stack + AI Backend Development learning journey. It showcases a professional separation of concerns architecture designed to scale seamlessly into Phase 2 (API layer), Phase 3 (Database integration), and beyond.

---

## 🎯 Quick Start

### Run the Application (5 seconds)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate

# Run the app
python src/main.py
```

**That's it!** The interactive menu will guide you through all features.

---

## 📋 Project Overview

The Expense Tracker CLI demonstrates professional Python development practices by combining:

- **Object-Oriented Programming** - Clean classes with single responsibility
- **Separation of Concerns** - Business logic decoupled from CLI logic
- **Modular Architecture** - Organized into layers (models, services, storage, cli, utils)
- **Data Persistence** - Automatic JSON save/load across sessions
- **Input Validation** - Comprehensive error handling and user feedback
- **Testing** - 35+ automated test cases
- **Professional Documentation** - Clear, maintainable code structure

---

## 📁 Modern Project Structure

```
expense-tracker/
│
├── src/                          # Application source code
│   ├── main.py                   # Entry point
│   │
│   ├── models/                   # Data layer
│   │   └── expense.py           # Expense class with validation
│   │
│   ├── services/                 # Business logic layer
│   │   ├── expense_tracker.py   # Core CRUD operations
│   │   ├── budget_service.py    # Budget management
│   │   └── export_service.py    # CSV export functionality
│   │
│   ├── storage/                  # Persistence layer
│   │   └── json_storage.py      # JSON file I/O
│   │
│   ├── cli/                      # User interaction layer
│   │   ├── menu.py              # Interactive menu system
│   │   └── commands.py          # Command handlers
│   │
│   └── utils/                    # Utilities layer
│       ├── validators.py        # Input validation
│       └── formatters.py        # Output formatting
│
├── tests/                        # Comprehensive test suite
│   ├── test_expense_tracker.py
│   └── test_expense_tracker_enhanced.py
│
├── data/                         # Data storage (auto-created)
│   ├── expenses.json
│   └── budgets.json
│
├── exports/                      # CSV exports (auto-created)
│
├── docs/                         # Technical documentation
│
├── README.md                     # This file
├── QUICK_START.md               # Quick reference guide
├── STRUCTURE.md                 # Detailed architecture
├── requirements.txt             # Dependencies
├── LICENSE                      # MIT License
└── .gitignore                   # Git configuration
```

---

## ✨ Core Features (Phase 1)

### 1. Add Expenses
Record transactions with date, amount, category, and description.
- Full validation for all inputs
- Default to today's date if not specified
- Category autocomplete available

### 2. View All Expenses
Display all recorded expenses in a formatted table (newest first).
- Easy-to-read layout
- Total calculation
- Sorted by date

### 3. Filter by Category
View expenses for specific categories:
- **Food** - Dining, groceries
- **Transport** - Gas, transit, rideshare
- **Rent** - Housing costs
- **Utilities** - Bills and services
- **Entertainment** - Recreation, subscriptions
- **Healthcare** - Medical expenses
- **Other** - Miscellaneous

### 4. Monthly Summary
Generate spending summaries by category for the current month.
- Breakdown per category
- Total spending calculation
- Easy to identify spending patterns

### 5. JSON Persistence
Automatic data persistence between sessions.
- All data saved to `data/expenses.json`
- Budget data saved to `data/budgets.json`
- Graceful handling of missing files
- Human-readable JSON format

### 6. Budget Management
Set and track spending limits per category.
- Define monthly budgets for each category
- Real-time spending vs. budget comparison
- Visual warnings when approaching 80% of budget limit

### 7. CSV Export
Export expense data for analysis in Excel or Google Sheets.
- Export individual expense records
- Export monthly summaries
- Compatible with all spreadsheet applications

### 8. Interactive CLI Menu
User-friendly terminal interface.
- Clear navigation
- Helpful error messages
- Case-insensitive input
- Graceful error handling

### 9. Professional Code Quality
Production-ready implementation.
- 35+ automated tests
- Type hints in docstrings
- Clear, maintainable code structure
- Comprehensive error messages

---

## 🏗️ Architecture Principles

This project demonstrates professional software design:

### 1. **Separation of Concerns**
- **Models** define data structures (`Expense` class)
- **Services** implement business logic (CRUD, budgets, exports)
- **Storage** handles persistence (JSON file I/O)
- **CLI** manages user interaction (menu, commands)
- **Utils** provide reusable helpers (validators, formatters)

### 2. **Dependency Injection Pattern**
Services don't create their own dependencies—they receive them, making code testable and flexible.

### 3. **Single Responsibility Principle**
Each class has one reason to change. The `Expense` class validates expenses; the `ExpenseTracker` service manages collections; the `JsonStorage` class handles file I/O.

### 4. **DRY (Don't Repeat Yourself)**
- Validation logic centralized in `validators.py`
- Output formatting centralized in `formatters.py`
- Reusable service classes

### 5. **Mockable Design**
File I/O is abstracted in a storage layer, making it easy to replace JSON with a database later without changing business logic.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Terminal / Command Prompt

### 2. Verify Python
```bash
python --version
```

### 3. Create Virtual Environment
```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows PowerShell:**
```bash
.\.venv\Scripts\Activate
```

**If activation blocked, run:**
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Application
```bash
python src/main.py
```

You should see the main menu:
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

Enter your choice (0-9):
```

---

## 📖 Usage Examples

### Interactive Mode (Recommended for First-Time Use)
```bash
python src/main.py
```
Then select options from the menu.

### Example: Adding an Expense
```
Menu selection: 1

--- Add Expense ---
Enter date (YYYY-MM-DD) [press Enter for today]: 2026-06-07
Enter amount ($): 50.00
Enter category (food/transport/rent/utilities/entertainment/healthcare/other): food
Enter description: Lunch at downtown restaurant

✓ Expense added: $50.00 (food) on 2026-06-07
```

### Example: Viewing Budget Status
```
Menu selection: 6

Budget Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category     Spent    Budget    Remaining    Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
food         $200.00  $300.00   $100.00      ✓
transport    $75.00   $150.00   $75.00       ✓
rent         $600.00  $600.00   $0.00        ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example: Monthly Summary
```
Menu selection: 4

Monthly Summary (June 2026):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
food         $150.00
transport    $80.00
rent         $600.00
utilities    $120.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL        $950.00
```

---

## 🧪 Running Tests

Execute the complete test suite:
```bash
python -m pytest tests/ -v
```

Or run tests directly:
```bash
python tests/test_expense_tracker.py
python tests/test_expense_tracker_enhanced.py
```

**Test Coverage:**
- ✅ Expense validation (date, amount, category, description)
- ✅ CRUD operations (create, read, update, delete)
- ✅ Category filtering
- ✅ Monthly summaries
- ✅ Budget management
- ✅ CSV export
- ✅ JSON persistence
- ✅ Edge cases and error handling

**Total: 35+ test cases with 100% pass rate**

---

## 📚 Documentation

| File | Purpose | Read Time |
|------|---------|-----------|
| **QUICK_START.md** | Fast 5-minute guide | 5 min |
| **STRUCTURE.md** | Detailed architecture explanation | 10 min |
| **docs/ARCHITECTURE.md** | System design and diagrams | 15 min |
| **docs/BUILD_SUMMARY.md** | Implementation details | 10 min |

---

## 🎓 Learning Outcomes

This project demonstrates practical understanding of:

### Python Fundamentals
- Classes and OOP principles
- Data structures (lists, dictionaries, sets)
- File I/O and JSON serialization
- Error handling and validation
- Functions and modularity

### Software Engineering
- Separation of concerns
- Design patterns (single responsibility, dependency injection)
- Test-driven development
- Code organization and maintainability
- Documentation and communication

### Best Practices
- Clear variable and function naming
- DRY (Don't Repeat Yourself) principle
- Comprehensive error messages
- Professional code structure
- Version control readiness

---

## 🔄 Future Roadmap

This codebase is designed to scale. Future phases will be built on this foundation:

### Phase 2 — Web Fundamentals
Add `src/api/` with FastAPI routes. Reuse existing business logic.

### Phase 3 — Database Integration
Replace `src/storage/json_storage.py` with `src/storage/database.py`. No changes needed to business logic!

### Phase 4 — Deployment
Docker containerization and cloud deployment.

### Phase 5 — AI Integration
Add semantic search and AI-powered expense categorization.

---

## 📊 Project Statistics

- **Total Code:** 1000+ lines
- **Main Application:** ~500 lines
- **Tests:** ~350 lines
- **Documentation:** Comprehensive
- **Test Cases:** 35+
- **Pass Rate:** 100%
- **Python Version:** 3.10+
- **External Dependencies:** None (uses standard library only)

---

## ✅ Project Status

**Phase 1 — Core Python Mastery:** ✅ Complete

**Completed:**
- ✅ Modular architecture (models, services, storage, cli, utils)
- ✅ All core features implemented
- ✅ Comprehensive testing (35+ tests)
- ✅ Professional documentation
- ✅ Production-ready code quality
- ✅ Backward compatible data persistence
- ✅ Scalable design for future phases

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 🎯 Quick Navigation

**First time?** → Start with `QUICK_START.md`

**Want to understand the code?** → Read `STRUCTURE.md` then browse `src/` folder

**Running into issues?** → Check `docs/` folder for detailed guides

**Ready to extend?** → Look at `src/services/` for examples of adding new features

---

**Happy tracking! 📊**
