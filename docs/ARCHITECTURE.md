# Expense Tracker - Architecture & Design

## 📐 Class Diagram

```
┌─────────────────────────────────┐
│         Expense                 │
├─────────────────────────────────┤
│ - date: Date                    │
│ - amount: Float                 │
│ - category: String              │
│ - description: String           │
├─────────────────────────────────┤
│ + __init__(date, amount, ...)   │
│ + to_dict()                     │
│ + from_dict(data)               │
│ - _validate_date()              │
│ - _validate_amount()            │
│ - _validate_category()          │
│ - _validate_description()       │
└─────────────────────────────────┘
         △
         │ manages
         │
┌─────────────────────────────────┐
│    ExpenseTracker               │
├─────────────────────────────────┤
│ - expenses: List[Expense]       │
├─────────────────────────────────┤
│ + add_expense(...)              │
│ + get_all_expenses()            │
│ + get_by_category()             │
│ + get_monthly_summary()         │
│ + delete_expense()              │
│ + save_to_file()                │
│ + load_from_file()              │
└─────────────────────────────────┘
         △
         │ reads/writes
         │
┌─────────────────────────────────┐
│   expenses.json                 │
│  (File Persistence)             │
└─────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
User Input
    │
    ▼
┌────────────────────┐
│  Validation        │  ← Checks all rules
│  Functions         │    - Date format
│  get_user_*()      │    - Amount positive
└─────────┬──────────┘    - Category valid
          │               - Description non-empty
          ▼
┌────────────────────┐
│ Expense Class      │  ← Creates instance
│ __init__()         │    with validated data
│ Validation Methods │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ ExpenseTracker     │  ← Manages list
│ add_expense()      │    of expenses
│ Internal list[]    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Save to JSON       │  ← Persist data
│ to_dict()          │
│ save_to_file()     │
└─────────┬──────────┘
          │
          ▼
    expenses.json
```

## 🎯 Feature Implementation Map

```
CLI Menu (main())
│
├─► 1. Add Expense
│   ├─► get_user_date() → validate date
│   ├─► get_user_amount() → validate amount
│   ├─► get_user_category() → validate category
│   ├─► input description → validate description
│   └─► tracker.add_expense() → Expense class
│       └─► validate → create → save to file
│
├─► 2. View All Expenses
│   ├─► tracker.get_all_expenses()
│   ├─► sorted by date (newest first)
│   └─► display_expenses_table()
│       └─► formatted output with f-strings
│
├─► 3. Filter by Category
│   ├─► get_user_category()
│   ├─► tracker.get_by_category()
│   │   └─► returns filtered list
│   └─► display_expenses_table()
│
├─► 4. Monthly Summary
│   ├─► tracker.get_monthly_summary()
│   │   └─► sums by category
│   └─► display_summary()
│       └─► formatted box output
│
└─► 5. Exit
    └─► All data already saved
```

## 📊 Validation Pipeline

```
User Input
    │
    ▼ (1)
┌──────────────────────┐
│ Input from user      │
│ (raw string)         │
└──────┬───────────────┘
       │
       ▼ (2)
┌──────────────────────┐      Valid?
│ Specific Validator   │─────────────► ✓ Return value
│ (date, amount, etc)  │
└──────┬───────────────┘
       │ Invalid
       ▼ (3)
┌──────────────────────┐
│ Raise ValueError     │
│ Custom message       │─────────► Show to user
└──────┬───────────────┘
       │
       ▼ (4)
┌──────────────────────┐
│ User re-enters       │──► Loop back to (2)
│ (chance to fix)      │
└──────────────────────┘
```

## 🗂️ File Structure

```
Expense Tracker Project
│
├── expense_tracker.py           (Main application)
│   ├── Expense class
│   │   ├── __init__()
│   │   ├── to_dict()
│   │   ├── from_dict()
│   │   └── validation methods
│   │
│   ├── ExpenseTracker class
│   │   ├── __init__()
│   │   ├── CRUD methods
│   │   ├── persistence methods
│   │   └── helper methods
│   │
│   ├── Display functions
│   │   ├── display_expenses_table()
│   │   └── display_summary()
│   │
│   ├── User input functions
│   │   ├── get_user_date()
│   │   ├── get_user_amount()
│   │   └── get_user_category()
│   │
│   └── main() - CLI menu loop
│
├── test_expense_tracker.py      (Test suite)
│   ├── test_expense_validation()
│   ├── test_tracker_crud()
│   ├── test_persistence()
│   └── test_edge_cases()
│
├── expenses.json                (Data file - auto-created)
│   └── Array of expense objects
│
└── Documentation files:
    ├── BUILD_SUMMARY.md         (This summary)
    ├── EXPENSE_TRACKER_README.md (Full reference)
    ├── QUICK_START.md           (Quick guide)
    └── EXAMPLES.md              (Usage examples)
```

## 🔀 State Flow

```
┌─────────────────────────────────────────┐
│ Application Starts                      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ ExpenseTracker.__init__()               │
│ └─ load_from_file()                     │
│    └─ Load expenses.json (if exists)    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ main() - Display Menu & Get Choice      │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┬─────────┬─────────┬─────────┐
    │                 │         │         │         │
    ▼                 ▼         ▼         ▼         ▼
  Choice=1          =2         =3        =4        =5
  Add Expense      View All   Filter    Summary    Exit
    │                │         │         │         │
    ▼                ▼         ▼         ▼         ▼
┌──────────┐  ┌──────────┐ ┌──────┐ ┌──────┐  ┌──────┐
│Validate  │  │Get All   │ │Get By│ │Get   │  │Save  │
│& Create  │  │Expenses  │ │Cat.  │ │Month.│  │&Exit │
│Expense   │  │Display   │ │Disp. │ │Disp. │  │      │
└────┬─────┘  └────┬─────┘ └──┬───┘ └──┬───┘  └──┬───┘
     │             │          │       │         │
     ▼             ▼          ▼       ▼         ▼
  Save File    Back to    Back to   Back to   End
              Menu       Menu      Menu
```

## 💾 JSON Schema

```json
[
  {
    "date": "YYYY-MM-DD",           // ISO 8601 format
    "amount": 50.00,                // Float, 2 decimals
    "category": "food",             // One of 7 categories
    "description": "string"         // Non-empty description
  },
  ...
]
```

## 🎭 Interaction Pattern

```
┌─────────────────────────────────────────┐
│ User Perspective                        │
│                                         │
│ 1. See menu                             │
│ 2. Choose option (1-5)                  │
│ 3. Provide information (if applicable)  │
│ 4. See result/feedback                  │
│ 5. Back to menu                         │
│ 6. Exit when done                       │
└─────────────────────────────────────────┘
         ▲              ▼
         └──────────────┘
              Loop


┌─────────────────────────────────────────┐
│ System Perspective                      │
│                                         │
│ 1. Load data from file (startup)        │
│ 2. Show menu to user                    │
│ 3. Process user choice                  │
│ 4. Validate any user input              │
│ 5. Update internal state                │
│ 6. Save to file                         │
│ 7. Display result to user               │
│ 8. Loop back to step 2                  │
│ 9. Save and exit on user request        │
└─────────────────────────────────────────┘
```

## 🔍 Error Handling Strategy

```
User Input (raw string)
         │
         ▼
    Try Block
         │
    ┌────┴────┐
    │          │
    ▼          ▼
Success    Exception
    │          │
    ▼          ▼
 Return    Catch Error
 Value   (ValueError, etc)
         │
         ▼
    Custom Message
    (user-friendly)
         │
         ▼
    Log/Display Error
         │
         ▼
    Prompt Retry
    or Exit
```

## 📈 Performance

```
Operation          Time Complexity    Space Complexity
─────────────────────────────────────────────────────
Add Expense        O(1)               O(1)
Get All            O(n)               O(n)
Get by Category    O(n)               O(k) where k ≤ n
Monthly Summary    O(n)               O(7) = O(1)
Save to File       O(n)               O(n)
Load from File     O(n)               O(n)

Where n = total number of expenses
```

## 🎓 Design Principles Used

```
✓ SOLID Principles
  ├─ Single Responsibility
  │  └─ Expense handles validation
  │  └─ ExpenseTracker handles operations
  │  └─ UI functions handle display
  │
  ├─ Open/Closed
  │  └─ Easy to add new categories
  │  └─ Easy to add new features
  │
  └─ Dependency Inversion
     └─ Functions accept objects, not primitives

✓ DRY (Don't Repeat Yourself)
  ├─ Validation logic in one place
  ├─ Display format in one function
  └─ Input prompts in helper functions

✓ KISS (Keep It Simple, Stupid)
  ├─ Minimal dependencies (only json, datetime)
  ├─ Clear naming conventions
  └─ Focused responsibility per class/function

✓ Fail Early
  ├─ Validate inputs immediately
  ├─ Clear error messages
  └─ User can fix and retry
```

---

**Diagrams & Design Documentation Complete** ✓
