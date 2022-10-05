from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def myview(request):
    print(request.COOKIES)
    resp = HttpResponse('<li><p><a href="/hello">Test the session</a></p></li>')
    resp.set_cookie('dj4e_cookie', '83195156', max_age=1000)
    num_visits = request.session.get('num_visits',0) + 1
    request.session['num_visits'] = num_visits
    #logging.error('Hello world DJ4E in the log...')
    # print('Hello world DJ4E in a print statement...')
    # response = """<html><body><p>Hello world DJ4E in HTML</p>
    # <p>This sample code is available at
    # <a href="https://github.com/csev/dj4e-samples">
    # https://github.com/csev/dj4e-samples</a></p>
    # </body></html>"""
    return HttpResponse ('view count='+str(num_visits))

