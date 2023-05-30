from app.models import Journal, Document
from django.shortcuts import render, get_object_or_404, redirect
from app.forms import DocumentForm
from django.db.models import Q



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

def search_document(request):
    form = DocumentForm()
    documents = []
    not_found = False

    if request.method == 'POST':
        search_query = request.POST.get('search')
        documents = Document.objects.filter(subject__icontains=search_query)
        if not documents:
            not_found = True

    return render(request, 'search_document.html', {'form': form, 'documents': documents, 'not_found': not_found})

def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    file_content = document.get_file_content()

    return render(request, 'view_document.html', {'document': document, 'file_content': file_content})