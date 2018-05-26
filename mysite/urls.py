from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='Home'),

    path('loggedAs:<int:person_id>/election:<int:election_id>/details/',
         views.election_details, name='Szczegóły wyborów'),
    path('loggedAs:<int:person_id>/election:<int:election_id>/results/',
         views.election_results, name='Wyniki wyborów'),
    path('loggedAs:<int:person_id>/election:<int:election_id>/candidates/',
         views.candidate_list, name='Lista kandydatów'),
    path('loggedAs<int:person_id>/election:<int:election_id>/vote/', views.vote, name='Głosuj'),
    path('loggedAs:<int:person_id>/', views.elections_list, name='Lista wyborów'),
    path('login/', views.login, name='Logowanie'),
    path('login/user', views.user_login, name='Logowanie użytkownika'),
    path('login/mod', views.mod_login, name='Logowanie moderatora'),
]

