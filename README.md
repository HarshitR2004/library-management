# NITK Library Management System

A comprehensive library management system built with Django that allows students to borrow books/journals, manage reading lists, and handle library dues.

## Demo Video

[Watch Demo Video](https://youtu.be/placeholder) - A complete walkthrough of all features

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/IRIS_Web_Rec25_231MT017.git
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

4. Configure environment variables:
- Create a `.env` file in the root directory
- Add the following variables:
```
Optional email settings (for notifications):
```
# Email configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
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

[Live Application Link]()

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
- Manual payment processing
- Payment history tracking
- Due notifications
- Librarian dashboard for due management

### Email Notifications
- Borrow approval notifications
- Return confirmations
- Payment receipts

## Planned Features

1. Online Payments
   - Integration with payment gateways
   - Online fine payment
   - Payment reminders

2. Enhanced Email System
   - Due date reminders
   - Overdue notifications

3. Additional Features
   - Book recommendations
   - Review and rating system
   - Digital content management

## Known Bugs

1. Reading List
   - Multiple additions of same book possible sometimes
   - Remove button sometimes requires double click

2. Due Management
   - Payment confirmation emails sometimes delayed

3. UI Issues
   - Responsive design breaks on some browsers
   - Form validation messages not consistently styled

## References

1. [Django Documentation](https://docs.djangoproject.com/)
2. [Bootstrap Documentation](https://getbootstrap.com/docs/)
3. [MDN Web Docs](https://developer.mozilla.org/)
4. [Real Python Tutorials](https://realpython.com/)

## Screenshots

![Login Page](screenshots/login.png)
![Student Dashboard](screenshots/student-dashboard.png)
![Book Catalog](screenshots/book-catalog.png)
![Due Management](screenshots/dues.png)
![Reading List](screenshots/reading-list.png)