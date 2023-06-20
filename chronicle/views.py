from app.models import Journal, Document, Article
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import DocumentForm
from django.db.models import Q



def index(request):
    journals = Journal.objects.all()
    return render(request, 'home.html')

def index2(request):
    journals = Journal.objects.all()
    return render(request, 'home2.html')