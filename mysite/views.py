from django import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone

# Create your views here.
from django.template import loader

from mysite.models import myUser, Mod
from .models import osoba, oddanyGlos, osobaWybory, wybory
from .forms import OsobaForm, OsobaWyboryForm, WyboryForm, ModForm, LoginForm


def home_view(request):
    username = ''
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
        else:
            username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    template = loader.get_template("home.html")
    all_elections = wybory.objects.order_by('-dataRozpoczecia')[:5]
    context = {
        'username': username,
        'all_elections': all_elections
    }
    return HttpResponse(template.render(context, request))


class allowedElection(object):
    myElection = wybory()
    voted = osobaWybory()
    in_time = ''


def elections_list(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    template = loader.get_template("election_list.html")
    person_id = logged_user.user_profile.pesel
    mylist = []
    allowed_elections = wybory.objects.all() \
        .filter(ID_WYBOROW__in=osobaWybory.objects.filter(pesel=person_id).values_list('ID_WYBOROW', flat=True)) \
        .order_by('dataZakonczenia')
    for x in allowed_elections:
        voted = osobaWybory.objects.get(ID_WYBOROW=x.ID_WYBOROW, pesel=person_id)
        if timezone.now() < x.dataZakonczenia:
            in_time = True
        else:
            in_time = False
        election = allowedElection()
        election.myElection = x
        election.voted = voted
        election.in_time = in_time
        mylist.append(election)

    logged_person = get_object_or_404(osoba, pk=person_id)
    username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    context = {
        'username': username,
        'allowed_elections': mylist,
        'logged_person': logged_person,
    }
    return HttpResponse(template.render(context, request))


def election_details(request, election_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')
    person_id = logged_user.user_profile.pesel
    template = loader.get_template("election_details.html")
    election = get_object_or_404(wybory, pk=election_id)
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = candidates_with_rating(election_id)
    turnout = election_turnout(election_id)
    username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    context = {
        'username': username,
        'election': election,
        'logged_person': logged_person,
        'candidates': candidates,
        'turnout': turnout
    }

    return HttpResponse(template.render(context, request))


class candidateWithRating(object):
    name = ''
    surname = ''
    rating = 0


# funkcja pomocnicza zwracająca frekwencję danych wyborów
def election_turnout(election_id):
    # wszyscy biorący udział w wyborach
    all_voters = osobaWybory.objects.filter(ID_WYBOROW=election_id).count()

    # ci, którzy zagłosowali
    people_who_voted = osobaWybory.objects.filter(ID_WYBOROW=election_id, oddalGlos=True).count()

    # frekwencja wyborcza
    turnout = round(people_who_voted * 100 / all_voters, 2)

    return turnout


# funkcja pomocnicza zwracająca wszystkich kandydatów danych wyborów, wraz z ich poparciem
def candidates_with_rating(election_id):
    # wszyscy kandydaci danych wyborów
    candidates = osoba.objects.filter(pesel__in=osobaWybory.objects.filter(ID_WYBOROW=election_id, kandydat=True)
                                      .values_list('pesel', flat=True))

    # wszystkie głosy
    all_votes = oddanyGlos.objects.filter(ID_WYBOROW=election_id).count()

    mylist = []

    for candidate in candidates:
        new_candidate = candidateWithRating()
        new_candidate.name = candidate.imie
        new_candidate.surname = candidate.nazwisko

        # głosy na danego kandydata
        votes = oddanyGlos.objects.filter(ID_WYBOROW=election_id, ID_KANDYDATA=candidate.pesel).count()

        # poparcie
        if votes == 0:
            rating = 0
        else:
            rating = round(votes * 100 / all_votes, 2)
        new_candidate.rating = rating
        mylist.append(new_candidate)

    mylist.sort(key=lambda x: x.rating, reverse=True)
    return mylist


def election_results(request, election_id):

    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')
    person_id = logged_user.user_profile.pesel
    template = loader.get_template("election_results.html")
    election = get_object_or_404(wybory, pk=election_id)
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = candidates_with_rating(election_id)
    turnout = election_turnout(election_id)

    username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    context = {
        'username': username,
        'election': election,
        'logged_person': logged_person,
        'candidates': candidates,
        'turnout': turnout
    }

    return HttpResponse(template.render(context, request))


def user_login(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return elections_list(request)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logged_user = myUser.objects.get(username=username)
                if not logged_user.is_mod:
                    login(request, user)
                    return elections_list(request)
                else:
                    raise forms.ValidationError('Wystąpił błąd w formularzu')
            else:
                raise forms.ValidationError('Niepoprawna nazwa lub hasło')
        else:
            template = loader.get_template('user_login.html')
            error_message = "Wprowadzono niepoprawne dane"
            return HttpResponse(template.render({'form': form, 'error_message': error_message}, request))
    else:
        form = LoginForm()

    template = loader.get_template('user_login.html')
    return HttpResponse(template.render({'form': form}, request))


def candidate_list(request, election_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')
    person_id = logged_user.user_profile.pesel
    template = loader.get_template("candidate_list.html")
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = osoba.objects.filter(pesel__in=osobaWybory.objects.filter(ID_WYBOROW=election_id, kandydat=True).
                                      values_list('pesel', flat=True)).order_by('nazwisko', 'imie')
    election = get_object_or_404(wybory, pk=election_id)

    username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    context = {
        'username': username,
        'logged_person': logged_person,
        'candidates': candidates,
        'election': election
    }
    return HttpResponse(template.render(context, request))


def vote(request, election_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')
    person_id = logged_user.user_profile.pesel
    template = loader.get_template("vote.html")
    message = ''
    logged_person = get_object_or_404(osoba, pk=person_id)
    election = get_object_or_404(wybory, pk=election_id)
    accepted = True
    if request.method == 'POST':
        candidates = request.POST.getlist('choices')

    voted = osobaWybory.objects.get(pesel=person_id, ID_WYBOROW=election_id).__getattribute__('oddalGlos')

    if len(candidates) == 0 or len(candidates) > election.maxLiczbaKandydatowDoPoparcia or voted:
        accepted = False
        message = 'Wybrano niepoprawną liczbę kandydatów lub głosowano już w tych wyborach.'
    else:
        voted = osobaWybory.objects.get(ID_WYBOROW=election, pesel=person_id)
        voted.oddalGlos = True
        voted.save()

    if accepted:
        for pesel in candidates:
            new_candidate = get_object_or_404(osoba, pk=pesel)
            new_vote = oddanyGlos(ID_WYBOROW=election, ID_KANDYDATA=new_candidate)
            new_vote.save()
        message = 'Zagłosowano pomyślnie w wyborach ' + election.nazwaWyborow + ' na następujących kandydatów: '
        for pesel in candidates:
            candidate = get_object_or_404(osoba, pk=pesel)
            message += candidate.imie + ' ' + candidate.nazwisko + ' '
    username = logged_user.user_profile.imie + ' ' + logged_user.user_profile.nazwisko
    context = {
        'username': username,
        'logged_person': logged_person,
        'accepted': accepted,
        'message': message,
        'election': election
    }
    return HttpResponse(template.render(context, request))


# Funkcje moderatora

def mod_person_list(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')
    template = loader.get_template("ModTemplates/mod_person_list.html")
    all_people = osoba.objects.all()
    username = 'moderator ' +  logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'all_people': all_people
    }
    return HttpResponse(template.render(context, request))


class electionsForList(object):
    myElection = wybory()
    in_time = ''


def mod_election_list(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    template = loader.get_template("ModTemplates/mod_election_list.html")

    mylist = []
    all_elections = wybory.objects.all().order_by('dataZakonczenia')
    for x in all_elections:
        if timezone.now() < x.dataZakonczenia:
            in_time = True
        else:
            in_time = False
        this_election = electionsForList()
        this_election.myElection = x
        this_election.in_time = in_time
        mylist.append(this_election)

    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'all_elections': mylist
    }
    return HttpResponse(template.render(context, request))


def mod_new_person(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = OsobaForm(request.POST)

        if form.is_valid():
            user = myUser.objects.create_user(username=form.cleaned_data['pesel'], password=form.cleaned_data['nr_dowodu'])
            user.set_password(user.password)
            new_person = osoba(pesel=form.cleaned_data['pesel'],
                               imie=form.cleaned_data['imie'],
                               nazwisko=form.cleaned_data['nazwisko'],
                               nr_dowodu=form.cleaned_data['nr_dowodu'],
                               user=user)
            new_person.save()
            return mod_person_list(request)
        else:
            raise forms.ValidationError('Wystąpił błąd w formularzu')
    else:
        form = OsobaForm()
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    template = loader.get_template('ModTemplates/mod_new_person.html')
    return HttpResponse(template.render({'form': form, 'username': username}, request))


def mod_new_election(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = WyboryForm(request.POST)
        if form.is_valid():
            if form.someValidation():
                some_election = wybory(nazwaWyborow=form.cleaned_data['nazwaWyborow'],
                                        maxLiczbaKandydatowDoPoparcia=form.cleaned_data['maxLiczbaKandydatowDoPoparcia'],
                                        dataRozpoczecia=form.cleaned_data['dataRozpoczecia'],
                                        dataZakonczenia=form.cleaned_data['dataZakonczenia'])
                some_election.save()
                return mod_election_list(request)
            else:
                raise forms.ValidationError('Data rozpoczęcia nie może być po dacie zakończenia')
        else:
            raise forms.ValidationError('Wystąpił błąd w formularzu')
    else:
        form = WyboryForm()
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    template = loader.get_template('ModTemplates/mod_new_election.html')
    return HttpResponse(template.render({'form': form, 'username': username}, request))


class personCandidate(object):
    person = osoba()
    isCandidate = ''


def mod_election_details(request, election_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    template = loader.get_template('ModTemplates/mod_election_details.html')
    election = get_object_or_404(wybory, pk=election_id)
    all_voters = osoba.objects.filter(pesel__in=osobaWybory.objects.
                                      filter(ID_WYBOROW=election_id).values_list('pesel', flat=True))
    my_list = []
    for voter in all_voters:
        new_person = personCandidate()
        new_person.person = voter
        new_person.isCandidate = osobaWybory.objects.get(ID_WYBOROW=election_id, pesel=voter.pesel)\
            .__getattribute__('kandydat')
        my_list.append(new_person)

    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'election': election,
        'allowed': my_list
    }
    return HttpResponse(template.render(context, request))


def mod_add_person_to_election(request, election_id):

    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = OsobaWyboryForm(request.POST)
        if form.is_valid():
            pesel = form.cleaned_data['pesel']
            election = get_object_or_404(wybory, pk=election_id)
            # Sprawdzenie czy takie osoby głosują już w tych wyborach
            voters = osobaWybory.objects.filter(ID_WYBOROW=election_id, pesel=pesel).count()
            if voters == 0:
                new_osoba_wybory = osobaWybory(ID_WYBOROW=election,
                                           pesel=pesel,
                                           kandydat=form.cleaned_data['kandydat'],
                                           oddalGlos=False)
                new_osoba_wybory.save()
                return mod_election_list(request)
            else:
                message = 'Podana osoba głosuje już w tych wyborach'
                template = loader.get_template('ModTemplates/mod_list_choice.html')
                return HttpResponse(template.render({'message': message}, request))
        else:
            raise forms.ValidationError('Wystąpił błąd w formularzu')
    else:

        form = OsobaWyboryForm()
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {'form': form, 'election_id': election_id, 'username': username}
    template = loader.get_template('ModTemplates/mod_add_person_to_election.html')

    return HttpResponse(template.render(context, request))


def mod_list_choice(request):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    template = loader.get_template("ModTemplates/mod_list_choice.html")
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username
    }
    return HttpResponse(template.render(context, request))


def mod_login(request):
    #jeśli już jest zalogowany
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if logged_user.is_mod:
            return mod_list_choice(request)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logged_user = myUser.objects.get(username=username)
                if logged_user.is_mod:
                    login(request, user)
                    return mod_list_choice(request)
                else:
                    raise forms.ValidationError('Wystąpił błąd w formularzu')
            else:
                raise forms.ValidationError('Niepoprawna nazwa lub hasło')
        else:
            template = loader.get_template('ModTemplates/mod_login.html')
            error_message = "Wprowadzono niepoprawne dane"
            return HttpResponse(template.render({'form': form, 'error_message': error_message}, request))
    else:
        form = LoginForm()

    template = loader.get_template('ModTemplates/mod_login.html')
    return HttpResponse(template.render({'form': form}, request))


def mod_delete_person(request, person_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    instance = get_object_or_404(osoba, pk=person_id)
    person = instance.imie + ' ' + instance.nazwisko
    instance.delete()
    template = loader.get_template('ModTemplates/mod_deleted_person.html')
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    return HttpResponse(template.render({'person': person, 'username': username}, request))


def mod_delete_election(request, election_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    instance = get_object_or_404(wybory, pk=election_id)
    deleted_election = instance.nazwaWyborow
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'election': deleted_election
    }
    instance.delete()
    template = loader.get_template('ModTemplates/mod_deleted_election.html')
    return HttpResponse(template.render(context, request))


def mod_delete_person_from_election(request, election_id, person_id):
    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    instance = get_object_or_404(osobaWybory, ID_WYBOROW=election_id, pesel=person_id)
    election = get_object_or_404(wybory, pk=election_id)
    person = get_object_or_404(osoba, pk=person_id)
    template = loader.get_template('ModTemplates/mod_delete_person_from_election.html')
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'election': election,
        'person': person
    }
    instance.delete()
    return HttpResponse(template.render(context, request))


def new_mod(request):

    if request.user.is_authenticated:
        user = request.user
        logged_user = myUser.objects.get(username=user.username)
        if not logged_user.is_mod:
            return render(request, 'access_denied.html')
    else:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = ModForm(request.POST)
        if form.is_valid():
            user = myUser.objects.create_user(username=form.cleaned_data['username'],password=form.cleaned_data['password'], is_mod=True)
            user.set_password(user.password)

            new_mod = Mod(user=user,
                          name=form.cleaned_data['name'],
                          surname=form.cleaned_data['surname'])
            new_mod.save()
            return mod_list_choice(request)
        else:
            raise forms.ValidationError('Wystąpił błąd w formularzu')
    else:
        form = ModForm()
    template = loader.get_template('ModTemplates/new_mod.html')
    username = 'moderator ' + logged_user.mod_profile.name + ' ' + logged_user.mod_profile.surname
    context = {
        'username': username,
        'form': form
    }
    return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    return home_view(request)
