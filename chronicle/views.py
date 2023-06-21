from app.models import Journal, Document, Article
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import DocumentForm
from django.db.models import Q



def index(request):
    journals = Journal.objects.all()
    return render(request, 'home.html')

def journal_list2(request):
    journals = Journal.objects.all()
    context = {
        'journals': journals
    }
    return render(request, 'journal-list copy.html', context)
    