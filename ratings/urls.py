from django.conf.urls import url
from ratings.views import vote

urlpatterns = [
    url(r'^vote/$', vote, name='ratings_vote'),
]
