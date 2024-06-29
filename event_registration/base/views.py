from django.shortcuts import render,redirect
from .models import User,Event,Submission
from .forms import SubmissionForm,CustomUserCreateForm,UserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from PIL import Image
from django.contrib.auth.hashers import make_password
from django.contrib import messages
# Create your views here.

def login_page(request):
    page = 'login'

    if request.method=='POST':
        user = authenticate(email=request.POST['email'],password=request.POST['password'])
        # print('userrrrrrrrrr======',user)
        if user is not None:
            login(request,user)
            messages.success(request,'You have successfully logged in.')
            return redirect('home')
        else:
            messages.error(request,'Email or Password is incorrect')
            return redirect('login')
    context = {'page':page}
    return render(request,'login_register.html',context)

def logout_user(request):
    logout(request)
    messages.info(request,'User was logged out!')
    return redirect('login')

def register_page(request):
    page='register'
    form = CustomUserCreateForm()
    if request.method=='POST':
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request,user)
            messages.success(request,'User account was created')
            return redirect('login')
        else: 
            messages.error(request,'An error has occured during registration')
    context = {'page':page,'form':form}
    return render(request,'login_register.html',context)

def home_page(request):
    limit = request.GET.get('limit')
    if limit == None:
        limit=20

    users = User.objects.filter(hackathon_participant = True)
    count = users.count()
    users = users[0:limit]
    events = Event.objects.all()
    context = {'users':users,'events':events,'count':count}

    return render(request,'home.html',context)

def user_page(request,pk):
    user = User.objects.get(id=pk)
    print('user_data',user)
    context = {'user': user}
    return render(request,'profile.html',context)

@login_required(login_url='login')
def account_page(request):
    user = request.user

    # img = user.avatar
    # img = Image.open(user.avatar)
    # new_size = (10,10)
    # img = img.resize(new_size)
    # img.show()
    # user.avatar = img
    # user.save()
    # print('IMG:',img)

    context = {'user':user}
    return render(request,'account.html',context)

@login_required(login_url='login')
def edit_account(request):
    form = UserForm(instance=request.user)

    if request.method=='POST':
        # form = UserForm(request.POST,request.FILES,instance=request.user)
        # print("ORIGINAL IMAGE",request.FILES.get('avatar'))
        # img = Image.open(request.FILES.get('avatar'))
        # newsize = (10,10)
        # img = img.resize(newsize)
        # request.FILES['avatar'] = img
        # print('NEW IMAGE',request.FILES.get('avatar'))
        form = UserForm(request.POST,request.FILES,instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            img = Image.open(user.avatar)
            newsize = (10,10)
            img = img.resize(newsize)
            print('img:',dir(img))
        return redirect('account')
    
    context = {'form':form}
    return render(request,'user_form.html',context)
@login_required(login_url='login')
def change_password(request):

    if request.method=='POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        new_pass = make_password(password1)
        print(new_pass)
        if password1==password2:
            new_pass = make_password(password1)
            request.user.password = new_pass
            request.user.save()
            messages.success(request,'You have successfully reset your password')
            return redirect('account')
    return render(request,'change_password.html')

def event_page(request,pk):
    event = Event.objects.get(id=pk)
    registered = False
    submitted = False
    if request.user.is_authenticated:
        registered = request.user.events.filter(id=event.id).exists()
        print('registered=',registered)
        submitted = Submission.objects.filter(participant=request.user,event=event).exists()
    context = {'event': event,'registered':registered,'submitted':submitted}
    return render(request,'event.html',context)

@login_required(login_url='login')
def registration_confirmation(request,pk):
    event = Event.objects.get(id=pk)

    if request.method == 'POST':
      event.participants.add(request.user)
      return redirect('event',pk=event.id)

    return render(request,'event_confirmation.html',{'event': event})     

@login_required(login_url='login')
def submission_form(request,pk):
    event = Event.objects.get(id=pk)
    print(event)
    form = SubmissionForm()

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.participant = request.user
            submission.event = event
            submission.save()
            return redirect('account')

    context = {'event': event,'form':form}
    return render(request,'submit_form.html',context)    

# Add owner authentication
@login_required(login_url='login')
def update_submission(request,pk):
    submission = Submission.objects.get(id=pk)

    if request.user != submission.participant:
        return HttpResponse("You can't be here!!!!")
    event = submission.event
    form = SubmissionForm(instance=submission)
    if request.method=='POST':
        form = SubmissionForm(request.POST,instance=submission)
        if form.is_valid():
            form.save()
            return redirect('account')
    context = {'form':form,'event':event}

    return render(request,'submit_form.html',context)
