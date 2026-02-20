# Comprehensive Development Prompt for RateMyKitchen

You are an expert Full Stack Django Developer with a specialty in modern, high-end "Glassmorphism" UI design. Your task is to build and complete the **RateMyKitchen** web application, ensuring a premium, consistent visual identity across all components (Guest, User/Hotel, Admin).

## 1. Project Context & Tech Stack
- **Project Name**: RateMyKitchen
- **Framework**: Django (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript (Chart.js for dashboards)
- **AI Integration**: YOLOv8 (for hygiene analysis - to be integrated via Python scripts)
- **Apps Structure**:
    - `Guest`: Public facing pages (Landing, Login, Register).
    - `User`: Hotel Dashboard and features.
    - `Admin`: Administrator Dashboard and verification tools.

## 2. Design System (Strict Adherence Required)
You must implement a **Global CSS Design System** based on the "Glassmorphism" aesthetic. All pages must share these exact styles.
- **Color Palette**:
    - Primary: `#C9A961` (Gold/Bronze)
    - Primary Dark: `#A88B4F`
    - Background: `linear-gradient(180deg, #FAFAFA 0%, #FFFFFF 100%)`
    - Text: `#1A1A1A` (Dark), `#2C3E50` (Primary Text), `#6C757D` (Secondary)
    - Success: `#10b981`, Danger: `#ef4444`
- **Glass Effect**:
    - Background: `rgba(255, 255, 255, 0.8)` or similar transparency.
    - Backdrop Filter: `blur(20px)` (Critical).
    - Borders: `1px solid rgba(201, 169, 97, 0.3)`.
    - Shadows: `0 20px 60px rgba(0,0,0,0.05)`.
- **Typography**:
    - Headers: 'Playfair Display', serif (Weights: 700, 800).
    - Body: 'Inter', sans-serif.

**Action**: Extract the CSS from `Guest/Templates/Guest/login.html` into a global static file (e.g., `static/css/glass_theme.css`) and use it as the source of truth. Create a `base.html` that includes this CSS and a standard navigation bar.

## 3. Feature Implementation Requirements

### A. Guest App
1.  **Landing Page**: Hero section with "Report Violation" and "Hotel Login/Register" CTAs.
2.  **Authentication**:
    -   **Login**: Use the existing design. Ensure it works for both Admin and Hotel Users (redirect based on role).
    -   **Register**: Create a registration form for Hotels with fields: Name, Email, Password, Address, Contact.
    -   **Public Complaint**: A form for guests to upload an image/video and description to report a hotel.

### B. Admin App (Dashboard)
1.  **Stats Dashboard**: Display 4 cards (Total Hotels, Safe Kitchens, Violations, Pending Requests) using the glass card style.
2.  **Charts**: Implement `Chart.js` to show "Hygiene Trends" (Line chart) and "Status Distribution" (Doughnut chart).
3.  **Hotel Verification**: A list of hotels with `is_verified=0`. Add "Approve" and "Reject" buttons.
4.  **Hygiene Analysis**:
    -   UI to select a verified hotel and upload an image/video.
    -   Backend stub to process this file (simulating YOLOv8 detection for now, or calling a script).
    -   Result handling: If "Clean", generate Certificate. If "Dirty", generate Violation Report.

### C. User (Hotel) App
1.  **Dashboard**: Show current status (Pending/Verified/Rejected) and Hygiene Rating.
2.  **My Certificate**: A view to download the generated PDF certificate.
3.  **Violation Reports**: A view to download violation reports.
4.  **Profile**: Edit hotel details.

## 4. Implementation Steps
1.  **Refactor CSS**: Move inline styles from `login.html` to `static/css/main.css`.
2.  **Base Template**: Create `templates/base.html` with the Navbar and Footer, extending it for all other pages.
3.  **Models**: Ensure `tbl_hotel`, `tbl_admin`, `KitchenImage`, `Certificate`, `HygieneViolation`, `PublicComplaint` are defined in `models.py` exactly as per the system design.
4.  **Views & URLs**: Create functional views for all the features listed above.
5.  **Templates**: Build `register.html`, `admin_dashboard.html`, `hotel_dashboard.html` using the *exact* same glassmorphism classes as `login.html`.

## 5. Deliverables
- Fully functional Django project.
- Consistent, responsive Glassmorphism UI.
- All database models migrated and working.
- Admin and User workflows essential for the demo.

**Start by refactoring the CSS and creating the Base Template.**
