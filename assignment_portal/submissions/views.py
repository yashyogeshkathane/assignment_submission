from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, AssignmentForm, AdminCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password
from datetime import datetime
from .models import CustomUser
from bson import ObjectId



# View for the superuser dashboard (only accessible to superusers)
@login_required
def superuser_dashboard(request):
    if not request.user.is_superuser:  # Ensure that only superusers can access this view
        return redirect('login')       # Redirect non-superusers to login

    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['assignment_db']
    users_collection = db['submissions_customuser']
    assignments_collection = db['assignments']

    # Find users who are not superusers or custom superusers
    users = users_collection.find({'is_superuser': False, 'is_superuser_custom': False})
    users_list = list(users)

    # Find admins
    admins = users_collection.find({'is_admin': True, 'is_superuser': False, 'is_superuser_custom': False})
    admins_list = list(admins)

    # Find all assignments
    assignments = assignments_collection.find()
    assignments_list = []

    # For each assignment, find user and admin details using usernames and include task
    for assignment in assignments:
        user = users_collection.find_one({'username': assignment.get('user_username')})      # Get user details
        admin = users_collection.find_one({'username': assignment.get('admin_username')})    # Get admin details

        assignments_list.append({
            'user_username': user['username'] if user else 'Unknown User',                   # Handle missing user data
            'admin_username': admin['username'] if admin else 'Unknown Admin',               # Handle missing admin data
            'status': assignment.get('status', 'No Status'),                                 # Get assignment status, default to 'No Status'
            'task': assignment.get('task', 'No Task'),                                       # Get task, default to 'No Task'
            'assignment_id': str(assignment['_id'])  # Use MongoDB's _id
        })

    # Handle empty database
    message = "No users or admins available in the database." if not users_list else None
    
    #Passing users,admin,assignments to the template
    return render(request, 'superuser_dashboard.html', {
        'users': users_list,
        'admins': admins_list,
        'assignments': assignments_list,
        'message': message
    })

# View for registering an admin (only accessible to superusers)
@login_required
def register_admin(request):
    if request.method == 'POST':                 # If the form is submitted
        form = AdminCreationForm(request.POST)   # Bind data to the form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')

            # Create a new admin user
            admin_user = CustomUser(
                username=username,
                password=make_password(password1),        # Hash the password before saving
                is_admin=True,
                is_superuser=False,
                is_superuser_custom=False
            )
            admin_user.save()                             # Save the admin user in the database
            messages.success(request, ' ')
            return redirect('superuser_dashboard')
        else:
            messages.error(request, 'There was an error with your form. Please try again.')
    else:
        form = AdminCreationForm()    # Create a blank form for the initial GET request


    return render(request, 'register_admin.html', {'form': form})

# View for the admin/user dashboard (different content for admin vs regular users)
@login_required
def dashboard(request):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['assignment_db']
    assignments_collection = db['assignments']

    # Check if the user is a superuser
    if request.user.is_superuser:
        return redirect('superuser_dashboard')          # Redirect superusers to the superuser dashboard

    # Check if the user is an admin
    elif request.user.is_admin:
        # Admins see only assignments assigned to them by their username by the users.
        assignments = assignments_collection.find({'admin_username': request.user.username})
        
        # Prepare assignments list for template
        assignments_list = []
        for assignment in assignments:
            assignments_list.append({
                'assignment_id': str(assignment['_id']),  # Convert ObjectId to string
                'user_username': assignment['user_username'],    # The user who submitted the assignment
                'task': assignment['task'],                      # The task assigned
                'status': assignment['status'],                   # The status of the assignment
                'submitted_at': assignment['submitted_at']       # The submission date and time
            })

        return render(request, 'admin_dashboard.html', {'assignments': assignments_list})              

    # Regular users see their assignments
    else:
        assignments = assignments_collection.find({'user_username': request.user.username})
        assignments_list = []
        for assignment in assignments:
            assignments_list.append({
                'assignment_id': str(assignment['_id']),  # Convert ObjectId to string
                'task': assignment['task'],               # The task assigned
                'status': assignment['status'],           # The status of the assignment
                'admin_username': assignment.get('admin_username', 'N/A'),  # Fetch admin username or default to 'N/A'
                'submitted_at': assignment['submitted_at']                  # Submission date and time
            })

        return render(request, 'user_dashboard.html', {
            'assignments': assignments_list,
            'username': request.user.username
        })

# View for uploading a new assignment (for regular users)
@login_required
def upload_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            # Connect to MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['assignment_db']
            assignments_collection = db['assignments']

            # Prepare the assignment data
            assignment_data = {
                'user_username': request.user.username,  # Set the logged-in user's username
                'task': form.cleaned_data['task'],  # Task from the form
                'admin_username': form.cleaned_data['admin_username'],  # Admin username from the form
                'status': 'pending',  # Default status
                'submitted_at': datetime.now(),  # Set current datetime
            }

            # Insert into MongoDB
            assignments_collection.insert_one(assignment_data)
            messages.success(request, ' ')
            return redirect('dashboard')  # Redirect to the user dashboard after upload
    else:
        form = AssignmentForm()

    return render(request, 'upload_assignment.html', {'form': form})

# View for accepting an assignment (for admins)
@login_required
def accept_assignment(request, assignment_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['assignment_db']
    assignments_collection = db['assignments']

    # Find the assignment using the MongoDB _id
    assignment = assignments_collection.find_one({'_id': ObjectId(assignment_id)})

    if assignment:
        if request.user.username == assignment['admin_username']:            # Ensure the admin is authorized to accept
            result = assignments_collection.update_one(
                {'_id': ObjectId(assignment_id)},
                {'$set': {'status': 'accepted', 'updated_at': datetime.now()}}              # Update the status to 'accepted'
            )

            if result.modified_count > 0:  # Check if the document was updated
                messages.success(request, f'')
            else:
                messages.warning(request, 'Assignment was not updated. It may already be accepted/rejected.')
        else:
            messages.error(request, 'You are not authorized to accept this assignment.')
    else:
        messages.error(request, 'Assignment does not exist.')

    return redirect('dashboard')

# View for rejecting an assignment (for admins)
@login_required
def reject_assignment(request, assignment_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['assignment_db']
    assignments_collection = db['assignments']

    # Find the assignment using the MongoDB _id
    assignment = assignments_collection.find_one({'_id': ObjectId(assignment_id)})

    if assignment:
        if request.user.username == assignment['admin_username']:
            result = assignments_collection.update_one(
                {'_id': ObjectId(assignment_id)},
                {'$set': {'status': 'rejected', 'updated_at': datetime.now()}}                # Update the status to 'rejected'
            )

            if result.modified_count > 0:  # Check if the document was updated
                messages.success(request, f' ')
            else:
                messages.warning(request, 'Assignment was not updated. It may already be accepted/rejected.')
        else:
            messages.error(request, 'You are not authorized to reject this assignment.')
    else:
        messages.error(request, 'Assignment does not exist.')

    return redirect('dashboard')

def home(request):
    return render(request, 'home.html')

# View to register a new user
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # No need for set_password, it's already done
            login(request, user)  # Log the user in immediately after registration
            messages.success(request, 'Registration successful!')
            return redirect('login')  # Redirect to login or another page
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# View for log in users/admins/superusers
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

# View for logging out users/admins/superusers
def logout_view(request):
    logout(request)
    return redirect('login')
