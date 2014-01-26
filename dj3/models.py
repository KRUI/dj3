from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime

# A scheduled on-air event is a Program
class Program(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500)
	link = models.CharField(max_length=100)
	created = models.DateTimeField('created')
	start_time = models.TimeField()
	end_time = models.TimeField()

	# Day Of Week Tag
	SUNDAY = 0
	MONDAY = 1
	TUESDAY = 2
	WEDNESDAY = 3
	THURSDAY = 4
	FRIDAY = 5
	SATURDAY = 6
	WEEKDAY_CHOICES = (
		(SUNDAY, 'Sunday'),
		(MONDAY, 'Monday'),
		(TUESDAY, 'Tuesday'),
		(WEDNESDAY, 'Wednesday'),
		(THURSDAY, 'Thursday'),
		(FRIDAY, 'Friday'),
		(SATURDAY, 'Saturday'),
	)
	day_of_week = models.IntegerField(max_length=1, choices=WEEKDAY_CHOICES)

	# Program Category Tags
	REGULAR_ROTATION = 0
	MUSIC_SPECIALITY = 1
	NEWS_TALK = 2
	SPORTS = 3
	CATEGORY_CHOICES = (
		(REGULAR_ROTATION, 'Regular Rotation'),
		(MUSIC_SPECIALITY, 'Music Speciality'),
		(NEWS_TALK, 'News/Talk'),
		(SPORTS, 'Sports'),
	)
	category = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES, default=REGULAR_ROTATION)

	def __unicode__(self):
		return self.name

	def start_time_raw(self):
		return self.start_time.strftime("%H:%M:%S")
	
	def end_time_raw(self):
		return self.end_time.strftime("%H:%M:%S")

# UserProfile is an object used to store non-authentication related data, such as permissions, roles, show information, etc
class UserProfile(models.Model):
	# Every UserProfile must reference a Django User object used for authentication
	user = models.OneToOneField(User)

	# Basic bookkeeping information
	student_id = models.CharField(max_length=12, default="", null=True)
	phone = models.CharField(max_length=10, default="", null=True)
	avatar = models.CharField(max_length=150, blank=True, null=True)
	created = models.DateTimeField('account created', default=timezone.now())

	# Keep a reference to a user's on-air program if they have one
	program = models.ForeignKey(Program, blank=True, null=True)
	
	# Academic Status Tags
	FRESHMAN = 0
	SOPHOMORE = 1
	JUNIOR = 2
	SENIOR = 3
	OTHER = 4
	NON_STUDENT = 5
	ACADEMIC_STATUS_CHOICES = (
		(FRESHMAN, 'Freshman'),
		(SOPHOMORE, 'Sophomore'),
		(JUNIOR, 'Junior'),
		(SENIOR, 'Senior'),
		(OTHER, 'Other'),
		(NON_STUDENT, 'Non-student'),
	)
	academic_status = models.IntegerField(max_length=1, choices=ACADEMIC_STATUS_CHOICES, default=FRESHMAN, null=True)
	
	# KRUI Director Roles (Non-directors should be set to NULL!)
	GENERAL_MANAGER = 1
	PROGRAM_DIRECTOR_897 = 2
	PROGRAM_DIRECTOR_LAB = 3
	TECHNOLOGY_DIRECTOR = 4
	OPERATIONS_DIRECTOR = 5
	ADMIN_DIRECTOR = 6
	MARKETING_DIRECTOR = 7
	MUSIC_DIRECTOR = 8
	PRODUCTION_DIRECTOR = 9
	NEWS_DIRECTOR = 10
	SPORTS_DIRECTOR = 11
	EDITOR_IN_CHIEF = 12
	UNDERWRITING_DIRECTOR = 13
	ROLE_CHOICES = (
		(GENERAL_MANAGER, 'General Manager'),
		(PROGRAM_DIRECTOR_897, 'Program Director (89.7)'),
		(PROGRAM_DIRECTOR_LAB, 'Program Director (Lab)'),
		(TECHNOLOGY_DIRECTOR, 'Technology Director'),
		(OPERATIONS_DIRECTOR, 'Operations Director'),
		(ADMIN_DIRECTOR, 'Administrative Director'),
		(MARKETING_DIRECTOR, 'Marketing Director'),
		(MUSIC_DIRECTOR, 'Music Director'),
		(PRODUCTION_DIRECTOR, 'Production Director'),
		(NEWS_DIRECTOR, 'News Director'),
		(SPORTS_DIRECTOR, 'Sports Director'),
		(EDITOR_IN_CHIEF, 'Editor-In-Chief'),
		(UNDERWRITING_DIRECTOR, 'Underwriting Director'),
		)
	
	role = models.IntegerField(max_length=2, choices=ROLE_CHOICES, null=True, blank=True)
	
	# On creation of a User, create a UserProfile
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			UserProfile.objects.create(user=instance)
	post_save.connect(create_user_profile, sender=User)

	def __unicode__(self):
		return str(self.user.get_username())

	def formatted_phone(self):
		formatted = "(" + self.phone[0:3] + ") " + self.phone[3:6] + "-" + self.phone[6:10]
		return formatted

# Represents a 'play' in the song log
class Track(models.Model):
	name = models.CharField(max_length=100)
	artist = models.CharField(max_length=100)
	album = models.CharField(max_length=100)
	comment = models.CharField(max_length=125)
	user_profile = models.ForeignKey(UserProfile)

	RED = 0
	ORANGE_YELLOW = 1
	GREEN = 2
	BLUE = 3
	ROTATION_CHOICES = (
		(RED, 'Red'),
		(ORANGE_YELLOW, 'Orange/Yellow'),
		(GREEN, 'Green'),
		(BLUE, 'Blue'),
	)
	rotation = models.IntegerField(max_length=1, choices=ROTATION_CHOICES, default=GREEN)
	
	def __unicode__(self):
		return self.artist + " - " + self.name

# All Contacts that are displayed in dj3:contact are Contact objects
class Contact(models.Model):
	user_profile = models.ForeignKey(UserProfile)
	title = models.CharField(max_length=75)
	description = models.CharField(max_length=1000)
	on_call = models.BooleanField(default=False)	
	
	def __unicode__(self):
		return self.title

# Required spots are recorded using this model
class Spot(models.Model):
	user_profile = models.ForeignKey(UserProfile)
	time_played = models.DateTimeField('time played')
	# Spot categorization tags
	LEGAL_ID = 0
	PSA = 1
	WEATHER = 2
	GRANT_SPOT = 3
	SPOT_CHOICES = (
	(LEGAL_ID, 'Legal ID'),
	(PSA, 'PSA'),
	(WEATHER, 'Weather'),
	(GRANT_SPOT, 'Grant Spot'),
	)
	spot_type = models.IntegerField(max_length=1, choices=SPOT_CHOICES)

class SubRequest(models.Model):
	created_by = models.ForeignKey(UserProfile)
	show = models.ForeignKey(Program)
	start_time = models.TimeField('start_time')
	end_time = models.TimeField('end_time')
	is_late = models.BooleanField(default=False)
