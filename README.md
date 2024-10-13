## Assignment Portal

Overview

The Assignment Portal is a web application built using Django and MongoDB that allows users to manage assignments. The application features three distinct roles: User, Admin, and Superuser. Each role has specific permissions and functionalities, ensuring a structured workflow for managing assignments.

## Roles

### User
- Users can register and log in to the application.
- Users can submit assignments and view the assignments they have submitted previously, along with their status (whether accepted or rejected).

### Admin
- Admins can only be registered by the Superuser.
- Admins can view all assignments tagged to them and have the ability to accept or reject these assignments.

### Superuser
- There is only one Superuser in the system, with the following credentials:
  - **Username:** xyz
  - **Password:** xyz1234
- The Superuser can register new Admins and view all registered Users and Admins.
- The Superuser can also see all assignments submitted by each User to their respective Admin.

All roles can log in through the same login page. Simply enter your credentials to access the appropriate dashboard based on your role.

## Setup Instructions

```markdown
# Setup Instructions

## 1. Clone the Repository

```bash
git clone <repository-url>
cd assignment_portal
```

## 2. Create a Virtual Environment

Make sure to install `virtualenv` if you haven't already:

```bash
pip install virtualenv
```

Create a virtual environment:

```bash
virtualenv venv
```

## 3. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS and Linux

```bash
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Set up your MongoDB Database

If you are using a local MongoDB instance, ensure it's running. You can install and start MongoDB by following the [MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

You need to configure your MongoDB details in `settings.py`. Modify the `DATABASES` section like this:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'your_database_name',
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
            'username': 'your_mongodb_username',   # Optional if no auth is set
            'password': 'your_mongodb_password',   # Optional if no auth is set
            'authSource': 'admin'
        }
    }
}
```

## 6. Run Migrations (if applicable)

If your application requires database migrations, run:

```bash
python manage.py migrate
```

## 7. Run the Development Server

```bash
python manage.py runserver
```
```

You can copy and paste this formatted text directly into your `README.md` file. Let me know if you need any further adjustments!

