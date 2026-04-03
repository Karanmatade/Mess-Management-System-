# 🍽️ Hostel Mess Management System

> A full-stack web application for managing hostel mess operations — students, attendance, menu, and billing — built with **Python Flask**, **MySQL**, and **premium Glassmorphism UI**.

---

## 📁 Project Structure

```
Mess Management System/
├── frontend/
│   ├── index.html          # Login page
│   ├── dashboard.html      # Dashboard with KPI + Charts
│   ├── students.html       # Student CRUD
│   ├── attendance.html     # Mark + track attendance
│   ├── menu.html           # Weekly menu management
│   ├── billing.html        # Generate & track bills
│   ├── reports.html        # Analytics & charts
│   ├── css/style.css       # Design system
│   └── js/api.js           # API helper + toast + utils
├── backend/
│   ├── app.py              # Flask entry point
│   ├── db.py               # MySQL connection pool
│   ├── .env                # Environment config
│   ├── requirements.txt
│   └── routes/
│       ├── auth.py         # Login + JWT
│       ├── dashboard.py    # KPI aggregation
│       ├── students.py     # Student CRUD
│       ├── attendance.py   # Mark / summary
│       ├── menu.py         # Weekly menu
│       ├── billing.py      # Bill generation
│       └── reports.py      # Analytics
└── database.sql            # Schema + seed data
```

---

## ⚙️ Prerequisites

- Python 3.9+
- MySQL 8.0+
- Node.js (optional, for serving frontend)

---

## 🚀 Setup Instructions

### Step 1 — MySQL Database

```bash
mysql -u root -p < database.sql
```

If you have a password: `mysql -u root -pYOURPASSWORD < database.sql`

---

### Step 2 — Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure database (edit .env)
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=mess_management

# Start server
python app.py
```

> Flask will run at **http://localhost:5000**

---

### Step 3 — Frontend

Open `frontend/index.html` directly in your browser, **or** serve with Python:

```bash
cd frontend
python -m http.server 8080
```

Then visit **http://localhost:8080**

> ⚠️ Browsers block `fetch` from `file://` — use the Python server above.

---

## 🔑 Default Login

| Username | Password |
|----------|----------|
| `admin`  | `admin@123` |

---

## 🌐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Admin login → JWT |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/` | KPIs + charts data |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | List all (with search/filter) |
| GET | `/api/students/{id}` | Get one student |
| POST | `/api/students/` | Add student |
| PUT | `/api/students/{id}` | Update student |
| DELETE | `/api/students/{id}` | Delete student |
| PATCH | `/api/students/{id}/toggle-status` | Toggle active/inactive |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/attendance/?date=YYYY-MM-DD` | Get by date |
| GET | `/api/attendance/student/{id}?month=YYYY-MM` | Student history |
| POST | `/api/attendance/mark` | Mark individual |
| POST | `/api/attendance/bulk-mark` | Mark all students |
| GET | `/api/attendance/summary?month=YYYY-MM` | Monthly summary |

### Menu
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/menu/` | Full week menu |
| GET | `/api/menu/today` | Today's menu |
| GET | `/api/menu/{day}` | Single day |
| PUT | `/api/menu/{day}` | Update day |
| PUT | `/api/menu/bulk` | Update full week |

### Billing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/billing/?month=YYYY-MM` | List bills |
| POST | `/api/billing/generate` | Generate from attendance |
| PATCH | `/api/billing/{id}/pay` | Mark paid |
| PATCH | `/api/billing/{id}/unpay` | Mark pending |
| GET | `/api/billing/student/{id}` | Student bill history |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/monthly-revenue` | 12-month revenue |
| GET | `/api/reports/meal-consumption` | 6-month meal trends |
| GET | `/api/reports/top-students` | Top 10 by meals |
| GET | `/api/reports/payment-stats?month=YYYY-MM` | Payment summary |

---

## 💰 Pricing

- Default cost per meal: **₹60**
- Monthly bill = Total meals attended × ₹60
- Configurable per bill generation

---

## 🛡️ Security

- Passwords hashed with **bcrypt** (12 rounds)
- All protected routes require **JWT Bearer token**
- Token expires after **8 hours**
- CORS enabled for local development

---

## 🎨 UI Features

- Glassmorphism design with dark theme
- Animated orbs on login page
- Smooth modal transitions
- Toast notifications (success/error/warning/info)
- Loading states on all data fetches
- Chart.js for analytics visualization
- Mobile-responsive sidebar
- Toggle switches for meal attendance

---

## 📊 Sample Data

The database includes:
- **10 students** (rooms A-101 to D-402)
- **7-day attendance** history for first 6 students
- **Full week menu** (Monday–Sunday)
- **8 billing records** for current month (mixed paid/pending)
- Admin: `admin` / `admin@123`
