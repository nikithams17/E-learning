import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from student_management_app.models import Students, Subjects, CustomUser, Attendance, AttendanceReport, StudentResult, \
    FeedBackParent, Parents, NotificationParent
from student_management_app.models import Subjects, CustomUser, Students, Attendance, AttendanceReport, StudentResult, \
    FeedBackStudent, FeedBackParent, Parents


def parent_home(request):
    return render(request, "parent_template/parent_main_content.html")

def parent_view_attendance(request):
    x = int(request.user.id) - 1
    student = Students.objects.get(admin=str(x))
    course = student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    return render(request, "parent_template/parent_view_attendance.html", {"subjects": subjects})


def parent_view_attendance_post(request):
    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_date_parse = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_parse = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    x = int(request.user.id) - 1
    #print(request.user.id,x)
    subject_obj = Subjects.objects.get(id=subject_id)
    user_obj = CustomUser.objects.get(id=str(x))
    stud_obj = Students.objects.get(admin=user_obj)

    attendance = Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse),
                                           subject_id=subject_obj)
    attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

    return render(request, "parent_template/parent_attendance_data.html", {"attendance_reports": attendance_reports})

def parent_view_result(request):
    x = int(request.user.id) - 1
    student = Students.objects.get(admin=str(x))
    studentresult = StudentResult.objects.filter(student_id=student.id)
    return render(request, "parent_template/parent_result.html", {"studentresult": studentresult})

def parent_feedback(request):
    parent_id = Parents.objects.get(admin=request.user.id)
    feedback_data = FeedBackParent.objects.filter(parent_id=parent_id)
    return render(request, "parent_template/parent_feedback.html", {"feedback_data": feedback_data})


def parent_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("parent_feedback"))
    else:
        feedback_msg = request.POST.get("feedback_msg")

        parent_obj = Parents.objects.get(admin=request.user.id)
        try:
            feedback = FeedBackParent(parent_id=parent_obj, feedback=feedback_msg, feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("parent_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("parent_feedback"))

def parent_all_notification(request):
    parent = Parents.objects.get(admin=request.user.id)
    notifications = NotificationParent.objects.filter(parent_id=parent.id)
    return render(request, "parent_template/all_notification.html", {"notifications": notifications})

def parent_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    parent = Parents.objects.get(admin=user)
    return render(request, "parent_template/parent_profile.html",
                  {"parent": parent})


def parent_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("parent_profile"))
    else:

        password = request.POST.get("password")
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            # customuser.first_name = first_name
            # customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            '''
            student = Students.objects.get(admin=customuser)
            student.address = address
            student.dob = dob
            student.gender = gender
            student.ph_no = ph_no
            student.save()
            '''
            messages.success(request, "Successfully Updated Password")
            return HttpResponseRedirect(reverse("parent_profile"))
        except:
            messages.error(request, "Failed to Update Password")
            return HttpResponseRedirect(reverse("parent_profile"))