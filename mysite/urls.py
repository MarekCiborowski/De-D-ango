from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='Home'),

    path('loggedUser/election:<int:election_id>/details/',
         views.election_details, name='Szczegóły wyborów'),
    path('loggedUser/election:<int:election_id>/results/',
         views.election_results, name='Wyniki wyborów'),
    path('loggedUser/election:<int:election_id>/candidates/',
         views.candidate_list, name='Lista kandydatów'),
    path('loggedUser/election:<int:election_id>/vote/', views.vote, name='Głosuj'),
    path('loggedUser/', views.elections_list, name='Lista wyborów'),
    path('login/user', views.user_login, name='Logowanie użytkownika'),

    path('login/mod', views.mod_login, name='Logowanie moderatora'),
    path('mod/', views.mod_list_choice, name='Wybór listy mod'),
    path('mod/elections', views.mod_election_list, name='Wybory mod'),
    path('mod/elections/add', views.mod_new_election, name='Nowe wybory mod'),
    path('mod/elections/details/<int:election_id>', views.mod_election_details, name='Szczegóły wyborów mod'),
    path('mod/elections/add_voter/<int:election_id>', views.mod_add_person_to_election, name='Dodaj wyborców mod'),
    path('mod/people', views.mod_person_list, name='Wyborcy mod'),
    path('mod/people/add', views.mod_new_person, name='Nowy wyborca mod'),
    path('mod/people/delete/<int:person_id>', views.mod_delete_person, name='Usuń osobę'),
    path('mod/elections/delete/<int:election_id>', views.mod_delete_election, name='Usuń wybory'),
    path('mod/new', views.new_mod, name='Nowy moderator'),
    path('mod/elections/delete_voter/<int:election_id>/<int:person_id>',
         views.mod_delete_person_from_election, name='Usuń osobę z wyborów'),
    path('logout', views.logout_view, name='Wyloguj')
]

