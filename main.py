'''-----------------------------------------------------------------------
Project Friendlytics
CSE 791 : Social Media Mining
Authors: Anil Pai & Sundar Lakshmanan, v 1.0, Dec 15, 2013
--------------------------------------------------------------------------
Import various standard modules.
We don't use all of these modules for this project,
but they can be handy later.
'''

# First the standard python modules
import webapp2
import facebook
import json
import urllib2
import cgi,os,logging, email, datetime, string, types, re, sys, traceback
from datetime import date


# Now the Google App Engine modules
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required


'''-------------------------------------------------------------------
# Our core code BEGINS
#---------------------------------------------------------------------

#---------------------------------------------------------------------
Here is the welcome web page stored as a string
'''

welcome = """
<html>
<body>
<h2>Welcome to Friendlytics!!!!</h2>
<br>
You have reached the Welcome Page of Friendlytics. What can you do now ?
<br><br>
You can call these REST API web services using the following commands.
<br><br>
1. Top 10 friends with most mutual friends.
<br><br>
friendlytics.appspot.com/ws1?at=[fb_access_token]
<br><br>
2. Top 20 friends with most friends.
<br><br>
friendlytics.appspot.com/ws2?at=[fb_access_token]
<br><br>
3. Top 25 friends with most followers.
<br><br>
friendlytics.appspot.com/ws3?at=[fb_access_token]
<br><br>
4. Age Distribution of Friends.
<br><br>
friendlytics.appspot.com/ws4?at=[fb_access_token]
<br><br>
5. Friends Relationship Status.
<br><br>
friendlytics.appspot.com/ws5?at=[fb_access_token]
<br><br>
6. Top 10 locations my friends are located.
<br><br>
friendlytics.appspot.com/ws6?at=[fb_access_token]
<br><br>
7. Top 10 languages my friends speak.
<br><br>
friendlytics.appspot.com/ws7?at=[fb_access_token]
<br><br>

</body>
</html>
"""

'''---------------------------------------------------------------------
Main page. Send back the welcome handler
------------------------------------------------------------------------
'''


class MainPage(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'text/html'
                self.response.out.write(welcome)


class TopMutual(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                g = facebook.GraphAPI(fb_token)
                print '-------------------'
                print 'Top 10 friends with most mutual friends'
                print '-------------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20name,%20mutual_friend_count%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())%20ORDER%20BY%20mutual_friend_count%20DESC%20LIMIT%2010&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                friend_names =[]
                mutual_friends = []
                json_out = {}
                for i in output_data['data']:
                    friend_names.append(i['name'])
                    mutual_friends.append(i['mutual_friend_count'])
                json_out['mutual'] = mutual_friends
                json_out['names'] = friend_names
                self.response.out.write(json.dumps(json_out, indent=1))


class TopFriends(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '---------------'
                print 'Top 20 friends with most friends'
                print '---------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20name,%20friend_count%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())%20ORDER%20BY%20friend_count%20DESC%20LIMIT%2020&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                friend_names =[]
                friends = []
                json_out = {}
                for i in output_data['data']:
                    friend_names.append(i['name'])
                    friends.append(i['friend_count'])
                json_out['friend'] = friends
                json_out['names'] = friend_names
                self.response.out.write(json.dumps(json_out, indent=1))


class TopFollow(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '---------------'
                print 'Top 25 friends with most followers'
                print '---------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20name,subscriber_count%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())%20ORDER%20BY%20subscriber_count%20DESC%20LIMIT%2025&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                friend_names =[]
                friends = []
                json_out = {}
                for i in output_data['data']:
                    if i['subscriber_count'] > 10000:
                        continue
                    friend_names.append(i['name'])
                    friends.append(i['subscriber_count'])
                json_out['friend'] = friends
                json_out['names'] = friend_names
                self.response.out.write(json.dumps(json_out, indent=1))


class AgeDistro(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '-------------------'
                print 'Age Distribution of Friends'
                print '-------------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20birthday_date%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                mutual_friends = []
                final_output = {}
                json_out = {}
                for i in output_data['data']:
                    if i['birthday_date'] is not None:
                        current_year = date.today().year
                        if (i['birthday_date'][6:10]) != '':
                            age = current_year - int(i['birthday_date'][6:10])
                            mutual_friends.append(age)

                for j in mutual_friends:
                        if j in final_output:
                            final_output[j] = final_output[j] + 1
                        else:
                            final_output[j] = 1

                count = {}
                count['0-10'] = 0
                count['10-20'] = 0
                count['20-30'] = 0
                count['30-40'] = 0
                count['40-50'] = 0
                count['50-60'] = 0
                count['60-70'] = 0
                count['70-80'] = 0
                count['80-90'] = 0
                count['90-100'] = 0
                count['>100'] = 0

                for key in final_output:
                    if int(key) > 0 and int(key) <= 10:
                        count['0-10'] = count['0-10'] + int(final_output[key])
                    elif int(key) > 10 and int(key) <= 20:
                        count['10-20'] = count['10-20'] + int(final_output[key])
                    elif int(key) > 20 and int(key) <= 30:
                        count['20-30'] = count['20-30'] + int(final_output[key])
                    elif int(key) > 30 and int(key) <= 40:
                        count['30-40'] = count['30-40'] + int(final_output[key])
                    elif int(key) > 40 and int(key) <= 50:
                        count['40-50'] = count['40-50'] + int(final_output[key])
                    elif int(key) > 50 and int(key) <= 60:
                        count['50-60'] = count['50-60'] + int(final_output[key])
                    elif int(key) > 60 and int(key) <= 70:
                        count['60-70'] = count['60-70'] + int(final_output[key])
                    elif int(key) > 70 and int(key) <= 80:
                        count['70-80'] = count['70-80'] + int(final_output[key])
                    elif int(key) > 80 and int(key) <= 90:
                        count['80-90'] = count['80-90'] + int(final_output[key])
                    elif int(key) > 90 and int(key) <= 100:
                        count['90-100'] = count['90-100'] + int(final_output[key])
                    else:
                        count['>100'] = count['>100'] + int(final_output[key])

                ot = {}
                ot = sorted(count, key=count.get, reverse=True)

                ot1 = {}
                relation_status = []
                count1 = []
                for k in ot:
                    relation_status.append(k)
                    count1.append(count[k])

                json_out['age_range'] = relation_status
                json_out['a_count'] = count1
                self.response.out.write(json.dumps(json_out, indent=1))


class RelationStatus(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '-------------------'
                print 'Friends Relationship Status'
                print '-------------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20relationship_status%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                mutual_friends = []
                final_output = {}
                json_out = {}
                for i in output_data['data']:
                    mutual_friends.append(i['relationship_status'])

                for j in mutual_friends:
                    if j is not None:
                        if j in final_output:
                            final_output[j] = final_output[j] + 1
                        else:
                            final_output[j] = 1

                ot = {}
                ot = sorted(final_output, key=final_output.get, reverse=True)

                ot1 = {}
                relation_status = []
                count = []
                for k in ot:
                    relation_status.append(k)
                    count.append(final_output[k])

                json_out['relation_status'] = relation_status
                json_out['relation_status_count'] = count

                self.response.out.write(json.dumps(json_out, indent=1))


class TopLocation(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '-------------------'
                print 'Top 10 locations my friends are located'
                print '-------------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20current_location%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                mutual_friends = []
                output = {}
                json_out = {}
                for i in output_data['data']:
                    if i['current_location'] is not None:
                        mutual_friends.append((i['current_location'])['name'])

                for j in mutual_friends:
                    if j != "null":
                        if j in output:
                            output[j] = output[j] + 1
                        else:
                            output[j] = 1
                ot = {}
                ot = sorted(output, key=output.get, reverse=True)
                ot = ot[0:10]

                ot1 = {}
                location = []
                count = []
                for k in ot:
                    location.append(k)
                    count.append(output[k])

                json_out['location'] = location
                json_out['l_count'] = count
                self.response.out.write(json.dumps(json_out, indent=1))


class TopLanguage(webapp2.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'application/json'
                self.response.headers.add_header("Access-Control-Allow-Origin", "*")
                fb_token = self.request.GET.get('at', '')
                print '-------------------'
                print 'Top 10 languages my friends speak'
                print '-------------------'
                url = "https://graph.facebook.com/fql?q=SELECT%20languages%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid1%20FROM%20friend%20WHERE%20uid2%20=%20me())&access_token="+fb_token
                resp = urllib2.urlopen(url)
                output_data = json.load(resp)
                mutual_friends = []
                output = {}
                json_out = {}
                for i in output_data['data']:
                    if i['languages'] is not None:
                        for a in i['languages']:
                            mutual_friends.append(a['name'])

                for j in mutual_friends:
                    if j != "null":
                        if j in output:
                            output[j] = output[j] + 1
                        else:
                            output[j] = 1
                ot = {}
                ot = sorted(output, key=output.get, reverse=True)
                ot = ot[0:10]

                ot1 = {}
                languages = []
                count = []
                for k in ot:
                    languages.append(k)
                    count.append(output[k])

                json_out['languages'] = languages
                json_out['languages_count'] = count
                self.response.out.write(json.dumps(json_out, indent=1))



'''---------------------------------------------------------------------
# Our core code ENDS
#-----------------------------------------------------------------------
# What follows is typical framework code.
#-----------------------------------------------------------------------
# This is like a web server. It routes the various
# requests to the right handlers. Each time we define
# a new handler, we need to add it to the list here.
'''

app = webapp2.WSGIApplication(
                [
                 (r'/', MainPage),
                 (r'/ws1', TopMutual),
                 (r'/ws2', TopFriends),
                 (r'/ws3', TopFollow),
                 (r'/ws4', AgeDistro),
                 (r'/ws5', RelationStatus),
                 (r'/ws6', TopLocation),
                 (r'/ws7', TopLanguage)
                ],
                debug=True)

'''---------------------------------------------------------------------
# This is typical startup code for Python
------------------------------------------------------------------------
'''


def main():
        run_wsgi_app(app)

if __name__ == "__main__":
        main()
