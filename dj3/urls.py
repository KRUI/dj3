from django.conf.urls import patterns, url
from dj3 import views

urlpatterns = patterns('',
	# Login/Authentication URLs
	url(r'^$', views.login_form, name='login'),
	url(r'^process_login/$', views.process_login, name='process_login'),
	url(r'^logout/$', views.logout_user, name='logout'),
	
	# Management URLs
	url(r'^manage/$', views.management_panel, name='manage'),
	url(r'^manage/users/$', views.manage_users, name='m_users'),
	url(r'^manage/programming/$', views.manage_programming, name='m_programming'),

	# Playlist URLs
	url(r'^playlist/$', views.playlist, name='playlist'),
	url(r'^playlist/process_track/$', views.process_track, name='process_track'),
	url(r'^playlist/process_spot/(?P<spot_id>\d+)/$', views.process_spot, name='process_spot'),
	
	# Forms & Form Processing
	url(r'^forms/sub_request/$', views.new_sub_request, name='new_sub_request'),
	url(r'^forms/sub_request/process_sub_request/$', views.process_sub_request, name='process_sub_request'),

	# Contact
	url(r'^contact/$', views.show_contact_info, name='director_contact'),
)
