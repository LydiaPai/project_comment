from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *


class editRoom(ModelForm):
    # 在 Meta 類中，我們指定了該表單所關聯的模型為 Room。 fields 列表定義了表單中要顯示和允許編輯的字段，這裡包括 "capacity"、"numberOfBeds"、"roomType" 和 "price" 四個字段。
    class Meta:
        model = Room
        fields = ["capacity", "numberOfBeds", "roomType", "price"]


class editBooking(ModelForm):
    class Meta:
        model = Booking
        fields = ["startDate", "endDate"]


class editDependees(ModelForm):
    class Meta:
        model = Dependees
        fields = ["booking", "name"]
