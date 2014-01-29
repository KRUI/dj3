from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.urlresolvers import reverse
from dj3.models import UserProfile, Track, Program, Spot, Contact, SubRequest
from datetime import datetime, timedelta
from string import split

### Login/Authentication Views

# Displays the login form
def login_form(request):
	return render(request, 'dj3/login.html')

def process_login(request):
	# Retrieve user/pass submission via POST
	user_input = request.POST['username']
	password_input = request.POST['password']
	
	# If username/password are blank, display an error message
	if not (user_input or password_input):
		error_message = "You must enter both a username and a password."
		return HttpResponse(error_message)

	else:
		# Attempt to authenticate with these credentials
		user = authenticate(username=user_input, password=password_input)

		# If we were given valid creds, log the user into the Django auth framework
		if user is not None:
			login(request, user)
			
			# Redirect to the main site (playlist for now)
			return redirect('/dj3/playlist')
		
		else:
			# Throw an invalid login error
			error_message = "Invalid login credentials"
			return HttpResponse(error_message)

def logout_user(request):
	logout(request)				# Recursion depth exceeded... it's getting late
	return redirect('/dj3/')

### User Profile Views
def edit_user_profile(request):
	# Check if this is being accessed directly after registration.
	process = request.GET.get('process', False)
	new_user_check = request.GET['new_user']
	error = False

	## Processing if GET 'process' is set
	if (process):
		# Check "student" fields
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		phone = request.POST['phone']
		student_id = request.POST['student_id']
		university_status = request.POST['university_status']
		no_id_checkbox = request.POST.get('no_id_checkbox', False)		

		if not(first_name or last_name or email or phone or student_id):
			error = True
			error_message = "You must fill out all required fields."

		# Ensure university status is set (default select value is -1)
		if (not error) and (int(university_status) == -1):
			error = True
			error_message = "You must select an university status (student or non-student)."

		# Ensure phone number field consists of only numbers
		if (not error) and not (phone.isdigit()):
			error = True
			error_message = "Phone number field can only contain digits (no dashes or parentheses)."
		
		# Ensure student ID number consists of only numbers
		if (not error) and not (student_id.isdigit()):
			error = True
			error_message = "Student ID field can only contain digits."

		# If no student ID is passed, OR the user's status is changed to non-student, we must validate the local address portion of the submission
		if (not error) and (no_id_checkbox or int(university_status) == UserProfile.NON_STUDENT):
			## Validate local address (ensure all fields are filled)
			address_1 = request.POST['address_line_1']
			address_2 = request.POST['address_line_2']
			city = request.POST['city']
			state = request.POST['state']
			zipcode = request.POST['zipcode']

			if (not error) and not(address_1 or city or state or zipcode):
				error = True
				error_message = "Since you did not provide a Student ID (or designated yourself as a non-student), you must provide a local address. The only optional field is the second address line."

			if (not error) and (state.__len__() != 2):
				error = True
				error_message = "State must be abbreviated (ex: IA for Iowa)."

		if (not error):
		# After validation, make the requested changes to the logged in user/profile.
			user = request.user
			user_profile = user.get_profile()
			user.first_name = first_name
			user.last_name = last_name
			user.email = email
			user_profile.university_status = university_status
			user_profile.student_id = student_id
			user_profile.phone = phone
			user_profile.save()
			user.save()
			success_message = "Your profile changes have been saved."
			# Render the template with a confirmation that changes were saved
			return render(request, 'dj3/edit_user_profile.html', {'new_user': new_user_check, 'university_status_list': UserProfile.UNIVERSITY_STATUS_CHOICES, 'success_message': success_message })
		else:

			# Render the template with the error_message displayed.
			return render(request, 'dj3/edit_user_profile.html', {'new_user': new_user_check, 'university_status_list': UserProfile.UNIVERSITY_STATUS_CHOICES, 'error_message': error_message})
	
	else:
		# If we aren't processing, just display the template as normal
		return render(request, 'dj3/edit_user_profile.html', {'new_user': new_user_check, 'university_status_list': UserProfile.UNIVERSITY_STATUS_CHOICES})

### Playlist & Song Logging Views

# Basic playlist display view
@login_required
def playlist(request):
	# Get the user's last ten played tracks if they exist
	profile = request.user.get_profile()
	track_list = Track.objects.filter(user_profile=profile).order_by('-id')[:10]
	
	return render(request, 'dj3/playlist.html', {'track_list': track_list, 'profile': profile})

# Processes a new song log entry
def process_track(request):
	# Retrieve passed track information 
	name_input = request.POST['track']
	artist_input = request.POST['artist']
	album_input = request.POST['album']

	# Check if all three input values were filled in
	if not (name_input and artist_input and album_input):
		# Display an error message on previous page
		return render(request, 'dj3/playlist.html', {'error_message': "You must provide a song name, artist name, and album name before logging a song."})
		
	else:
		# Get the profile of the current user
		profile = request.user.get_profile()

		# Create a new Track and write it to the database
		t = Track(name=name_input, artist=artist_input, album=album_input, comment="implement comments!", rotation=2, user_profile=profile)
		t.save()

		# Direct us back to the playlist
		return HttpResponseRedirect(reverse('dj3:playlist'))

def process_spot(request, spot_id):
	# If spot_id is non-existent or not in the field of allowed values, throw an error.
	if (spot_id > 3 and spot_id < 0):
		return HttpResponse("Spot ID is invalid.")
	
	# Retrieve user profile
	profile = request.user.get_profile()

	# Create a new spot 
	s = Spot(user_profile=profile, time_played=timezone.now(), spot_type=spot_id)
	s.save()
	
	# Redirect to playlist view
	return HttpResponseRedirect(reverse('dj3:playlist'))

def process_sub_request(request):
	# Category is in URL as a GET variable
	category_int = request.GET["cat"]

	## Retrieve the other information via POST
	user_email = request.POST["email"]
	start_time = request.POST["start_time"]
	end_time = request.POST["end_time"]
	absent_date = request.POST["absent_date"]
	
	# Split absent_date on "-" to get month, day, and year, do the same for start_time,  then build a datetime object with both absent_date and start_time for comparison
	split_list = split(s=absent_date, sep="-")
	m = split_list[0]
	d = split_list[1]
	y = split_list[2]
	split_time = split(s=start_time, sep=":")
	h = split_time[0]
	mi = split_time[1]
	s = split_time[2]

	# absent_datetime is now the date & time of the show that will be missed
	absent_datetime = datetime(month=int(m), day=int(d), year=int(y), hour=int(h), minute=int(mi), second=int(s))

	# Retrieve Program object
	user_profile = request.user.get_profile()
	user_program = user_profile.program
	
	# Determine if this is considered a /late/ sub request. 
	# FIXME: Hardcoded to assume all sub requests issued less than 24 hours before the show's starting time as late. Must add a pref to change this if necessary
	request_is_late = False
	current_time = timezone.now().replace(tzinfo=None)
	if (current_time > absent_datetime):
		request_is_late = True
		
	# Create the sub request
	sub_request = SubRequest(created_by=user_profile, show=user_program, start_time=start_time, end_time=end_time, is_late=request_is_late)	
	sub_request.save()
	return HttpResponse("Sub Request is late? " + str(request_is_late))

# Shows a dynamically generated director contact info page, based on the information in the UserProfiles assigned to Director roles
def show_contact_info(request):

	# Get the list of all Contact objects and pass to the template
	contact_list = Contact.objects.all()
	return render(request, 'dj3/director_contact.html', {'contact_list': contact_list})

## Form SubmissionViews
def new_sub_request(request):
	# Get the profile and active show for this user (if available) and pass as contexts to auto-fill the form
	profile = request.user.get_profile()
	active_show = profile.program
	
	# Get the integer constant representing the program category. then use it to index the tuple stored in models.Program to get a user friendly text representation of the program format.
	category_int = active_show.category

	# Slice twice to remove ID from output - format: (id, 'textual description) [see models.Program for more info]
	category_txt = Program.CATEGORY_CHOICES[category_int][1]
	return render(request, 'dj3/new_sub_request.html', {'profile': profile, 'program': active_show, 'category_text': category_txt })

## Management Views
@login_required
def management_panel(request):
	return render(request, 'dj3/m_panel.html')

@login_required
def manage_programming(request):
	return render(request, 'dj3/m_programming.html')

@login_required
def manage_users(request):
	return render(request, 'dj3/m_users.html')
