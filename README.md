# NITK Library Management System

A comprehensive library management system built with Django that allows students to borrow books/journals, manage reading lists, and handle library dues.

## Demo Video

[Watch Demo Video](https://youtu.be/placeholder) - A complete walkthrough of all features

## Deployment

[Live Application Link](https://iris-smartlibrary.onrender.com/) - A live deployment of the app

- Student Username - test_student1
- Librarian Username - test_lib1

- Password (common for all) - password123

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
   - Filter Books does not work sometimes

## References

1. [Django Documentation](https://docs.djangoproject.com/)
2. [Bootstrap Documentation](https://getbootstrap.com/docs/)
5. [Chai aur Code Django Playlist](https://www.youtube.com/playlist?list=PLu71SKxNbfoDOf-6vAcKmazT92uLnWAgy)


