from django.shortcuts import render
from .forms import SubscriberForm, PostsForm, EmailSentForm
from .models import Subscribers, Posts, EmailSent
from datetime import datetime
from pytz import timezone
from django.core.mail import EmailMessage
from decouple import config
def my_scheduled_job():
    import facebook
    graph = facebook.GraphAPI(config('FACEBOOK_USER_TOKEN'))
    post = graph.get_object(id=config('GNDEC_PAGE_ID'), fields='feed')
    post_id = post['feed']['data'][0]['id']
    post_date_time = post['feed']['data'][0]['created_time'][:-5]
    #facebook provie post time in UTC so we have to convert it into IST
    date_str = post_date_time
    datetime_obj_naive = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    datetime_obj_pacific = timezone('UTC').localize(datetime_obj_naive)
    datetime_obj_pacific = datetime_obj_pacific.astimezone(timezone('Asia/Kolkata'))
    #date of post
    post_date = datetime_obj_pacific.strftime("%Y-%m-%d")
    #time of post
    post_time = datetime_obj_pacific.strftime("%H:%M:%S(%Z)")
    #facebook post data
    message = post['feed']['data'][0]['message']

    #last post id to whom email was sent
    last_email_post = EmailSent.objects.last()
    last_email_post = last_email_post.post_id


    #subscriber
    subscribers = Subscribers.objects.all().values_list('email')
    last_entry = Posts.objects.last()
    if not last_entry.post_id == post_id:
        Posts.objects.create(created_time = post_time, created_date = post_date, post_id = post_id, message = message)

        if not last_email_post == post_id:
            for users in subscribers:
	            #for emailid in users:
                toemail = users[0]
                subject = 'New post @TNP GNDEC '+post_date+' '+post_time
                msg_body = '*You are getting multiple emails because it is beta version of our app. Just bear with us.*\n'+' '+message+'\n \n' '*Team*''\n \n''*Jugadi Time*\n(https://jugaditi.me)'
                email = EmailMessage(subject, msg_body, to=[toemail])
                email.send()
            EmailSent.objects.create(post_id = post_id)

    else:
        if not last_email_post == post_id:
            for users in subscribers:
	            #for emailid in users:
                toemail = users[0]
                subject = 'New post @TNP GNDEC '+post_date+' '+post_time
                msg_body = '*You are getting multiple emails because it is beta version of our app. Just bear with us.*\n'+' '+message+'\n \n' '*Team*''\n \n''*Jugadi Time*(https://jugaditi.me)'
                email = EmailMessage(subject, msg_body, to=[toemail])
                email.send()
            EmailSent.objects.create(post_id = post_id)
