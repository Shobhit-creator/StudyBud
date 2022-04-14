from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic, Message, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.http import HttpResponse

# Create your views here.

#  ctrl + / ---> to comment in one shot
# rooms = [

#     {'id': 1, 'name': 'Let\'s Learn Python' },

#     {'id': 2, 'name': 'Design with me' },

#     {'id': 3, 'name': 'Frontend developers' }

# ]

# always write function name in small letter and class name start with capital letter
def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:# redirecting user to home page if he already logged in.
        return redirect('home')

    if request.method=='POST':
        username = request.POST.get('email').lower()# to get user lowercase
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username OR password does not exists")
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)#to get the user rightaway
            user.username = user.username.lower()
            user.save()
            login(request, user)# user logged in then sending to home page
            return redirect('home')
        else:
            messages.error("An error occured during registration")
    context = {'form': form}
    return render(request, 'base/login_register.html', context)




def home(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else ''
    rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q) #here matching with description attribute with query 
            )
    topics = Topic.objects.all()[0:5]
    rooms_count = rooms.count()# count method of list which is faster than the len method of list
    room_messages =  Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()#Many to one relationship https://stackoverflow.com/questions/42080864/set-in-django-for-a-queryset
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}         
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)# created will evaluate to false if create else true if select
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )

        return redirect('home')

        # if form.is_valid():
        #     room = form.save(commit=False)# give an instance of room
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')#here home is the name of the home route in the urls.py


    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room =  Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")#wtih this we are not allow one user to edit or delete room of other user
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic 
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form':form, 'topics': topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Your are not allowed here!!")

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})




