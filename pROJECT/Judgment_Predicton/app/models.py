from django.conf import settings
from django.db import models
from django.utils import timezone
UTYPE = (
	('','Select'),
    ('Victim','Victim'),
    ('Suspect', 'Suspect'),)
UserTYPE = (
	('','Select'),
    ('Police','Police'),
    ('Lawyer', 'Lawyer'),('Judge', 'Judge'),)
class User_Detail(models.Model):
	username = models.CharField(max_length=30,unique=True)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	password = models.CharField(max_length=40)
	mail = models.EmailField(max_length=30)
	mobile = models.CharField(max_length=15)
	country = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	city = models.CharField(max_length=30)
	address =  models.TextField(max_length=200)
	def __str__(self):
		return self.username

class Police_Detail(models.Model):
	police_name = models.CharField(max_length=100)
	username = models.CharField(max_length=80,unique=True)
	password = models.CharField(max_length=40)
	mail = models.EmailField(max_length=30)
	mobile = models.CharField(max_length=15)
	designation = models.CharField(max_length=100)
	station_name = models.CharField(max_length=200)
	country = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	city = models.CharField(max_length=30)
	address =  models.TextField(max_length=200)
	image = models.FileField('Upload Image',upload_to='documents/',null=True)
	def __str__(self):
		return self.police_name
class Lawyer_Detail(models.Model):
	lawyer_name = models.CharField(max_length=100)
	username = models.CharField(max_length=80,unique=True)
	password = models.CharField(max_length=40)
	mail = models.EmailField(max_length=30)
	mobile = models.CharField(max_length=15)
	qualification = models.CharField(max_length=100)
	experience = models.CharField(max_length=200)
	specialization = models.CharField(max_length=200)
	country = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	city = models.CharField(max_length=30)
	address =  models.TextField(max_length=200)
	image = models.FileField('Upload Image',upload_to='documents/',null=True)
	def __str__(self):
		return self.lawyer_name
class Judge_Detail(models.Model):
	judge_name = models.CharField(max_length=100)
	username = models.CharField(max_length=80,unique=True)
	password = models.CharField(max_length=40)
	mail = models.EmailField(max_length=30)
	mobile = models.CharField(max_length=15)
	qualification = models.CharField(max_length=100)
	experience = models.CharField(max_length=200)
	specialization = models.CharField(max_length=200)
	country = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	city = models.CharField(max_length=30)
	address =  models.TextField(max_length=200)
	image = models.FileField('Upload Image',upload_to='documents/',null=True)
	def __str__(self):
		return self.judge_name
class Fir_Detail(models.Model):
	police_id = models.ForeignKey(Police_Detail, on_delete=models.CASCADE,null=True)
	case_no = models.CharField(max_length=100,null=True)
	case_type = models.CharField(max_length=100,null=True)
	victim_name = models.CharField(max_length=100)
	suspect_name = models.CharField(max_length=15)
	victim_gender = models.CharField(max_length=100)
	case_date = models.DateField()
	case_filed_date = models.DateField()
	case_location = models.CharField(max_length=100)
	victim_address =  models.TextField(max_length=1000)
	suspect_address =  models.TextField(max_length=1000)
	fir_doc = models.FileField('FIR Document ',upload_to='documents/',null=True)
	evidance = models.FileField('Evidance Document',upload_to='documents/',null=True)
	victim_photo = models.FileField('Victim Photo ',upload_to='documents/',null=True)
	suspect_photo = models.FileField('Suspect Photo ',upload_to='documents/',null=True)
	case_summary =  models.TextField(max_length=1000)
	case_status = models.CharField(max_length=100,null=True,blank=True)
	judgement = models.TextField(max_length=1000,null=True,blank=True)
	def __str__(self):
		return self.case_no
class Lawyer_Request(models.Model):
	lawyer_id = models.ForeignKey(Lawyer_Detail, on_delete=models.CASCADE)
	user_id = models.ForeignKey(User_Detail, on_delete=models.CASCADE)
	status = models.CharField(max_length=100)
	def __str__(self):
		return self.user_id.username
class Lawyer_Evidance(models.Model):
	lawyer_id = models.ForeignKey(Lawyer_Detail, on_delete=models.CASCADE)
	case_no = models.CharField(max_length=100)
	lawyer_evidance_doc = models.FileField('Evidance Document ',upload_to='documents/')
	other_doc = models.FileField('Other Document ',upload_to='documents/')
	case_summary = models.TextField(max_length=2000)
	def __str__(self):
		return self.case_no
class More_Evidance(models.Model):
	police_id = models.ForeignKey(Police_Detail, on_delete=models.CASCADE,null=True,blank=True)
	case_id = models.ForeignKey(Fir_Detail, on_delete=models.CASCADE)
	more_evidance_doc = models.FileField('Evidance Document ',upload_to='documents/')
	date = models.DateField(null=True,blank=True)
	def __str__(self):
		return self.case_id.case_no
class Send_Case(models.Model):
	lawyer_id = models.ForeignKey(Lawyer_Detail, on_delete=models.CASCADE)
	police_id = models.ForeignKey(Police_Detail, on_delete=models.CASCADE)
	case_id = models.ForeignKey(Fir_Detail, on_delete=models.CASCADE)
	date = models.DateField(null=True,blank=True)
	status = models.CharField(max_length=100,null=True,blank=True)
	def __str__(self):
		return self.police_id.username