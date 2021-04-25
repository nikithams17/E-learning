import datetime

import json

# import requests
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, \
    FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport, \
    NotificationStudent, NotificationStaffs, Parents, FeedBackParent, NotificationParent


def admin_home(request):
    student_count1 = Students.objects.all().count()
    staff_count = Staffs.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()

    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []
    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subjects_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs = Staffs.objects.all()
    attendance_present_list_staff = []
    attendance_absent_list_staff = []
    staff_name_list = []
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all = Students.objects.all()
    attendance_present_list_student = []
    attendance_absent_list_student = []
    student_name_list = []
    for student in students_all:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves + absent)
        student_name_list.append(student.admin.username)

    return render(request, "hod_template/main_content.html",
                  {"student_count": student_count1, "staff_count": staff_count, "subject_count": subject_count,
                   "course_count": course_count, "course_name_list": course_name_list,
                   "subject_count_list": subject_count_list,
                   "student_count_list_in_course": student_count_list_in_course,
                   "student_count_list_in_subject": student_count_list_in_subject, "subject_list": subject_list,
                   "staff_name_list": staff_name_list, "attendance_present_list_staff": attendance_present_list_staff,
                   "attendance_absent_list_staff": attendance_absent_list_staff, "student_name_list": student_name_list,
                   "attendance_present_list_student": attendance_present_list_student,
                   "attendance_absent_list_student": attendance_absent_list_student})


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        qualification = request.POST.get("qualification")
        dob = request.POST.get("dob")
        blood_group = request.POST.get("blood_group")
        teacher_roll_number = request.POST.get("teacher_roll_number")
        password = request.POST.get("password")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        ph_no = request.POST.get("ph_no")

        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        profile_pic_url = fs.url(filename)

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                  last_name=last_name, first_name=first_name, user_type=2)
            user.staffs.gender = gender
            user.staffs.address = address
            user.staffs.ph_no = ph_no
            user.staffs.dob = dob
            user.staffs.qualification = qualification
            user.staffs.blood_group = blood_group
            user.staffs.teacher_roll_number = teacher_roll_number
            user.staffs.profile_pic = profile_pic_url
            user.save()
            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request, "Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course = request.POST.get("course")
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Successfully Added Course")
            return HttpResponseRedirect(reverse("add_course"))
        except:
            messages.error(request, "Failed to Add Course")
            return HttpResponseRedirect(reverse("add_course"))


def add_student(request):
    courses = Courses.objects.all()
    sessions = SessionYearModel.object.all()
    return render(request, "hod_template/add_student_template.html", {"courses": courses, "sessions": sessions})


def add_student_save(request):
    if request.method != 'POST':
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        first_name = request.POST.get("first_name")
        password = request.POST.get("password")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        parent_username = request.POST.get("parent_username")
        blood_group = request.POST.get("blood_group")
        email = request.POST.get("email")
        address = request.POST.get("address")
        roll_number = request.POST.get("roll_number")
        # parent_roll_number = request.POST.get("parent_roll_number")
        gender = request.POST.get("gender")
        ph_no = request.POST.get("ph_no")
        dob = request.POST.get("dob")
        session_year_id = request.POST.get("session_year_id")
        course_id = request.POST.get("course")
        parent_email = request.POST.get("parent_email")
        parent_address = request.POST.get("parent_address")
        parent_password = request.POST.get("parent_password")
        father_name = request.POST.get("father_name")
        mother_name = request.POST.get("mother_name")
        father_occupation = request.POST.get("father_occupation")
        mother_occupation = request.POST.get("mother_occupation")
        parent_ph_no = request.POST.get("parent_ph_no")

        profile_pic = request.FILES['profile_pic']
        fs = FileSystemStorage()
        filename = fs.save(profile_pic.name, profile_pic)
        profile_pic_url = fs.url(filename)

        try:
            user = CustomUser.objects.create_user(username=username, password=password,
                                                  email=email, last_name=last_name, first_name=first_name, user_type=3)
            user1 = CustomUser.objects.create_user(username=parent_username, password=parent_password,
                                                   email=parent_email, last_name=mother_name, first_name=father_name,
                                                   user_type=4)
            user.students.address = address
            course_obj = Courses.objects.get(id=course_id)
            user.students.course_id = course_obj
            # parent_obj = Parents.objects.get(id=parent_roll_number)
            # user.students.parent_roll_number = parent_obj
            user.students.gender = gender
            user.students.roll_number = roll_number
            # user1.parents.parent_roll_number = parent_roll_number
            # user.students.parent_roll_number = parent_roll_number
            user.students.dob = dob
            user.students.blood_group = blood_group
            user1.parents.parent_ph_no = parent_ph_no
            user1.parents.father_occupation = father_occupation
            user1.parents.mother_occupation = mother_occupation
            user1.parents.parent_address = parent_address
            user.students.ph_no = ph_no
            user.students.profile_pic = profile_pic_url
            session_year = SessionYearModel.object.get(id=session_year_id)
            user.students.session_year_id = session_year

            user.save()
            user1.save()
            messages.success(request, "Successfully Added Student Details")
            return HttpResponseRedirect(reverse("add_student"))
        except:
            messages.error(request, "Failed to Add Student Details")
            return HttpResponseRedirect(reverse("add_student"))


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_template/add_subject_template.html", {"staffs": staffs, "courses": courses})


def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Courses.objects.get(id=course_id)
        staff_id = request.POST.get("staff")
        staff = CustomUser.objects.get(id=staff_id)
        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    staffs = Staffs.objects.all()
    return render(request, "hod_template/manage_staff_template.html", {"staffs": staffs})


def manage_student(request):
    course = request.POST.get("course")
    students = Students.objects.filter(course_id=course)
    parents = Parents.objects.all()
    return render(request, "hod_template/manage_student_template.html", {"students": students, "parents": parents})

def manage_course(request):
    courses = Courses.objects.all()
    return render(request, "hod_template/manage_course_template.html", {"courses": courses})


def manage_subject(request):
    course = request.POST.get("course")
    subjects = Subjects.objects.filter(course_id=course)
    return render(request, "hod_template/manage_subject_template.html", {"subjects": subjects})


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    return render(request, "hod_template/edit_staff_template.html", {"staff": staff, "id": staff_id})


def edit_staff_save(request):
    if request.method != 'POST':
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get("staff_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        dob = request.POST.get("dob")
        qualification = request.POST.get("qualification")
        blood_group = request.POST.get("blood_group")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        ph_no = request.POST.get("ph_no")
        teacher_roll_number = request.POST.get("teacher_roll_number")

        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()

            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.dob = dob
            staff_model.qualification = qualification
            staff_model.blood_group = blood_group
            staff_model.teacher_roll_number = teacher_roll_number
            if profile_pic_url != None:
                staff_model.profile_pic = profile_pic_url
            staff_model.gender = gender
            staff_model.ph_no = ph_no
            staff_model.save()
            messages.success(request, "Successfully Updated Staff Details")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))
        except:
            messages.error(request, "Failed to Edit Staff Details")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))


def edit_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    x = int(student_id) + 1
    courses = Courses.objects.all()
    sessions = SessionYearModel.object.all()
    parents = Parents.objects.get(admin=str(x))
    print(student_id, x)
    return render(request, "hod_template/edit_student_template.html",
                  {"student": student, "courses": courses, "sessions": sessions, "id": student_id, "parents": parents})


def edit_student_save(request):
    if request.method != 'POST':
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        address = request.POST.get("address")
        roll_number = request.POST.get("roll_number")
        gender = request.POST.get("gender")
        ph_no = request.POST.get("ph_no")
        dob = request.POST.get("dob")
        session_year_id = request.POST.get("session_year_id")
        course_id = request.POST.get("course")
        parent_email = request.POST.get("parent_email")
        parent_address = request.POST.get("parent_address")
        father_name = request.POST.get("father_name")
        mother_name = request.POST.get("mother_name")
        father_occupation = request.POST.get("father_occupation")
        mother_occupation = request.POST.get("mother_occupation")
        parent_ph_no = request.POST.get("parent_ph_no")
        parent_username = request.POST.get("parent_username")

        if request.FILES.get('profile_pic', False):
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
        else:
            profile_pic_url = None

        try:
            x = int(student_id) + 1
            user = CustomUser.objects.get(id=student_id)
            user1 = CustomUser.objects.get(id=str(x))

            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()

            user1.first_name = father_name
            user1.last_name = mother_name
            user1.username = parent_username
            user1.email = parent_email
            user1.save()

            student = Students.objects.get(admin=student_id)
            parent = Parents.objects.get(admin=str(x))

            parent.parent_address = parent_address
            parent.ph_no = parent_ph_no
            parent.father_occupation = father_occupation
            parent.mother_occupation = mother_occupation
            parent.save()

            student.address = address
            session_year = SessionYearModel.object.get(id=session_year_id)
            student.session_year_id = session_year
            student.gender = gender
            student.roll_number = roll_number
            student.dob = dob
            student.ph_no = ph_no
            course = Courses.objects.get(id=course_id)
            student.course_id = course

            if profile_pic_url != None:
                student.profile_pic = profile_pic_url

            student.save()

            # del request.session['student_id']
            messages.success(request, "Successfully Updated Student Details")
            return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
        except:
            messages.error(request, "Failed to Edit Student Details")
            return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_template/edit_subject_template.html",
                  {"subject": subject, "staffs": staffs, "courses": courses, "id": subject_id})


def edit_subject_save(request):
    if request.method != 'POST':
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")
        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            course = Courses.objects.get(id=course_id)
            subject.course_id = course
            subject.save()
            messages.success(request, "Successfully Updated Subject Details")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))
        except:
            messages.error(request, "Failed to Edit Subject Details")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    return render(request, "hod_template/edit_course_template.html", {"course": course, "id": course_id})


def edit_course_save(request):
    if request.method != 'POST':
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course")
        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()
            messages.success(request, "Successfully Updated Course Details")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))
        except:
            messages.error(request, "Failed to Edit Course Details")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))


def manage_session(request):
    return render(request, "hod_template/manage_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year = request.POST.get("session_start")
        session_end_year = request.POST.get("session_end")

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_parent_email_exist(request):
    email = request.POST.get("parent_email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_roll_number_exist(request):
    roll_number = request.POST.get("roll_number")
    user_obj = Students.objects.filter(roll_number=roll_number).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


'''@csrf_exempt
def check_parent_roll_number_exist(request):
    parent_roll_number = request.POST.get("parent_roll_number")
    user_obj = Parents.objects.filter(parent_roll_number=parent_roll_number).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)'''


@csrf_exempt
def check_teacher_roll_number_exist(request):
    teacher_roll_number = request.POST.get("teacher_roll_number")
    user_obj = Staffs.objects.filter(teacher_roll_number=teacher_roll_number).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_parent_username_exist(request):
    username = request.POST.get("parent_username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    return render(request, "hod_template/staff_feedback_template.html", {"feedbacks": feedbacks})


def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    return render(request, "hod_template/student_feedback_template.html", {"feedbacks": feedbacks})


@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def parent_feedback_message(request):
    feedbacks = FeedBackParent.objects.all()
    return render(request, "hod_template/parent_feedback_template.html", {"feedbacks": feedbacks})


@csrf_exempt
def parent_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedBackParent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    return render(request, "hod_template/staff_leave_view.html", {"leaves": leaves})


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    return render(request, "hod_template/student_leave_view.html", {"leaves": leaves})


def student_approve_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def student_disapprove_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def staff_approve_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def staff_disapprove_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def admin_view_attendance(request):
    course = request.POST.get("course")
    # print(course)
    subjects = Subjects.objects.filter(course_id=course)
    # subject2 = Subjects.objects.get(staff_id=request.user.id)
    #subjects = Subjects.objects.filter(course_id=course).filter(staff_id=request.user.id)
    #session_years = SessionYearModel.object.all()
    #return render(request, "staff_template/staff_take_attendance.html",
                  #{"subjects": subjects, "session_years": session_years})
    #subjects = Subjects.objects.all()
    session_year_id = SessionYearModel.object.all()
    return render(request, "hod_template/admin_view_attendance.html",
                  {"subjects": subjects, "session_year_id": session_year_id})


@csrf_exempt
def admin_get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id=subject)
    session_year_obj = SessionYearModel.object.get(id=session_year_id)
    attendance = Attendance.objects.filter(subject_id=subject_obj, session_year_id=session_year_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": str(attendance_single.attendance_date),
                "session_year_id": attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id,
                      "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
                      "status": student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "hod_template/admin_profile.html", {"user": user})


def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))


def select_student_class(request):
    courses = Courses.objects.all()
    return render(request, "hod_template/select_student_class_template.html", {"courses": courses})

def select_attendance_class(request):
    courses = Courses.objects.all()
    return render(request, "hod_template/select_attendance_class_template.html", {"courses": courses})

def select_subject(request):
    courses = Courses.objects.all()
    return render(request, "hod_template/select_subject_template.html", {"courses": courses})


def admin_send_notification_student(request):
    student = Students.objects.all()
    return render(request, "hod_template/student_notification.html", {"students": student})

def admin_send_notification_parent(request):
    parent = Parents.objects.all()
    return render(request, "hod_template/parent_notification.html", {"parents": parent})

def admin_send_notification_staff(request):
    staff = Staffs.objects.all()
    return render(request, "hod_template/staff_notification.html", {"staffs": staff})


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    student = Students.objects.get(admin=id)
    token = student.fcm_token
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification": {
            "title": "Student Management System",
            "body": message,
            "click_action": "https://studentmanagementsystem22.herokuapp.com/student_all_notification",
            "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to": token
    }
    headers = {"Content-Type": "application/json",
               "Authorization": "key=AAAA8jHrBqI:APA91bFFHtJXpd6HkmhHFAhr2WTO0A3_c1JWPK1Bv5FeJo1mmZ32Ck9chrfixaFEiPB0RfP0xuUUwbeRUiiFBAI5i3GYo-VrlyIxaM-pAD7NteXDfzCYxd6g944M-66MnIWnMx0hHLwB"}
    data = request.post(url, data=json.dumps(body), headers=headers)
    notification = NotificationStudent(student_id=student, message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_parent_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    parent = Parents.objects.get(admin=id)
    token = parent.fcm_token
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification": {
            "title": "Student Management System",
            "body": message,
            "click_action": "https://studentmanagementsystem22.herokuapp.com/parent_all_notification",
            "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to": token
    }
    headers = {"Content-Type": "application/json",
               "Authorization": "key=AAAA8jHrBqI:APA91bFFHtJXpd6HkmhHFAhr2WTO0A3_c1JWPK1Bv5FeJo1mmZ32Ck9chrfixaFEiPB0RfP0xuUUwbeRUiiFBAI5i3GYo-VrlyIxaM-pAD7NteXDfzCYxd6g944M-66MnIWnMx0hHLwB"}
    data = request.post(url, data=json.dumps(body), headers=headers)
    notification = NotificationParent(parent_id=parent, message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    staff = Staffs.objects.get(admin=id)
    token = staff.fcm_token
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification": {
            "title": "Student Management System",
            "body": message,
            "click_action": "https://studentmanagementsystem22.herokuapp.com/staff_all_notification",
            "icon": "http://studentmanagementsystem22.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to": token
    }
    headers = {"Content-Type": "application/json",
               "Authorization": "key=AAAA8jHrBqI:APA91bFFHtJXpd6HkmhHFAhr2WTO0A3_c1JWPK1Bv5FeJo1mmZ32Ck9chrfixaFEiPB0RfP0xuUUwbeRUiiFBAI5i3GYo-VrlyIxaM-pAD7NteXDfzCYxd6g944M-66MnIWnMx0hHLwB"}
    data = request.post(url, data=json.dumps(body), headers=headers)
    notification = NotificationStaffs(staff_id=staff, message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")


def delete_student(request, student_id):
    # student = Students.objects.get(id=student_id)
    # student.delete()
    user = CustomUser.objects.get(id=student_id)
    x = int(student_id) + 1
    user1 = CustomUser.objects.get(id=str(x))
    print(student_id, x)
    user.delete()
    user1.delete()
    return HttpResponseRedirect("/select_student_class")


def delete_staff(request, staff_id):
    user = CustomUser.objects.get(id=staff_id)
    user.delete()
    return HttpResponseRedirect(reverse("manage_staff"))


def delete_course(request, course_id):
    user = Courses.objects.get(id=course_id)
    user.delete()
    # return HttpResponseRedirect("/manage_course")
    # return render(request, "hod_template/manage_course_template.html", {"id": course_id})
    return HttpResponseRedirect(reverse("manage_course"))


def delete_subject(request, subject_id):
    user = Subjects.objects.get(id=subject_id)
    user.delete()
    return HttpResponseRedirect("/select_subject")
