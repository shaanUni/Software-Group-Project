from django.shortcuts import render

def home(request):
    return render(request, "pages/home.html")

def mockup_teams(request):
    return render(request, "pages/mockup_teams.html")

def mockup_organisation(request):
    return render(request, "pages/mockup_organisation.html")