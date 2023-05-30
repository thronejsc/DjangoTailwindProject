from app.models import Journal, Document
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import DocumentForm
from django.db.models import Q



def index(request):
    journals = Journal.objects.all()
    return render(request, 'home.html')