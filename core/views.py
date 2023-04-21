from django.shortcuts import render,redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth,messages
from .models import Profile,Post,LikePost,FollowersCount,Message
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
from .forms import MessageForm



@login_required
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user_message = Message.objects.all()
    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestion = [x for x in list(all_users) if (x not in list(user_following_all))]
    current = User.objects.filter(username=request.user.username)
    final_list = [x for x in list(new_suggestion) if (x not in list(current))]
    random.shuffle(final_list)
    
    username_profile = []
    username_profile_list = []
    for users in final_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_profile_list = list(chain(*username_profile_list))
    context = {'user_profile':user_profile,
               'posts':feed_list,
               'suggestions_profile_list':suggestions_profile_list[:4] ,
               'user_message': user_message
               }
    return render(request,'core/index.html',context)

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'This Email is already in use')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'This username is not available')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email , password=password)
                user.save()

                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)
            
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'password does not match')
            return redirect('signup')
    else:
        return render(request,'core/signup.html')
 
@login_required
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    context= {'user_profile': user_profile}

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')

    return render(request,'core/setting.html',context)

@login_required
def upload(request):
    if request.method=='POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user,image=image,caption=caption)
        new_post.save()
        return redirect('index')
    else:
        return redirect('index')

@login_required   
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id,username=username) 
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')

@login_required   
def profile(request,pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_post = Post.objects.filter(user=pk)
    user_message = Message.objects.all()
    length = len(user_post)

    follower = request.user.username
    user = pk


    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text = 'unfollow'
    else:
        button_text = 'follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_post': user_post,
        'length': length,
        'button_text':button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'user_message':user_message
    }
    return render(request,'core/profile.html',context)


@login_required
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+ user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+ user)
            
    else:
        return redirect('/')


def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))

    context ={
        'user_profile': user_profile,
        'username_profile_list': username_profile_list
    }
    return render(request,'core/search.html',context)

@login_required
def send_message(request,username):
    receiver = get_object_or_404(User,username=username)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            if message.sender != message.receiver:
                message.save()
                messages.success(request,'your message was sent')
                return HttpResponseRedirect(reverse('inbox'))
            else:
                messages.error(request,'You can not send yourself a message')
        else:
            messages.error(request,'There is an error sending your message')
    else:
        form = MessageForm()
    return render(request,'core/send_message.html',{'form':form,'receiver':receiver})
    
@login_required
def inbox(request):
    messages_received = Message.objects.filter(receiver=request.user)
    messages_sent = Message.objects.filter(sender=request.user)
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    context = {'messages_received':messages_received,
    'messages_sent':messages_sent,
    'user_object': user_object,
    'user_profile': user_profile,
    }

    return render(request,'core/inbox.html',context)



        