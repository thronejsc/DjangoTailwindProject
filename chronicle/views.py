from app.models import Journal, Document
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import DocumentForm



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

def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.save()
            return redirect('upload_document')
    else:
        form = DocumentForm()
    documents = Document.objects.all()
    return render(request, 'upload_document.html', {'form': form, 'documents': documents})