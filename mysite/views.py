from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone

# Create your views here.
from django.template import loader
from .models import osoba, oddanyGlos, osobaWybory, wybory


def home_view(request):
    template = loader.get_template("home.html")
    all_elections = wybory.objects.order_by('-dataRozpoczecia')[:5]
    context = {
        'all_elections': all_elections
    }
    return HttpResponse(template.render(context, request))


class allowedElection(object):
    myElection = wybory()
    voted = osobaWybory()
    in_time = ''


def elections_list(request, person_id):
    template = loader.get_template("election_list.html")
    mylist = []
    allowed_elections = wybory.objects.all() \
        .filter(ID_WYBOROW__in=osobaWybory.objects.filter(pesel=person_id).values_list('ID_WYBOROW', flat=True))\
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

    context = {
        'allowed_elections': mylist,
        'logged_person': logged_person,
    }
    return HttpResponse(template.render(context, request))


def election_details(request, person_id, election_id):
    template = loader.get_template("election_details.html")
    election = get_object_or_404(wybory, pk=election_id)
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = candidates_with_rating(election_id)
    turnout = election_turnout(election_id)

    context = {
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


def election_results(request, person_id, election_id):
    template = loader.get_template("election_results.html")
    election = get_object_or_404(wybory, pk=election_id)
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = candidates_with_rating(election_id)
    turnout = election_turnout(election_id)

    context = {
        'election': election,
        'logged_person': logged_person,
        'candidates': candidates,
        'turnout': turnout
    }

    return HttpResponse(template.render(context, request))


def login(request):
    return render(request, 'voter_login.html')


def user_login(request):
    return render(request, 'voter_login.html')


def mod_login(request):
    return render(request, 'voter_login.html')


def candidate_list(request, person_id, election_id):
    template = loader.get_template("candidate_list.html")
    logged_person = get_object_or_404(osoba, pk=person_id)
    candidates = osoba.objects.filter(pesel__in=osobaWybory.objects.filter(ID_WYBOROW=election_id, kandydat=True).
                                      values_list('pesel', flat=True)).order_by('nazwisko', 'imie')
    election = get_object_or_404(wybory, pk=election_id)
    context = {
        'logged_person': logged_person,
        'candidates': candidates,
        'election': election
    }
    return HttpResponse(template.render(context, request))


def vote(request, person_id, election_id):

    template = loader.get_template("vote.html")
    logged_person = get_object_or_404(osoba, pk=person_id)
    election = get_object_or_404(wybory, pk=election_id)
    accepted = True
    candidates = request.POST.getlist('choices')

    voted = osobaWybory.objects.get(pesel=person_id, ID_WYBOROW=election_id).__getattribute__('oddalGlos')

    if len(candidates) == 0 or len(candidates) > election.maxLiczbaKandydatowDoPoparcia or voted:
        accepted = False
    else:
        voted = osobaWybory.objects.get(ID_WYBOROW=election, pesel=person_id)
        voted.oddalGlos = True
        voted.save()

    if accepted:
        for pesel in candidates:
            new_candidate = get_object_or_404(osoba, pk=pesel)
            new_vote = oddanyGlos(ID_WYBOROW=election, ID_KANDYDATA=new_candidate)
            new_vote.save()

    message = 'Zagłosowano pomyślnie w wyborach '+election.nazwaWyborow + ' na następujących kandydatów: '
    for pesel in candidates:
        candidate = get_object_or_404(osoba, pk=pesel)
        message += candidate.imie + ' ' + candidate.nazwisko + ' '

    context = {
        'logged_person': logged_person,
        'accepted': accepted,
        'message': message,
        'election': election
    }
    return HttpResponse(template.render(context, request))
