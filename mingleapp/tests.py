from django.test import TestCase, Client
from django.urls import reverse
from .forms import CustomUserCreationForm, CreatePostForm
from .models import CustomUser, StatusUpdate, Post, FriendRequest
from .serializers import UserSerializer




class FormTests(TestCase):

    def test_custom_user_creation_form(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'strong_password_123',
            'password2': 'strong_password_123',
            'profile_picture': None  
        }
        form = CustomUserCreationForm(data)
        self.assertTrue(form.is_valid())

    def test_create_post_form(self):
        # First create a user
        user = CustomUser.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            username='john.doe',  # Ensure unique usernames for multiple tests
            password='strong_password_123'
        )
        
        data = {
            'content': 'This is a test post.',
            'author': user.id  
        }
        form = CreatePostForm(data)
        self.assertTrue(form.is_valid())


class UserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = CustomUser.objects.create_user(
            username='john.doe',
            email='john.doe@example.com',
            password='strong_password_123'
        )

    def test_login_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'john.doe',
            'password': 'strong_password_123'
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_view(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('profile', kwargs={'user_id': self.user1.id}))
        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'password1': 'strong_password_123',
            'password2': 'strong_password_123',
        }
        response = self.client.post(reverse('register'), data)
        # Adjusting to check for 302 which is a common redirect code after registration
        self.assertEqual(response.status_code, 302)

def test_update_profile(self):
    self.client.force_login(self.user1)
    data = {
        'email': 'john.doe@updated.com',
        'bio': 'Updated bio',
        'hobbies': 'Updated hobbies',
        'education': 'Updated education',
        'location': 'Updated location',
    }
    response = self.client.post(reverse('update_profile', kwargs={'user_id': self.user1.id}), data)
    # Adjusting to check for 302 which is a common redirect code after updating profile
    self.assertEqual(response.status_code, 302)




class CustomUserModelTest(TestCase):
    
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            email='testuser1@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.user2 = CustomUser.objects.create_user(
            email='testuser2@example.com',
            password='password123',
            first_name='Jane',
            last_name='Smith'
        )

    def test_create_custom_user(self):
        self.assertEqual(self.user1.email, 'testuser1@example.com')
        self.assertEqual(self.user1.username, 'testuser1')
        self.assertEqual(self.user1.first_name, 'John')
        self.assertEqual(self.user1.last_name, 'Doe')
        self.assertTrue(self.user1.is_active)

    def test_post_status_update(self):
        status_text = "This is a status update!"
        status = StatusUpdate.objects.create(user=self.user1, text=status_text)
        self.assertEqual(status.text, status_text)
        self.assertEqual(status.user, self.user1)

    def test_create_post(self):
        post_content = "This is a post content!"
        post = Post.objects.create(content=post_content, author=self.user1)
        self.assertEqual(post.content, post_content)
        self.assertEqual(post.author, self.user1)

    def test_send_friend_request(self):
        friend_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertEqual(friend_request.from_user, self.user1)
        self.assertEqual(friend_request.to_user, self.user2)



class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user_attributes = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_active': True,
            'is_staff': False,
            'bio': 'Test bio',
            'hobbies': 'Test hobbies',
            'education': 'Test education',
            'location': 'Test location',
            'username': 'johndoe',
            'password': 'securepassword123'
        }
        self.user = CustomUser.objects.create(**self.user_attributes)

 

    def test_user_serializer_creates_user(self):
        unique_attributes = {
            'email': 'unique_test@example.com',
            'first_name': 'John',
            'last_name': 'Unique',
            'is_active': True,
            'is_staff': False,
            'bio': 'Test bio unique',
            'hobbies': 'Test hobbies unique',
            'education': 'Test education unique',
            'location': 'Test location unique',
            'username': 'uniquejohndoe',
            'password': 'securepassword123'
        }
        serializer = UserSerializer(data=unique_attributes)
        self.assertTrue(serializer.is_valid(), serializer.errors)  # Will print errors if not valid
        user = serializer.save()
        self.assertEqual(CustomUser.objects.count(), 2)  # Original user + new one from serializer
        self.assertEqual(user.email, unique_attributes['email'])
