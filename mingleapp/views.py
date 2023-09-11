from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, UpdateProfileForm, CreatePostForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, Post, FriendRequest, Chat
from django.db import IntegrityError
from django.db.models.query_utils import Q
from django.http import JsonResponse
from operator import attrgetter
from itertools import chain
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions


import logging

logger = logging.getLogger(__name__)

class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            print(f"Integrity error: {e}")  # Print directly to the console
            if 'email' in str(e):
                form.add_error('email', 'This email already exists.')
            else:
                form.add_error(None, 'An error occurred. Please try again.')
            return render(self.request, self.template_name, {'form': form})
        except Exception as e:
            print(f"General exception: {e}")  # Print directly to the console
            form.add_error(None, 'An unexpected error occurred. Please try again.')
            return render(self.request, self.template_name, {'form': form})


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('homepage')


class UserLogoutView(LogoutView):
    template_name = 'registration/logout.html'


def index(request):
    return render(request, 'index.html')


@login_required(login_url='/login')
def profile_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_posts = Post.objects.filter(author=user)
    friends = user.friends.all()
    all_posts = sorted(chain(user_posts), key=attrgetter('timestamp'), reverse=True)
    context = {'user': user, 'posts': all_posts, 'friends': friends, 'request_user': request.user}
    return render(request, 'profile.html', context)  # Ensure {% csrf_token %} in the template if there's a form.


def update_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Initiate the form with the user instance for GET requests too
    form = UpdateProfileForm(instance=user)

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                form.save()
                return redirect('profile', user_id=user.id)
            except IntegrityError as e:
                if 'email' in str(e):
                    form.add_error('email', 'This email already exists.')
                elif 'username' in str(e):
                    form.add_error('username', 'This username already exists.')
                else:
                    form.add_error(None, 'An error occurred. Please try again.')
                return render(request, 'update_profile.html', {'form': form})  # return to the same page with the error
    
    # Handles GET request
    return render(request, 'update_profile.html', {'form': form})


@login_required(login_url='/login')
def homepage_view(request):

    friends = request.user.friends.all()
    exclude_users = [friend.id for friend in friends]
    exclude_users += [request.user.id]
    users = CustomUser.objects.exclude(id__in=exclude_users)

    # Fetching friend requests for the logged-in user.
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    sent_friend_requests = [friend_.to_user.id for friend_ in sent_friend_requests]

    friends_posts = Post.objects.filter(author__in=friends)
    user_posts = Post.objects.filter(author=request.user)
    all_posts = sorted(chain(friends_posts, user_posts), key=attrgetter('timestamp'), reverse=True)

    # Include friend_requests in the context.
    context = {'posts': all_posts, 'users': users, 'friends': friends, 'friend_requests': friend_requests,
               'sent_friend_requests': sent_friend_requests}
    
    if request.method == 'POST':
        if 'add_post' in request.POST:
            form = CreatePostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('homepage')
            context['form'] = form
        elif 'accept' in request.POST or 'decline' in request.POST:
            friend_request_id = request.POST.get('friend_request_id')
            friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
            
            if 'accept' in request.POST:
                friend_request.from_user.friends.add(friend_request.to_user)
                friend_request.to_user.friends.add(friend_request.from_user)
            friend_request.delete()
            return redirect('homepage')
        elif 'search' in request.POST:
            search_term = request.POST.get('search_term')
            users = CustomUser.objects.filter(Q(first_name__contains=search_term) | Q(last_name__contains=search_term)).exclude(id__in=[request.user.id])
            searched_users = []
            for user in users:
                if request.user.id not in [user_.id for user_ in user.friends.all()]:
                    searched_users.append({
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_friend': False,
                        'is_request_sent': user.id in sent_friend_requests
                    })
                else:
                    searched_users.append({
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_friend': True,
                        'is_request_sent': user.id in sent_friend_requests
                    })

            context['searched_users'] = searched_users
    else:
        context['form'] = CreatePostForm()

    return render(request, 'homepage.html', context)  # Ensure {% csrf_token %} in the template.


def send_friend_request(request, user_id):
    if request.method == 'POST':
        to_user = get_object_or_404(CustomUser, id=user_id)
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        if created:
            return redirect('homepage')
        else:
            return redirect('homepage')
            # return HttpResponse("You already sent a friend request to this user.")


def accept_friend_request(request, friend_request_id):
    if request.method == 'POST':
        # Checks if the POST request is for accepting a friend request
        if 'accept' in request.POST or 'decline' in request.POST:
            friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
            
            if 'accept' in request.POST:
                friend_request.from_user.friends.add(friend_request.to_user)
                friend_request.to_user.friends.add(friend_request.from_user)
            
            friend_request.delete()
            return redirect('homepage')
        
        # Checks if the POST request is for adding a friend
        elif 'add_friend' in request.POST:
            friend_id = request.POST.get('friend_id')
            friend = get_object_or_404(CustomUser, id=friend_id)
            FriendRequest.objects.create(from_user=request.user, to_user=friend)
            return redirect('homepage') 

    return redirect('homepage')


def search_user_request(request):
    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        from django.db.models.query_utils import Q
        users = CustomUser.objects.filter(Q(first_name__contains=search_term) | Q(last_name__contains=search_term))
        for user in users:
            print(user.first_name)
            print(user.last_name)
        return redirect('homepage')


@login_required(login_url='/login')
def chat_view(request, user_id):
    friends = request.user.friends.all()
    friend = request.user.friends.filter(id=user_id).first()
    if not friend:
        return redirect('homepage')

    chats_with_friend = Chat.objects.filter((Q(from_user=friend) & Q(to_user=request.user)) | (Q(from_user=request.user) & Q(to_user=friend))).order_by('create_at')
    context = {'friends': friends, 'friend': friend, 'chat': chats_with_friend}
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Chat.objects.create(from_user_id=request.user.id, to_user_id=user_id, content=message)

        return redirect(request.path_info)

    return render(request, 'chat.html', context)




class UserApiView(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
