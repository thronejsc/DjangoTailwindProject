from app.models import Journal
from django.shortcuts import render, get_object_or_404


def index(request):
    journals = Journal.objects.all()
    return render(request, 'home.html')

def journal_search(request):
    template_name = 'journal_search.html'
    query = request.GET.get('q')
    schoolworks = Journal.objects.all()
    
    if query:
        schoolworks = schoolworks.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(author__icontains=query)
        )
    
    context = {
        'schoolworks': schoolworks,
        'query': query
    }
    
    return render(request, template_name, context)
