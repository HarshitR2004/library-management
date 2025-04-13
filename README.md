# NITK Library Management System

A comprehensive library management system built with Django that allows students to borrow books/journals, manage reading lists, and handle library dues.

## Demo Video

[Watch Demo Video](https://drive.google.com/file/d/1WIbcvfCkUngyvC_Ef2v1LqNTV9pvb8Eb/view?usp=sharing)

## Deployment

[Live Application Link](https://iris-smartlibrary.onrender.com/) - A live deployment of the app

- Student Username - test_student1
- Librarian Username - test_lib1

- Password (common for all) - password123

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HarshitR2004/IRIS_Web_Rec25_231MT017.git
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


Optional email settings (for notifications):
```
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_USE_TLS=True
- EMAIL_HOST_USER=your.email@gmail.com
- EMAIL_HOST_PASSWORD=your-app-password
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

## Running the Project

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application:
- Admin panel: http://localhost:8000/admin/
- Main application: http://localhost:8000/


## Implemented Features

### User Management
- Multi-role authentication (Student, Librarian, Admin)
- Role-based access control
- User profile management

### Book Management
- Book catalog with search and filter
- Book details and availability tracking
- Journal management with approval system
- Genre and topic categorization

### Borrowing System
- Book borrowing requests
- Librarian approval workflow
- Return management
- Automated due date calculation
- Availability tracking

### Reading List
- Personal reading lists


### Due Management
- Automated fine calculation
- Payment history tracking
- Librarian dashboard for due management

### Email Notifications
- Borrow approval notifications
- Return confirmations
- Payment receipts
