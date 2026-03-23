# Database Table Design

This document details the schema for each table in the **KitchenHygiene** database.

### 1. [tbl_admin](file:///d:/KitchenHygiene/Admin/models.py#4-11) (Admin)
Stores primary administrator credentials.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID for the admin. |
| `admin_name` | Varchar(100) | Full name of the admin. |
| `admin_email` | Email | Unique email for login. |
| `admin_password` | Varchar(128) | Hashed password. |

---

### 2. [tbl_hotel](file:///d:/KitchenHygiene/User/models.py#6-40) (User)
The core table storing business account details and hygiene status.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID for the hotel. |
| `hotel_name` | Varchar(100) | Registered business name. |
| `hotel_email` | Email | Unique contact/login email. |
| `hotel_password` | Varchar(128) | Hashed password. |
| `hotel_contact` | Varchar(20) | Business contact number. |
| `hotel_address` | Varchar(255) | Physical location. |
| `is_verified` | Integer | 0: Pending, 1: Verified, 2: Rejected. |
| `hygiene_status`| Varchar(50) | Pending, Clean, Moderately Clean, Dirty. |
| `cert_generated`| Boolean | Indicates if a certificate exists. |
| `verified_at` | DateTime | Timestamp of admin approval. |

---

### 3. [KitchenImage](file:///d:/KitchenHygiene/User/models.py#41-47) (User)
History of kitchen snapshots with AI scoring.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The hotel owner of the image. |
| [image](file:///d:/KitchenHygiene/Admin/views.py#104-151) | ImageField | Path to the kitchen photo. |
| `uploaded_at` | DateTime | Timestamp of upload. |
| `ai_score` | Float | Probability score from YOLO. |
| `ai_rating` | Integer | Calculated rating (e.g., 1-5). |

---

### 4. [CustomerReview](file:///d:/KitchenHygiene/User/models.py#51-57) (User)
Feedback from public diners.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The hotel being reviewed. |
| `customer_name` | Varchar(100) | Name of the reviewer. |
| `rating` | Integer | Star rating (1-5). |
| [review](file:///d:/KitchenHygiene/Admin/views.py#261-285) | Text | Detailed feedback. |
| `timestamp` | DateTime | When the review was posted. |

---

### 5. [Certificate](file:///d:/KitchenHygiene/User/models.py#59-69) (User)
Issued hygiene certificates.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The recipient hotel. |
| `issue_date` | Date | Issuance timestamp. |
| `valid_till` | Date | Expiry timestamp (typically +1 year). |
| `status` | Varchar(20) | Active, Expired, Revoked. |
| [file](file:///d:/KitchenHygiene/User/views.py#37-42) | FileField | Path to the PDF certificate. |
| `cert_number` | Varchar(50) | Unique certificate identifier. |

---

### 6. [UploadModel](file:///d:/KitchenHygiene/User/models.py#73-82) (User)
Media uploads for inspection.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The hotel that uploaded. |
| [image](file:///d:/KitchenHygiene/Admin/views.py#104-151) | ImageField | Optional inspection image. |
| [video](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | FileField | Optional inspection video. |
| `uploaded_at` | DateTime | Upload timestamp. |
| `hygiene_status`| Varchar(50) | Analysis result for this specific file. |

---

### 7. [HygieneViolation](file:///d:/KitchenHygiene/User/models.py#84-94) (User)
Records of failed inspections.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The hotel in violation. |
| `issue_date` | Date | When the violation was recorded. |
| `hygiene_status`| Varchar(50) | Dirty or Moderately Clean. |
| [pdf_file](file:///d:/KitchenHygiene/Admin/views.py#210-260) | FileField | Link to the violation report PDF. |
| `fine_amount` | Decimal | Monetary penalty applied. |

---

### 8. [PublicComplaint](file:///d:/KitchenHygiene/User/models.py#95-109) (User)
Crowdsourced violation reports.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The targeted hotel. |
| [image](file:///d:/KitchenHygiene/Admin/views.py#104-151) | ImageField | Evidence image. |
| [video](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | FileField | Evidence video. |
| `description` | Text | Explanation of the issue. |
| `ai_status` | Varchar(50) | Result of AI triage. |
| `priority` | Varchar(20) | Low, Medium, High. |
| `submitted_at` | DateTime | Time of submission. |

---

### 9. [HotelWarning](file:///d:/KitchenHygiene/User/models.py#110-121) (User)
Direct communications from Admin to Hotel.

| Field | Type | Description |
| :--- | :--- | :--- |
| [id](file:///d:/KitchenHygiene/Admin/yolov8_predict.py#62-119) | Integer (PK) | Unique ID. |
| `hotel_id` | FK (tbl_hotel)| The recipient hotel. |
| `complaint_id` | FK (Complaint) | Optional link to a specific complaint. |
| `violation_id` | FK (Violation) | Optional link to a violation record. |
| `message` | Text | Warning content. |
| `fine_amount` | Decimal | Amount to be paid. |
| `is_read` | Boolean | Read/Unread status. |
| `created_at` | DateTime | Timestamp of the warning. |
