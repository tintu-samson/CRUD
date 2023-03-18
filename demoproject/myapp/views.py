from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import RoomForm
from django.db.models import Q
#from django.http import HttpResponse
# Create your views here.


def loginPage(request):
    page = 'login-page'
    
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'user does not exist..')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"username or password does not exist..")
            
    context = {'page':page}
    return render(request,'myapp/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page='register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.post)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"an error occured during registration")
    context = {'form':form}
    return render(request,'myapp/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()
    context={'rooms':rooms,'topics':topics,'room_count':room_count}
    
    return render(request,'myapp/home.html',context)

def room(request,pk):
    rooms = Room.objects.get(id = pk)
    context = {'rooms':rooms}        
    return render(request,'myapp/room.html',context)


@login_required(login_url='login-page')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,"myapp/room_form.html",context)


@login_required(login_url='login-page')
def updateRoom(request,pk):
    room= Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse("you are not allowed here")
    
    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'myapp/room_form.html',context)


@login_required(login_url='login-page')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("you are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'room':room}
    
    return render(request,'myapp/delete.html',context)