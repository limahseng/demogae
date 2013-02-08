#!/usr/bin/env python

import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
import datetime # format date time
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
from google.appengine.api import mail	# send email

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def format_datetime(value):
    return value.strftime("%d-%m-%Y %H:%M")

jinja_environment.filters['datetime'] = format_datetime

class Person(db.Expando):
	''' User profile '''
	pid = db.StringProperty(required=True)
	name = db.StringProperty(required=True)		
	email = db.EmailProperty(required=True)
	remark = db.TextProperty()
	updated = db.DateTimeProperty(auto_now=True)
	
		
class MainHandler(webapp2.RequestHandler):
	''' Home page '''
	def get(self):
		user = users.get_current_user()

		if user:
			query = Person.all().filter("email =", user.email())
			#query = Person.gql("WHERE email = :1", user.email())
			result = query.fetch(1)
			if result: # record exists
				person = result[0]
				greeting = ("%s" % (person.name,))
			else: # not found
				person = False
				greeting = "Oops"
			url = users.create_logout_url(self.request.uri)
			url_linktext = "logout"
		else: # not logged in
			person = ""
			greeting = ""
			url = users.create_login_url(self.request.uri)
			url_linktext = "login"
			
		template_values = {
			'person': person,
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
		}

		if user:
			template = jinja_environment.get_template('index.html')
		else:
			template = jinja_environment.get_template('404.html')
		self.response.out.write(template.render(template_values))

		
class UpdateHandler(webapp2.RequestHandler):
	''' Update profile '''
	def post(self):
		if self.request.get('update'): # update profile
			updated_remark = self.request.get('remark')
			current_user = users.get_current_user()
			query = Person.gql('WHERE email = :1', current_user.email())
			result = query.fetch(1)
			if result:
				student = result[0]
				student.remark = db.Text(updated_remark)
				student.put()
			else:
				self.response.write("Cannot update!")
		# go back to home page
		self.redirect('/')


# main
#p1 = Person(pid=users.get_current_user().nickname(), name="LIM AH SENG", email=users.get_current_user().email(), remark="cute little boy")
#p1.put()

app = webapp2.WSGIApplication([('/', MainHandler), ('/update', UpdateHandler)], debug=True)
