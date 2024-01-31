from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from .models import Category,Doctor,TimeSlot,Appointment
from django.db.models import Q 
from django.db import connection
import mysql.connector
import razorpay
from datetime import date
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

# Create your views here.
def landingPage(request):
    return render(request,'index.html')

def authenticatePage(request):
    mydict = {
        'error':False
    }
    if request.user.is_authenticated:
       return redirect('/home')
    else: 
        if request.method == 'POST':
            username=request.POST.get('signup_username')
            email=request.POST.get('signup_email')
            password=request.POST.get('signup_password')
            # print(username,email,password)
            if username is not None:
                try:
                    new_user = User.objects.create_user(username=username,email=email,password=password)
                    new_user.save()
                    login(request,new_user)
                except:
                    mydict = {'error':True}
                    return render(request,'authentication.html',context=mydict)
                return render(request,'home.html')
        if request.method == 'POST':
            Lusername = request.POST.get('login_username')
            Lpass = request.POST.get('login_password')
            user = authenticate(username=Lusername,password=Lpass)
            # print(Lusername,Lpass)
            # print(user)
            if user is not None:
                login(request,user)
                return redirect('/home')
            else:
                return render(request,'authentication.html')
            
        return render(request,'authentication.html')

    


def homePage(request):
    if request.user.is_authenticated:
        category_objs = Category.objects.all()
        doctors_objs = Doctor.objects.all()
        n = len(doctors_objs)
        appointments_objs = Appointment.objects.all()
        todaydate = date.today()
        an = 0
        ca = 0
        for i in appointments_objs:
            if i.user == request.user:
                an = an + 1
                if i.appointment_date < todaydate:
                    ca = ca + 1

        context = {
            'category_objs':category_objs,
            'doctors_objs':doctors_objs,
            'n':n,
            'appointments_objs' : appointments_objs, 
            'todaydate': todaydate,
            'an':an,
            'ca':ca,
        }

        return render(request,'home.html',context)
    else:
        return render(request,'authentication.html')
    
def signout(request):
    logout(request)
    return redirect('/')
def availability(request,uid):
            # mydb = mysql.connector.connect(
            # host="localhost",
            # user="root",
            # password="",
            # database="reservation_system"
            # )
            cursor= connection.cursor()
            # print("hello " +uid)
            query='''SELECT time_slots FROM appointment_timeslot LEFT JOIN appointment_appointment ON appointment_timeslot.time_slots = appointment_appointment.time_slot AND appointment_appointment.appointment_date = %s AND appointment_appointment.doctor_id = %s WHERE appointment_appointment.time_slot IS NULL;'''
            doctors_obj = Doctor.objects.get(uid=uid)
            id_ =str(doctors_obj.uid)
            id = id_.replace("-", "")
            selected_date=str(request.GET.get('date'))
            cursor.execute(query,(selected_date,id))
            result=cursor.fetchall()
            # blocked_slots=Appointment.objects.filter(doctor=uid,appointment_date=selected_date).values("time_slot")
            # available_timeslot=TimeSlot.objects.all()
            # print(available_timeslot)
            # print(blocked_slots)
            # result=[element for element in available_timeslot if element not in blocked_slots]
            # result=list(set(available_timeslot)-set(blocked_slots))
            print(result)
            book_date = request.GET.get("date")
            client = razorpay.Client(auth= ('rzp_test_AJENNDOZFIdTd3','2aS49WIxV9Uo7II6hlmHRAOP'))
            payment = client.order.create({ 'amount' : doctors_obj.doctor_price * 100 , 'currency' : 'INR', 'payment_capture' : 1})    
            context={
                'doctors_obj':doctors_obj,
                'result':result,
                'date':selected_date,
                'payment':payment,
            }
            cursor.close()
            # mydb.close()
            return render(request,'doctordetail.html',context)
def doctorDetail(request,uid):

    if request.user.is_authenticated:
        doctors_obj = Doctor.objects.get(uid=uid)

        context = {
            'doctors_obj':doctors_obj,
            
        }
        return render(request,'doctordetail.html',context)
    else:
        return render(request,'authentication.html')

# mydb=mysql.connector.connect(
#         host="localhost",
#         password='',
#         user='root',
#         database='hospital_system'
#     )
#         mycursor = mydb.cursor()
#         mycursor.execute("SELECT DISTINCT doctor_category FROM abs_doctors")
#         result=mycursor.fetchall()
#         print(result)
#         mydict = {
#             'result':result
#         }

def appointment(request):
    if request.user.is_authenticated:
        category_objs = Category.objects.all()
        doctors_objs = Doctor.objects.all()
        n = len(doctors_objs)
        sort_by = request.GET.get('sort_by')
        search = request.GET.get('search')
        category = request.GET.getlist('category')
        if sort_by is not 'Recommended':
            if sort_by == 'Lowest':
                doctors_objs=doctors_objs.order_by('doctor_price')
            elif sort_by == 'Highest':
                doctors_objs=doctors_objs.order_by('-doctor_price')
        if search is not None:
            doctors_objs = doctors_objs.filter(
                Q(doctor_name__icontains=search)|
                Q(description__icontains=search) )
        if category is not 'Category':    
            if len(category):
                doctors_objs=doctors_objs.filter(category__category_name__in = category).distinct

        

        context = {
            'category_objs':category_objs,
            'doctors_objs':doctors_objs,
            'sort_by':sort_by,
            'search':search,
            'category':category,
            'n':n 
        }

        return render(request,'appointment.html',context)
    else:
        return render(request,'authentication.html')
    
def confirm(request,uid,date):
    if request.method == 'GET':
        selected_date=date
        doctors_obj = Doctor.objects.get(uid=uid)
        t_slot = request.GET.get('time_slot')
        u = request.user
        appointment = Appointment(appointment_date=selected_date,time_slot=t_slot,doctor=doctors_obj,user=u)
        appointment.save()
        
        subject = "DocLab: Appoiment Details"
        message = "Your Appointment has been confirmed with "+doctors_obj.doctor_name+", on "+selected_date+" between "+t_slot+". Thank You."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [u.email]
        send_mail(subject,message,from_email,recipient_list)
    return render(request,'success.html')

def confirmpayment(request,uid,date):
    if request.method == 'GET':
        selected_date=date
        doctors_obj = Doctor.objects.get(uid=uid)
        t_slot = request.GET.get('time_slot')
        u = request.user    
        appointment = Appointment(appointment_date=selected_date,time_slot=t_slot,doctor=doctors_obj,user=u,is_paid=True)
        appointment.save()
        subject = "DocLab: Appoiment Details"
        message = "Your Appointment has been confirmed with "+doctors_obj.doctor_name+", on "+selected_date+" between "+t_slot+". Thank You. Payment Done."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [u.email]
        send_mail(subject,message,from_email,recipient_list)

    return render(request,'success.html')

def cancel(request,id):
    appointment_obj = Appointment.objects.get(appointment_id=id)
    appointment_obj.delete()
    return HttpResponseRedirect(reverse('homePage'))