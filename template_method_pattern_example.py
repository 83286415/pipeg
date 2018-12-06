from abc import ABCMeta, abstractmethod
import os, sys

# 抽象方法 Trip
class Trip():
    def __init__(self):
        pass

    @abstractmethod
    def setTransport(self):
        pass

    @abstractmethod
    def day1(self):
        pass

    @abstractmethod
    def day2(self):
        pass

    @abstractmethod
    def day3(self):
        pass

    @abstractmethod
    def returnHome(self):
        pass

    #  模板方法 tmplate_method()
    def itinerary(self):
        self.setTransport()
        self.day1()
        self.day2()
        self.day3()
        self.returnHome()


# 具体类 VeniceTrip
class VeniceTrip(Trip):
    def setTransport(self):
        print("Take a boat and find your way in the Grand Canal")

    def day1(self):
        print("Visit St Mark Basilica in St Mark Square")

    def day2(self):
        print("Enjoy the food near the Rialto Bridge")

    def day3(self):
        print("Get souvenirs for friends and get back")

    def returnHome(self):
        print("Get souvenirs for friends and get back")


# 具体类 MaldivesTrip
class MaldivesTrip(Trip):
    def setTransport(self):
        print("On foot,on any island,Wow")

    def day1(self):
        print("Enjoy the marine life of Banana Reef")

    def day2(self):
        print("Go for the water sports and snorkelling")

    def day3(self):
        print("Relax on the beach and enjoy the sun")

    def returnHome(self):
        print("Dont feel like leaving the beach..")


# 客户端
class TravelAgency:
    def arrange_trip(self):
        choice = input("What kind of place you like to go historical or to a beach")
        if choice == "historical":
            self.trip = VeniceTrip()
            self.trip.itinerary()
        if choice == "beach":
            self.trip = MaldivesTrip()
            self.trip.itinerary()



TravelAgency().arrange_trip()