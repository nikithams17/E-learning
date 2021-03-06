import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from student_management_app.EmailBackEnd import EmailBackEnd


def showDemoPage(request):
    return render(request, "demo.html")


def ShowLoginPage(request):
    return render(request, "login_page.html")


def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get("email"),
                                         password=request.POST.get("password"))
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("staff_home"))
            elif user.user_type == "3":
                return HttpResponseRedirect(reverse("student_home"))
            else:
                return HttpResponseRedirect(reverse("parent_home"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")


def GetUserDetails(request):
    if request.user != None:
        return HttpResponse("User : " + request.user.email + " usertype : " + str(request.user.user_type))
    else:
        return HttpResponse("Please Login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/7.16.1/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/7.16.1/firebase-app.js");' \
         'var firebaseConfig = {' \
         '   apiKey: "AIzaSyBdC3UQqErbwpqRYnOtZXoKO8lvQkZpe9U",' \
         '   authDomain: "studentmanagementsystem-75790.firebaseapp.com",' \
         '   databaseURL: "https://studentmanagementsystem-75790.firebaseio.com",' \
         '   projectId: "studentmanagementsystem-75790",' \
         '   storageBucket: "studentmanagementsystem-75790.appspot.com",' \
         '   messagingSenderId: "1040219571874",' \
         '   appId: "1:1040219571874:web:9e24bea9a7bde37a78b9fb",' \
         '   measurementId: "G-21CH37QKTE"' \
         '};' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging = firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'


    return HttpResponse(data,content_type="text/javascript")