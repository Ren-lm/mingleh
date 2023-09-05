from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Post

# The code I wrote starts here
# The CustomUserCreationForm class inherits from Django's UserCreationForm to customize the registration process.
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'profile_picture']  # Fields to be displayed in the form

    # Overriding the save method to add custom behavior
    def save(self, commit=True):
        # Calling the save method of the super class (UserCreationForm) but telling it not to save to the database yet.
        user = super().save(commit=False)

        # Setting the username to be the prefix of the email (before the "@").
        user.username = self.cleaned_data.get("email").split('@')[0]

        # If commit is True (default), save the user object to the database.
        if commit:
            user.save()
        return user

# This form is used for updating the profile of a CustomUser.
class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser  
        # Fields to be displayed in the form for updating user profile.
        fields = ['profile_picture', 'email', 'bio', 'hobbies', 'education', 'location']

# This form is used for creating a new post.
class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post  
        fields = ['content']  # Field to be displayed in the form for creating a new post

        # The code I wrote ends here