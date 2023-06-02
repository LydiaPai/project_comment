from django.db import models
from django.utils import timezone

from accounts.models import Guest
from abc import ABC, abstractmethod
# design pattern：factory
class Room(models.Model):
    number = models.IntegerField(primary_key=True)
    capacity = models.SmallIntegerField()
    numberOfBeds = models.SmallIntegerField()
    price = models.FloatField()
    statusStartDate = models.DateField(null=True)
    statusEndDate = models.DateField(null=True)
    roomType = models.CharField(max_length=10)

    def __str__(self):
        return str(self.number)


class KingRoom(Room):
    def __init__(self, number, capacity, numberOfBeds, price):
        super().__init__(number, capacity, numberOfBeds, price)
        self.roomType = 'King'


class LuxuryRoom(Room):
    def __init__(self, number, capacity, numberOfBeds, price):
        super().__init__(number, capacity, numberOfBeds, price)
        self.roomType = 'Luxury'


class NormalRoom(Room):
    def __init__(self, number, capacity, numberOfBeds, price):
        super().__init__(number, capacity, numberOfBeds, price)
        self.roomType = 'Normal'


class EconomicRoom(Room):
    def __init__(self, number, capacity, numberOfBeds, price):
        super().__init__(number, capacity, numberOfBeds, price)
        self.roomType = 'Economic'


class RoomFactory:
    @staticmethod
    def create_room(room_type, number, capacity, number_of_beds, price):
        if room_type == 'King':
            return KingRoom(number, capacity, number_of_beds, price)
        elif room_type == 'Luxury':
            return LuxuryRoom(number, capacity, number_of_beds, price)
        elif room_type == 'Normal':
            return NormalRoom(number, capacity, number_of_beds, price)
        elif room_type == 'Economic':
            return EconomicRoom(number, capacity, number_of_beds, price)
        else:
            raise ValueError('Invalid room type')


# 這個Booking模型類的作用是存儲預訂的相關信息，包括預訂的房間號、客人、預訂日期以及開始和結束日期。它還提供了計算與預訂相關的depen數量的方法
class Booking(models.Model):
    roomNumber = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, null=True, on_delete=models.CASCADE)
    dateOfReservation = models.DateField(default=timezone.now)
    startDate = models.DateField()
    endDate = models.DateField()

    def numOfDep(self):
        return Dependees.objects.filter(booking=self).count()

    def __str__(self):
        return str(self.roomNumber) + " " + str(self.guest)


class Dependees(models.Model):
    booking = models.ForeignKey(Booking,   null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.booking) + " " + str(self.name)


class Refund(models.Model):
    guest = models.ForeignKey(Guest,   null=True, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Booking, on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return str(self.guest)


class RoomServices(models.Model):
    SERVICES_TYPES = (
        ('Food', 'Food'),
        ('Cleaning', 'Cleaning'),
        ('Technical', 'Technical'),
    )

    curBooking = models.ForeignKey(
        Booking,   null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    createdDate = models.DateField(default=timezone.now)
    servicesType = models.CharField(max_length=20, choices=SERVICES_TYPES)
    price = models.FloatField()

    def str(self):
        return str(self.curBooking) + " " + str(self.room) + " " + str(self.servicesType)
