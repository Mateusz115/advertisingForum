from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from .forms import AdForm
from django.contrib.auth.decorators import login_required
from .models import Advertisment 
from django.db.models import Q
#auth


def register(request):
    if request.method == 'GET':
        return render(request,'register.html',{'form':UserCreationForm()})
    else:#POST
        if request.POST.get('password1') == request.POST.get('password2'):
            try:
                user = User.objects.create_user(username=request.POST.get(
                    'username'), password=request.POST.get('password2'))
            except IntegrityError:
                error = 'This username is already taken. Try using different one.'
                return render(request, 'register.html', {'form': UserCreationForm(),
                'error': error})
            else:             # wykonuje się kiedy w try nie dojdzie do bledu
                user.save()
                # login user
                return redirect('home')
        else:
            error = 'Passwords did not match. Try again.'
            return render(request, 'register.html', {'form': UserCreationForm(),
            'error': error})

def log(request):
    if request.method == 'GET':    
        return render(request, 'log.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(username=request.POST.get( 'username' 
        ), password=request.POST.get( 'password' ))
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Username or password is wrong. Try again'
            return render(request, 'log.html', {'form': AuthenticationForm(), 
            'error': error})

@login_required
def logoutuser(request):
    logout(request)
    return redirect('home')
#ads

def home(request):
    ads = Advertisment.objects.all()
    return render(request,'home.html', {'ads':ads})

def detail(request, adId):
    ad = get_object_or_404(Advertisment, pk=adId)
    return render(request, 'detail.html', {'ad':ad})

@login_required
def my(request):
    ads = Advertisment.objects.filter(user=request.user)
    return render(request, 'my.html', {'ads': ads})

@login_required
def create(request):
    if request.method  == 'GET':
        return render(request, 'create.html',{'form': AdForm()})
    else:
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('home')
        else:
            error = 'Something went wrong. Please Try again.'
            return render(request, 'create.html',{'form': AdForm(), 'error':error})

@login_required
def edit(request, adId):
    ad = get_object_or_404(Advertisment, pk=adId, user=request.user) # use
    if request.method == 'GET':        
        form = AdForm(instance=ad)
        return render(request, 'edit.html', {'form':form, 'ad':ad})
    else:
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('my')
        else:
            error = 'Something went wrong. Please Try again.'
            return render(request, 'edit.html',{'form': form, 'ad':ad, 'error':error})

@login_required
def deleteAd(request, adId):
    ad = get_object_or_404(Advertisment, pk=adId, user=request.user)
    ad.delete()
    return redirect('my')

def search(request):
    keyWords = request.POST.get('search').split(" ")
    for word in keyWords:
        queryset = Advertisment.objects.filter(
            Q(company__icontains=word)| Q(desc__icontains=word))
        try:
            ads = ads | queryset
        except:
            ads = queryset
    return render(request, 'home.html', {'ads':ads})