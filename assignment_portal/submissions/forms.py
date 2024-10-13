from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Assignment

# Form for creating a new user (inherits from UserCreationForm)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser                                    # Use the CustomUser model
        fields = ['username', 'password1', 'password2']       # Specify the fields to be included in the form (username, password1, password2)



# Form for creating a new admin
class AdminCreationForm(forms.ModelForm):
    # Two password fields (password and confirm password) for the admin creation form
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

    class Meta:
        model = CustomUser                   # Use the CustomUser model
        fields = ['username']                 # Only the username is taken from the user, the rest is custom

     # Custom validation for password matching and username uniqueness
    def clean(self):
        cleaned_data = super().clean()                # Call the parent clean method to get the cleaned data
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Validate that the passwords match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")           # Raise validation error if passwords do not match

        # Additional validation for the username can be added here
        username = cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose another one.")

        return cleaned_data

# Form for uploading or assigning a new task/assignment
class AssignmentForm(forms.ModelForm):
    admin_username = forms.CharField(max_length=150, label="Admin Username")  # Add admin username field

    class Meta:
        model = Assignment            # Use the Assignment model
        fields = ['task', 'admin_username']  # Use admin_username instead of admin

