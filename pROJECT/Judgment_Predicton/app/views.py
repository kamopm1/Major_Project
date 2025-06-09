from django.shortcuts import render,redirect,get_object_or_404
from . models import *
from django.contrib import messages
import datetime
from django.db.models import Q
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from datetime import date

def public_register(request):
	if request.method == 'POST':
		lname = request.POST.get('lname')
		fname = request.POST.get('fname')
		email = request.POST.get('mail')
		uname = request.POST.get('uname')
		psw = request.POST.get('psw')
		pnum = request.POST.get('num')
		country = request.POST.get('country')
		state = request.POST.get('state')
		city = request.POST.get('city')
		addr = request.POST.get('addr')
		crt = User_Detail.objects.create(first_name=fname,last_name=lname,
		mail=email,mobile=pnum,username=uname,password=psw,
		country=country,state=state,city=city,address=addr)
		if crt:
			messages.success(request,'Registered Successfully')
	return render(request,'public_register.html',{})
def public_login(request):
	if request.session.has_key('public'):
		return redirect("dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('uname')
			password =  request.POST.get('psw')
			post = User_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('uname')
				request.session['public'] = username
				a = request.session['public']
				sess = User_Detail.objects.only('id').get(username=a).id
				request.session['p_id']=sess
				return redirect("dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'public_login.html',{})
def dashboard(request):
	if request.session.has_key('public'):
		return render(request,'dashboard.html',{})
	else:
		return render(request,'public_login.html',{})
def logout(request):
    try:
        del request.session['public']
        del request.session['p_id']
    except:
     pass
    return render(request, 'public_login.html', {})
def police_login(request):
	if request.session.has_key('police'):
		return redirect("police_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('uname')
			password =  request.POST.get('psw')
			post = Police_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('uname')
				request.session['police'] = username
				a = request.session['police']
				sess = Police_Detail.objects.only('id').get(username=a).id
				request.session['police_id']=sess
				return redirect("police_dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'police_login.html',{})
def lawyer_login(request):
	if request.session.has_key('lawyer'):
		return redirect("lawyer_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('uname')
			password =  request.POST.get('psw')
			post = Lawyer_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('uname')
				request.session['lawyer'] = username
				a = request.session['lawyer']
				sess = Lawyer_Detail.objects.only('id').get(username=a).id
				request.session['lawyer_id']=sess
				return redirect("lawyer_dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'lawyer_login.html',{})
def lawyer_dashboard(request):
	if request.session.has_key('lawyer'):
		return render(request,'lawyer_dashboard.html',{})
	else:
		return render(request,'lawyer_login.html',{})
def lawyer_logout(request):
    try:
        del request.session['lawyer']
        del request.session['lawyer_id']
    except:
     pass
    return render(request, 'lawyer_login.html', {})
def judge(request):
	if request.session.has_key('judge'):
		return redirect("judge_dashboard")
	else:
		if request.method == 'POST':
			username = request.POST.get('uname')
			password =  request.POST.get('psw')
			post = Judge_Detail.objects.filter(username=username,password=password)
			if post:
				username = request.POST.get('uname')
				request.session['judge'] = username
				a = request.session['judge']
				sess = Judge_Detail.objects.only('id').get(username=a).id
				request.session['judge_id']=sess
				return redirect("judge_dashboard")
			else:
				messages.success(request, 'Invalid Username or Password')
	return render(request,'judge.html',{})
def judge_dashboard(request):
	if request.session.has_key('judge'):
		return render(request,'judge_dashboard.html',{})
	else:
		return render(request,'judge.html',{})
def judge_logout(request):
    try:
        del request.session['judge']
        del request.session['judge_id']
    except:
     pass
    return render(request, 'judge.html', {})
def police_dashboard(request):
	if request.session.has_key('police'):
		if request.method == 'POST':
			if request.POST.get('case') == 'New':
				return render(request,'case_type.html',{})
			elif request.POST.get('case') == 'Existing':
				return render(request,'all_cases.html',{})
		return render(request,'police_dashboard.html',{})
	else:
		return render(request,'police_login.html',{})
def police_logout(request):
    try:
        del request.session['police']
        del request.session['police_id']
    except:
     pass
    return render(request, 'police_login.html', {})
def add_details(request):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		uid = Police_Detail.objects.get(id=int(user_id))
		if request.method == 'POST':
			case_no = request.POST.get('case_no')
			case_type = request.GET.get('case_type')
			victim_name = request.POST.get('victim_name')
			suspect_name = request.POST.get('suspect_name')
			victim_gender = request.POST.get('victim_gender')
			case_date = request.POST.get('case_date')
			case_filed_date = request.POST.get('case_filed_date')
			case_location = request.POST.get('case_location')
			victim_address = request.POST.get('victim_address')
			suspect_address = request.POST.get('suspect_address')
			fir_doc = request.FILES['fir_doc']
			evidance = request.FILES['evidance']
			victim_photo = request.FILES['victim_photo']
			suspect_photo = request.FILES['suspect_photo']
			case_summary = request.POST.get('case_summary')
			crt = Fir_Detail.objects.create(police_id=uid,case_type=case_type,case_no=case_no,victim_name=victim_name,
			suspect_name=suspect_name,victim_gender=victim_gender,case_date=case_date,case_filed_date=case_filed_date,
			case_location=case_location,victim_address=victim_address,suspect_address=suspect_address,fir_doc=fir_doc,
			evidance=evidance,victim_photo=victim_photo,suspect_photo=suspect_photo,case_summary=case_summary,case_status='Unsolved')
			if crt:
				messages.success(request,'Deatils Added Successfully.')
		return render(request,'add_details.html',{})
	else:
		return render(request,'police_login.html',{})
def case_type(request):
	if request.session.has_key('police'):
		return render(request,'case_type.html',{})
	else:
		return render(request,'police_login.html',{})
def all_cases(request):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		ids = Fir_Detail.objects.filter(police_id=int(user_id)).order_by('-case_date')
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a))
				return render(request,'all_cases.html',{'row':ids,'detail':detail})
			else:
				return render(request,'all_cases.html',{'ids':ids})
		return render(request,'all_cases.html',{'ids':ids})
	else:
		return render(request,'police_login.html',{})
def search_date(request):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		from datetime import date
		formatted_date = date.today()
		row = Fir_Detail.objects.filter(case_date=formatted_date)
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(case_date=a)
				return render(request,'search_date.html',{'detail':detail})
			else:
				return render(request,'search_date.html',{'row':row})
		return render(request,'search_date.html',{'row':row})
	else:
		return render(request,'police_login.html',{})
def search_by_law(request):
	if request.session.has_key('lawyer'):
		from datetime import date
		from datetime import datetime
		user_id = request.session['lawyer_id']
		formatted_date = date.today()
		row = Fir_Detail.objects.filter(case_date=formatted_date)
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(case_date=a)
				return render(request,'search_by_law.html',{'detail':detail,'current_date':formatted_date})
			else:
				return render(request,'search_by_law.html',{'current_date':formatted_date,'row':row})
		return render(request,'search_by_law.html',{'current_date':formatted_date,'row':row})
	else:
		return render(request,'police_login.html',{})
def search_by_judge(request):
	if request.session.has_key('judge'):
		from datetime import date
		from datetime import datetime
		user_id = request.session['judge_id']
		formatted_date = date.today()
		row = Fir_Detail.objects.filter(case_date=formatted_date)
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(case_date=a)
				return render(request,'search_judge.html',{'detail':detail,'current_date':formatted_date})
			else:
				return render(request,'search_judge.html',{'current_date':formatted_date,'row':row})
		return render(request,'search_judge.html',{'current_date':formatted_date,'row':row})
	else:
		return render(request,'judge.html',{})
def judgement(request,pk):
	if request.session.has_key('judge'):
		if request.method == 'POST':
			judgement = request.POST.get('judgement')
			case_status = request.POST.get('case_status')
			crt = Fir_Detail.objects.filter(id=pk).update(case_status=case_status,judgement=judgement)
			if crt:
				return redirect('judge_solved')
		return render(request,'judgement.html',{})
	else:
		return render(request,'judge.html',{})
def view_judgement(request,pk):
	if request.session.has_key('judge'):
		row = Fir_Detail.objects.filter(id=pk)
		return render(request,'view_judgement.html',{'row':row})
	else:
		return render(request,'judge.html',{})
def all_detail(request,pk):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		ids = Fir_Detail.objects.filter(id=pk)
		return render(request,'all_detail.html',{'row':ids})
	else:
		return render(request,'police_login.html',{})
def choose_lawyer(request):
	if request.session.has_key('p_id'):
		user_id = request.session['p_id']
		ids = Lawyer_Detail.objects.all()
		return render(request,'choose_lawyer.html',{'row':ids})
	else:
		return render(request,'public_login.html',{})
def choose_lawyer_police(request):
	if request.session.has_key('police_id'):
		user_id = request.session['police_id']
		ids = Lawyer_Detail.objects.all()
		return render(request,'choose_lawyer_police.html',{'row':ids})
	else:
		return render(request,'public_login.html',{})
def send_request(request,pk):
	if request.session.has_key('p_id'):
		user_id = request.session['p_id']
		uid = User_Detail.objects.get(id=int(user_id))
		lawyer_id = Lawyer_Detail.objects.get(id=pk)
		crt = Lawyer_Request.objects.create(user_id=uid,lawyer_id=lawyer_id,status='Pending')
		if crt:
			return redirect('requested_list')
	else:
		return render(request,'public_login.html',{})
def requested_list(request):
	if request.session.has_key('p_id'):
		user_id = request.session['p_id']
		ids = Lawyer_Request.objects.filter(user_id=int(user_id))
		return render(request,'requested_list.html',{'row':ids})
	else:
		return render(request,'public_login.html',{})
def user_case(request):
	if request.session.has_key('lawyer_id'):
		user_id = request.session['lawyer_id']
		ids = Lawyer_Request.objects.filter(lawyer_id=int(user_id))
		detail = Send_Case.objects.filter(lawyer_id=int(user_id))
		return render(request,'user_case.html',{'row':ids,'detail':detail})
	else:
		return render(request,'lawyer_login.html',{})
def accept(request,pk):
	if request.session.has_key('lawyer_id'):
		user_id = request.session['lawyer_id']
		ids = Lawyer_Request.objects.filter(id=pk).update(status="Accepted")
		if ids:
			return redirect('user_case')
	else:
		return render(request,'lawyer_login.html',{})
def reject(request,pk):
	if request.session.has_key('lawyer_id'):
		user_id = request.session['lawyer_id']
		ids = Lawyer_Request.objects.filter(id=pk).update(status="Rejected")
		if ids:
			return redirect('user_case')
	else:
		return render(request,'lawyer_login.html',{})
def accept_police(request,pk):
	if request.session.has_key('lawyer_id'):
		user_id = request.session['lawyer_id']
		ids = Send_Case.objects.filter(id=pk).update(status="Accepted")
		if ids:
			return redirect('user_case')
	else:
		return render(request,'lawyer_login.html',{})
def reject_police(request,pk):
	if request.session.has_key('lawyer_id'):
		user_id = request.session['lawyer_id']
		ids = Send_Case.objects.filter(id=pk).update(status="Rejected")
		if ids:
			return redirect('user_case')
	else:
		return render(request,'lawyer_login.html',{})
def lawyer_doc(request):
	if request.session.has_key('lawyer'):
		user_id = request.session['lawyer_id']
		uid = Lawyer_Detail.objects.get(id=int(user_id))
		if request.method == 'POST':
			case_no = request.POST.get('case_no')
			lawyer_evidance_doc = request.FILES['lawyer_evidance_doc']
			other_doc = request.FILES['other_doc']
			case_summary = request.POST.get('case_summary')
			crt = Lawyer_Evidance.objects.create(lawyer_id=uid,case_no=case_no,lawyer_evidance_doc=lawyer_evidance_doc,
			case_summary=case_summary,other_doc=other_doc)
			if crt:
				messages.success(request,'Deatils Added Successfully.')
		return render(request,'lawyer_doc.html',{})
	else:
		return render(request,'lawyer_login.html',{})
def all_case_detail(request):
	if request.session.has_key('lawyer'):
		user_id = request.session['lawyer_id']
		ids = Fir_Detail.objects.all()
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a))
				return render(request,'all_case_detail.html',{'row':ids,'detail':detail})
			else:
				return render(request,'all_case_detail.html',{'ids':ids})
		return render(request,'all_case_detail.html',{'ids':ids})
	else:
		return render(request,'lawyer_login.html',{})
def unsolved_cases(request):
	if request.session.has_key('lawyer'):
		user_id = request.session['lawyer_id']
		ids = Fir_Detail.objects.filter(case_status='Unsolved')
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a),case_status='Unsolved')
				return render(request,'unsolved_cases.html',{'row':ids,'detail':detail})
			else:
				return render(request,'unsolved_cases.html',{'ids':ids})
		return render(request,'unsolved_cases.html',{'ids':ids})
	else:
		return render(request,'lawyer_login.html',{})
def solved_cases(request):
	if request.session.has_key('lawyer'):
		user_id = request.session['lawyer_id']
		ids = Fir_Detail.objects.filter(case_status='Solved')
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a),case_status='Solved')
				return render(request,'solved_cases.html',{'row':ids,'detail':detail})
			else:
				return render(request,'solved_cases.html',{'ids':ids})
		return render(request,'solved_cases.html',{'ids':ids})
	else:
		return render(request,'lawyer_login.html',{})
def judge_solved(request):
	if request.session.has_key('judge'):
		user_id = request.session['judge_id']
		ids = Fir_Detail.objects.filter(case_status='Solved')
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a),case_status='Solved')
				return render(request,'judge_solved.html',{'row':ids,'detail':detail})
			else:
				return render(request,'judge_solved.html',{'ids':ids})
		return render(request,'judge_solved.html',{'ids':ids})
	else:
		return render(request,'judge.html',{})
def judge_unsolved(request):
	if request.session.has_key('judge'):
		user_id = request.session['judge_id']
		ids = Fir_Detail.objects.filter(case_status='Unsolved')
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a),case_status='Unsolved')
				return render(request,'judge_unsolved.html',{'row':ids,'detail':detail})
			else:
				return render(request,'judge_unsolved.html',{'ids':ids})
		return render(request,'judge_unsolved.html',{'ids':ids})
	else:
		return render(request,'judge.html',{})
def case_list(request,pk):
	if request.session.has_key('lawyer'):
		user_id = request.session['lawyer_id']
		ids = Fir_Detail.objects.filter(id=pk)
		cas_id = Fir_Detail.objects.get(id=pk)
		detail = More_Evidance.objects.filter(case_id=pk)
		case_no = cas_id.case_no
		b = Lawyer_Evidance.objects.filter(case_no=case_no)
		return render(request,'case_list.html',{'row':ids,'b':b,'detail':detail})
	else:
		return render(request,'lawyer_login.html',{})
def all_case_list_detail(request):
	if request.session.has_key('judge'):
		user_id = request.session['judge_id']
		ids = Fir_Detail.objects.all()
		if request.method == 'GET':
			if request.GET.get('search'):
				a = request.GET.get('search')
				detail = Fir_Detail.objects.filter(Q(case_no=a) | Q(case_type__icontains=a))
				return render(request,'all_case_list_detail.html',{'row':ids,'detail':detail})
			else:
				return render(request,'all_case_list_detail.html',{'ids':ids})
		return render(request,'all_case_list_detail.html',{'ids':ids})
	else:
		return render(request,'judge.html',{})
def case_list_judge(request,pk):
	if request.session.has_key('judge'):
		user_id = request.session['judge_id']
		ids = Fir_Detail.objects.filter(id=pk)
		cas_id = Fir_Detail.objects.get(id=pk)
		case_no = cas_id.case_no
		b = Lawyer_Evidance.objects.filter(case_no=case_no)
		detail = More_Evidance.objects.filter(case_id=pk)
		return render(request,'case_list_judge.html',{'row':ids,'b':b,'detail':detail})
	else:
		return render(request,'judge.html',{})

def more_evidance(request):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		current_date = date.today()
		ids = More_Evidance.objects.filter(police_id=int(user_id)).order_by('-date')
		deatil = Fir_Detail.objects.filter(police_id=int(user_id))
		if request.method == 'POST':
			case_id = request.POST.get('case_id')
			cid = Fir_Detail.objects.get(id=int(case_id))
			uid = Police_Detail.objects.get(id=int(user_id))
			more_evidance_doc = request.FILES['more_evidance_doc']
			crt = More_Evidance.objects.create(police_id=uid,case_id=cid,more_evidance_doc=more_evidance_doc,date=current_date)
			if crt:
				messages.success(request,'Added Successfully..')

		return render(request,'more_evidance.html',{'row':ids,'deatil':deatil})
	else:
		return render(request,'police_login.html',{})
def send_lawyer(request,pk):
	if request.session.has_key('police'):
		user_id = request.session['police_id']
		current_date = date.today()
		deatil = Fir_Detail.objects.filter(police_id=int(user_id))
		row = Send_Case.objects.filter(police_id=int(user_id)).order_by('-date')
		if request.method == 'POST':
			case_id = request.POST.get('case_id')
			cid = Fir_Detail.objects.get(id=int(case_id))
			uid = Police_Detail.objects.get(id=int(user_id))
			lawyer_id  = Lawyer_Detail.objects.get(id=pk)
			crt = Send_Case.objects.create(police_id=uid,case_id=cid,lawyer_id=lawyer_id,date=current_date,status='Pending')
			if crt:
				messages.success(request,'Sent to Lawyer Successfully..')

		return render(request,'send_lawyer.html',{'deatil':deatil,'row':row})
	else:
		return render(request,'police_login.html',{})