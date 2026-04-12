# MINI PROJECT REPORT
## Title: Mess Management System

**DEPARTMENT OF INFORMATION TECHNOLOGY**
**Academic Year 2025-2026**

---

### Title: Mess Management System

### Aim: 
To develop a comprehensive, real-time Hostel Mess Management System using HTML, CSS, JavaScript for the frontend, and Python for the backend to efficiently automate student attendance, manage meal-based billing, and generate comprehensive reports for hostel administration.

### Objectives:
1. To store and manage student details accurately over multiple billing cycles.
2. To provide an interactive attendance calendar for admins to track and toggle daily breakfast, lunch, and dinner consumption.
3. To accurately automate financial calculations and billing based on individual meal pricing and daily attendance.
4. To implement automated billing synchronization, 30-day billing cycle alerts, and daily attendance resets.
5. To export attendance and billing reports robustly into Excel (.csv) format.

---

### Non-Functional Requirements

**Performance:**
The dashboard and reporting interfaces are optimized to load quickly, processing JSON attendance data seamlessly to ensure a lag-free experience for the mess administrator during peak usage times.

**Reliability:**
The system ensures that data entries (like toggling a student's meal status) are safely written and retrieved from the backend records (e.g., `att.json` and database tables) reliably without data loss.

**Usability:**
The web application features a premium, modern, and interactive user interface. It simplifies tasks for the administrator, allowing them to perform bulk actions directly from an integrated calendar intuitive layout.

**Compatibility:**
The system is accessible through any modern web browser, and the backend easily initiates across Windows environments via a provided `start.bat` execution script.

---

### Architecture / System Design

**Architecture Components:**
- **Presentation Layer (Frontend):** HTML, CSS, and Vanilla JavaScript (`dashboard.html`, `students.html`, `reports.html`) forming a dynamic single-page-like experience.
- **Domain/Business Logic Layer (Backend):** Python-based server that processes attendance inputs, manages the billing logic, and handles cycle reset calculations.
- **Data Layer:** Lightweight JSON-based file storage (`att.json`) and associated databases to keep track of active students, meal schemas, and attendance histories.

---

### Technology Stack

**Frontend Technologies:**
- **HTML5:** Semantic structuring of web pages and admin forms.
- **CSS3:** Premium styling with responsive design logic (avoiding generic UI for specialized visual excellence).
- **Vanilla JavaScript:** DOM manipulation, interactive attendance calendar handling.

**Backend & Storage:**
- **Python:** Core functionality server, API endpoints, logic processing (`requirements.txt`).
- **File System / JSON / Data logic:** Local data storage handling offline-first principles while processing real-time tracking (via `att.json`).
- **Batch Scripting:** `start.bat` handles environment setup and running the localhost server.

---

### Key Features Implementation

**Attendance Management:**
- Fully interactive attendance calendar module where admins can click on a specific date and view a detailed list of active students.
- Ability to mark or toggle specific meals (Breakfast, Lunch, Dinner).

**Billing Module:**
- Independent configuration of meal prices.
- Dynamic generation of totals tied directly to the attendance matrices.
- 30-day billing cycle automated alert system.

**Reporting & Exports:**
- Comprehensive reporting dashboard.
- Export functionality tightly integrated to process structural data into CSV formats, formatted perfectly for Excel viewing.

**Hostel System Finalization:**
- Automated resets when cycles expire.
- Automated API polling to ensure front-end data matches back-end data gracefully.

---

### Testing Strategy

**Manual & UI Testing:**
- Validated front-end UI responsiveness for calendar toggles to ensure visual state changes directly fire backend API requests.
- End-to-end trials of exporting the CSV reports to ensure data formatting integrity.

**System Integration:**
- Verifying the `start.bat` launch operations bind the server and load frontend statically without crashing.
- Simulating 30-day cycle changes to test the system's threshold alerts successfully offloading old data.

---

### Conclusion
The Mess Management System successfully digitizes the traditional, manual methods of maintaining hostel mess data. By transitioning to a web-based, Python-backed solution, the system ensures real-time accuracy in billing and seamless attendance tracking. Advanced features like the 30-day cycle alerts and independent meal pricing eliminate billing discrepancies. Ultimately, it delivers a highly usable, premium dashboard to drastically reduce administrative workload and guarantee precise financial records.
