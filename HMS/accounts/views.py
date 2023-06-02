from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

from django.contrib import messages
from hotel.models import Guest
from datetime import datetime, date, timedelta
import random

# Own imports
from accounts.models import *
from room.models import *
from hotel.models import *
from .forms import *
# Create your views here.

# 註冊頁面
def register_page(request):
    form = CreateUserForm()
# 驗證當前用戶是否通過身分驗證
    # 已登入
    if request.user.is_authenticated:
        return redirect('home')
    # 未登入
    else:
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            # 驗證表單有沒有符合格式
            if form.is_valid():
                # email是否已經存在於database
                if (len(User.objects.filter(email=request.POST.get("email"))) != 0):
                    messages.error(
                        request, 'Email address is alredy taken')
                    return redirect('login')
                # 儲存
                user = form.save()
                # 獲取用戶名
                username = form.cleaned_data.get('username')
                # 獲取名為"guest"的用戶組對象
                group = Group.objects.get(name="guest")
                # 將用戶添加到"guest"用戶組
                user.groups.add(group)
                # 保存Guest模型實例到數據庫
                curGuest = Guest(
                    user=user, phoneNumber=request.POST.get("phoneNumber"))
                curGuest.save()
                # 在當前會話中添加一條成功消息，指示成功創建了用戶賬號
                messages.success(
                    request, 'Guest Account Was Created Succesfuly For ' + username)

                return redirect('login')
        # 如果未滿足條件，則執行以下操作
        context = {'form': form}
        return render(request, 'accounts/register.html', context)

# 使用了@login_required裝飾器來要求用戶在訪問該視圖前先進行登錄
@login_required(login_url='login')
def add_employee(request):
    # 獲取當前用戶所屬的用戶組中的第一個用戶組名稱，並將其轉換為字符串。這個變量用於確定用戶在視圖中的角色。
    role = str(request.user.groups.all()[0])
    path = role + "/"

    form = CreateUserForm()
    # 用於選擇員工角色的表單實例
    form2 = ROLES()
    form3 = CreateEmployeeForm()

    if request.method == 'POST':
        post = request.POST.copy()  # to make it mutable
        post['phoneNumber'] = "+90" + post['phoneNumber']
        request.POST = post

        form = CreateUserForm(request.POST)
        form2 = ROLES(request.POST)
        form3 = CreateEmployeeForm(request.POST)

        if form.is_valid() and form2.is_valid() and form3.is_valid():
            user = form.save()
            employee = form3.save()
            employee.user = user
            employee.save()

            username = form.cleaned_data.get('username')

            role = form2.cleaned_data.get("ROLES_TYPES")

            group = Group.objects.get(name=role)
            user.groups.add(group)

            messages.success(
                request, role + ' Account Was Created Succesfuly For ' + username)

            return redirect('employees')

    context = {
        'form': form,
        'form2': form2,
        'form3': form3,
        "role": role
    }
    return render(request, path + "add-employee.html", context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "Username or Password is incorrect")

        context = {}
        return render(request, 'accounts/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def guests(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    # 查詢所有預訂記錄，並按照客人進行分組，計算每個客人的預訂次數，並按預訂次數降序排序。
    topRange = Booking.objects.all().values("guest").annotate(total=Count("guest")).order_by("-total")
    # 設置顯示前幾名客人的數量限制
    topLimit = 10
    # 創建一個空列表，用於存儲排名靠前的客人信息
    topList = []
    # 使用循環遍歷topRange，將排名靠前的客人對象添加到topList中，直到達到數量限製或遍歷完所有客人
    for t in topRange:
        if len(topList) > 10:
            break
        else:
            topList.append(Guest.objects.get(id=t.get("guest")))
    # 查詢所有預訂記錄，並將起始日期和結束日期與當前日期進行比較，篩選出在最近30天內有預訂的客人。
    bookings = Booking.objects.all()
    fd = datetime.combine(date.today()-timedelta(days=30), datetime.min.time())
    ld = datetime.combine(date.today(), datetime.min.time())
    # 創建一個空列表guests，用於存儲符合篩選條件的客人對象
    guests = []

    for b in bookings:
        if b.endDate >= fd.date() and b.startDate <= ld.date():
            if b.guest not in guests:
                guests.append(b.guest)
     # 檢查是否存在名為"filterDate"的字段，如果是，則表示用戶正在進行日期篩選
    if request.method == "POST":
        if "filterDate" in request.POST:

            if request.POST.get("f_day") == "" and request.POST.get("l_day") == "":
                guests = Guest.objects.all()

                context = {
                    "role": role,
                    "guests": guests,
                    "fd": "",
                    "ld": ""
                }
                return render(request, path + "guests.html", context)

            if request.POST.get("f_day") == "":
                fd = datetime.strptime("1970-01-01", '%Y-%m-%d')
            else:
                fd = request.POST.get("f_day")
                fd = datetime.strptime(fd, '%Y-%m-%d')

            if request.POST.get("l_day") == "":
                ld = datetime.strptime("2030-01-01", '%Y-%m-%d')
            else:
                ld = request.POST.get("l_day")
                ld = datetime.strptime(ld, '%Y-%m-%d')

            for b in bookings:
                if b.endDate >= fd.date() and b.startDate <= ld.date():
                    if b.guest not in guests:
                        guests.append(b.guest)
       
        if "filterGuest" in request.POST:
            guests = Guest.objects.all()
            users = User.objects.all()
            if (request.POST.get("id") != ""):
                users = users.filter(
                    id__contains=request.POST.get("id"))
                guests = guests.filter(user__in=users)

            if (request.POST.get("name") != ""):
                users = users.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                guests = guests.filter(user__in=users)

            if (request.POST.get("email") != ""):
                users = users.filter(email__contains=request.POST.get("email"))
                guests = guests.filter(user__in=users)

            if (request.POST.get("number") != ""):
                guests = guests.filter(
                    phoneNumber__contains=request.POST.get("number"))

            context = {
                "role": role,
                "guests": guests,
                "id": request.POST.get("id"),
                "name": request.POST.get("name"),
                "email": request.POST.get("email"),
                "number": request.POST.get("number")
            }
            return render(request, path + "guests.html", context)

        if "top" in request.POST:
            topRange = Booking.objects.all().values("guest").annotate(
                total=Count("guest")).order_by("-total")
            topList = []
            topLimit = request.POST.get("top")
            for t in topRange:
                if len(topList) >= int(topLimit):
                    break
                else:
                    topList.append(Guest.objects.get(id=t.get("guest")))
            context = {
                "role": role,
                "guests": guests,
                "topList": topList,
                "topLimit": topLimit,
                "fd": fd,
                "ld": ld
            }
            return render(request, path + "guests.html", context)
    context = {
        "role": role,
        "guests": guests,
        "topList": topList,
        "topLimit": topLimit,
        "fd": fd,
        "ld": ld
    }
    return render(request, path + "guests.html", context)


@login_required(login_url='login')
def employees(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    employees = Employee.objects.all()

    if request.method == "POST":
        if "filter" in request.POST:
            users = User.objects.all()
            if (request.POST.get("id") != ""):
                users = users.filter(
                    id__contains=request.POST.get("id"))
                employees = employees.filter(user__in=users)

            if (request.POST.get("name") != ""):
                users = users.filter(
                    Q(first_name__contains=request.POST.get("name")) | Q(last_name__contains=request.POST.get("name")))
                employees = employees.filter(user__in=users)

            if (request.POST.get("email") != ""):
                users = users.filter(email__contains=request.POST.get("email"))
                employees = employees.filter(user__in=users)

            if (request.POST.get("number") != ""):
                employees = employees.filter(
                    phoneNumber__contains=request.POST.get("number"))

            if (request.POST.get("filterRole") != ""):
                try:
                    group = Group.objects.get(
                        name__contains=request.POST.get("filterRole"))
                except:
                    group = None
                users = users.filter(groups=group)
                employees = employees.filter(user__in=users)

        context = {
            "role": role,
            "employees": employees,
            "id": request.POST.get("id"),
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "number": request.POST.get("number"),
            "filterRole": request.POST.get("filterRole")
        }
        return render(request, path + "employees.html", context)

    context = {
        "role": role,
        "employees": employees
    }
    return render(request, path + "employees.html", context)


@login_required(login_url='login')
def employee_details(request, pk):
    if request.method == 'POST':
        user = User.objects.get(id=pk)
        employee = Employee.objects.get(user=user)
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        employee.phoneNumber = request.POST.get("phoneNumber")
        user.save()
        employee.save()
        return redirect("home")

    role = str(request.user.groups.all()[0])
    path = role + "/"

    tempUser = User.objects.get(id=pk)
    employee = Employee.objects.get(user=tempUser)
    tasks = Task.objects.filter(employee=employee)
    context = {
        "role": role,
        "employee": employee,
        "tasks": tasks
    }
    return render(request, path + "employee-profile.html", context)


@ login_required(login_url='login')
def employee_details_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    tempuser = User.objects.get(id=pk)
    employee = Employee.objects.get(user=tempuser)

    form1 = editEmployee(instance=employee)
    form2 = editUser(instance=tempuser)

    context = {
        "role": role,
        "employee": employee,
        "user": tempuser,
        "form1": form1,
        "form2": form2
    }

    if request.method == "POST":
        form1 = editEmployee(request.POST, instance=employee)
        form2 = editUser(request.POST, instance=tempuser)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()

    return render(request, path + "employee-edit.html", context)


@ login_required(login_url='login')
def guest_edit(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"
    #　根據傳遞的pk值（主鍵）從數據庫中獲取對應的User對象。
    tempuser = User.objects.get(id=pk)
    # 根據獲取到的User對象，獲取對應的Guest對象
    guest = Guest.objects.get(user=tempuser)
    form1 = editGuest(instance=guest)
    form2 = editUser(instance=tempuser)

    context = {
        "role": role,
        "guest": guest,
        "form1": form1,
        "form2": form2,
        "user": tempuser,
    }

    if request.method == "POST":
        form1 = editGuest(request.POST, instance=guest)
        form2 = editUser(request.POST, instance=tempuser)
        if form1.is_valid and form2.is_valid:
            form1.save()
            form2.save()

    return render(request, path + "guest-edit.html", context)


@login_required(login_url='login')
def guest_profile(request, pk):
    tempUser = User.objects.get(id=pk)
    guest = Guest.objects.get(user=tempUser)

    if request.method == 'POST':
        tempUser.first_name = request.POST.get("first_name")
        tempUser.last_name = request.POST.get("last_name")
        guest.phoneNumber = request.POST.get("phoneNumber")
        tempUser.save()
        guest.save()
        return redirect("home")
    role = str(request.user.groups.all()[0])
    path = role + "/"

    eventAttendees = EventAttendees.objects.filter(guest=guest)
    bookings = Booking.objects.filter(guest=guest)
    context = {
        "role": role,
        "guest": guest,
        "eventAttendees": eventAttendees,
        "bookings": bookings
    }
    return render(request, path + "guest-profile.html", context)


@login_required(login_url='login')
def tasks(request):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    tempEmp = Employee.objects.get(user=request.user)
    tasks = Task.objects.filter(employee=tempEmp)

    context = {
        "role": role,
        'tasks': tasks
    }
    if request.method == "POST":
        if "markAsComplete" in request.POST:
            tid = request.POST.get("tid")
            Task.objects.get(id=tid).delete()
            return redirect("tasks")

        if "filter" in request.POST:
            if(request.POST.get("id") != ""):
                tasks = tasks.filter(id=request.POST.get("id"))

            if(request.POST.get("desc") != ""):
                tasks = tasks.filter(
                    description__contains=request.POST.get("desc"))

            if(request.POST.get("fd") != ""):
                tasks = tasks.filter(startTime__gte=request.POST.get("fd"))

            if(request.POST.get("ed") != ""):
                tasks = tasks.filter(endTime__lte=request.POST.get("ed"))

            context = {
                "role": role,
                "tasks": tasks,
                "id": request.POST.get("id"),
                "desc": request.POST.get("desc"),
                "fd": request.POST.get("fd"),
                "ed": request.POST.get("ed")
            }

    return render(request, path + "tasks.html", context)


@login_required(login_url='login')
def completeTask(request, pk):
    role = str(request.user.groups.all()[0])
    path = role + "/"

    task = Task.objects.get(id=pk)
    if request.method == "POST":
        task.delete()
        return redirect("tasks")

    context = {
        "role": role,
        'task': task

    }
    return render(request, path + "completeTask.html", context)

