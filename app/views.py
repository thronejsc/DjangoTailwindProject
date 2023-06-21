from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView

from app.forms import MyUserCreationForm, ArticleForm, ReviewForm, ArticleFormFinal
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q

from app.models import MyUser, STAGE_UNDER_REVIEW, Journal, Article, STAGE_PUBLISHED, EditorNote, STAGE_REJECTED, \
    STAGE_ACCEPTED

from .models import Subject, Document
from .forms import DocumentForm, CommentForm, SearchForm
from django.shortcuts import render, get_object_or_404
from .models import Document
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.base import ContentFile

# ----DECORATOR


def is_author(user):
    if user.user_type == "AUTHOR":
        return True
    return False


def is_editor(user):
    if user.user_type == "EDITOR":
        return True
    return False


def is_publisher(user):
    if user.user_type == "PUBLISHER":
        return True
    return False


#  ---- END DECORATOR

class SignUpView(CreateView):
    form_class = MyUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def where_next(request):
    """Simple redirector to figure out where the user goes next."""
    if request.user.is_anonymous:
        return HttpResponse(reverse('login'))
    elif request.user.user_type == "AUTHOR":
        return HttpResponseRedirect(reverse('author-profile'))
    elif request.user.user_type == "EDITOR":
        return HttpResponseRedirect(reverse('editor-profile'))
    elif request.user.user_type == "PUBLISHER":
        return HttpResponseRedirect(reverse('publisher-profile'))


@user_passes_test(is_author)
def author_base(request):
    articles_accepted = Article.objects.filter(state='Accepted').filter(author=request.user).count()
    articles_in_queue = Article.objects.filter(state='Under Review').filter(author=request.user).count()
    articles_rejected = Article.objects.filter(state='Rejected').filter(author=request.user).count()
    articles_published = Article.objects.filter(state='Published').filter(author=request.user).count()
    articles = Article.objects.filter(author=request.user)
    # print(articles_in_queue)
    labels = ["Articles In Peer Review","Articles Acepted","Articles Published","Articles Rejected"]
    data = []
    # labels.append
    data.append(articles_in_queue)
    data.append(articles_accepted)
    data.append(articles_published)
    data.append(articles_rejected)
    context = {
        'articles_in_queue': articles_in_queue,
        'articles_accepted': articles_accepted,
        'articles_rejected': articles_rejected,
        'articles_published': articles_published,
        'articles': articles,
        'labels': labels,
        'data': data,
    }
    return render(request, 'author/author.html', context)


@user_passes_test(is_editor)
def editor_base(request):
    articles_accepted = Article.objects.filter(state='Accepted').count()
    articles_in_queue = Article.objects.filter(state='Under Review').count()
    articles_rejected = Article.objects.filter(state='Rejected').count()
    articles_published = Article.objects.filter(state='Published').count()
    articles = Article.objects.filter(author=request.user)
    # print(articles_in_queue)
    labels = ["Articles In Peer Review","Articles Acepted","Articles Published","Articles Rejected"]
    data = []
    # labels.append
    data.append(articles_in_queue)
    data.append(articles_accepted)
    data.append(articles_published)
    data.append(articles_rejected)
    context = {
        'articles_in_queue': articles_in_queue,
        'articles_accepted': articles_accepted,
        'articles_rejected': articles_rejected,
        'articles_published': articles_published,
        'articles': articles,
        'labels': labels,
        'data': data,
    }
    return render(request, 'editor/editor.html', context)


@user_passes_test(is_publisher)
def publisher_base(request):
    authors = MyUser.objects.filter(user_type='AUTHOR').count()
    editors = MyUser.objects.filter(user_type='EDITOR').count()
    articles_published = Article.objects.filter(state='Published').count()
    articles_accepted = Article.objects.filter(state='Accepted').count()
    # print(authors,editors)
    labels = ["Articles Published","Articles Acepted"]
    data = []
    # labels.append
    data.append(articles_published)
    data.append(articles_accepted)
    context = {
        'authors': authors,
        'editors': editors,
        'articles_published': articles_published,
        'articles_accepted': articles_accepted,
        'labels': labels,
        'data': data,
    }
    # print(labels)
    # print(data)
    return render(request, 'publisher/publisher.html',context)


def journal_list(request):
    journals = Journal.objects.all()
    context = {
        'journals': journals
    }
    return render(request, 'journal-list.html', context)


def journal_view(request, journal_id):
    template_name = 'journal-detail.html'
    journal = get_object_or_404(Journal, id=journal_id)
    articles = Article.objects.filter(journal=journal_id).filter(
        state=STAGE_PUBLISHED)  # change filter STATE  to published
    # print(articles)
    context = {
        'journal': journal,
        'articles': articles,
    }
    return render(request, template_name, context)


def article_view(request, article_id):
    template_name = 'article-detail.html'
    article = get_object_or_404(Article, id=article_id)
    keywords = article.keywords
    print(keywords)
    context = {
        'article': article,
        'keywords': keywords,
    }
    return render(request, template_name, context)

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
            file_content = request.FILES['file'].read()
            file_name = request.FILES['file'].name
            document.file.save(file_name, ContentFile(file_content))
            document.file.close()  # Close the file after saving to the database
            document.save()
            return redirect('upload_document')
    else:
        form = DocumentForm()
    documents = Document.objects.all()
    return render(request, 'upload_document.html', {'form': form, 'documents': documents})


def search_document(request):
    form = SearchForm()
    documents = []
    not_found = False

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            year_level = form.cleaned_data['year_level']
            documents = Document.objects.filter(subject__icontains=subject, year_level=year_level)
            if not documents:
                not_found = True

    return render(request, 'author/search-form.html', {'form': form, 'documents': documents, 'not_found': not_found})

@login_required
def view_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    comments = document.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            comment.save()
            return JsonResponse({'success': True})  # Return a JSON response indicating successful comment submission
        else:
            return JsonResponse({'success': False, 'errors': form.errors})  # Return a JSON response with form errors
    else:
        form = CommentForm()

    # Assuming you have a FileField or ImageField in the Document model
    pdf_file = document.file

    # Generate the URL for the PDF file
    pdf_url = request.build_absolute_uri(pdf_file.url)

    return render(request, 'view_document.html', {'document': document, 'comments': comments, 'form': form, 'pdf_url': pdf_url})


def comment_submit(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, pk=document_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            comment.created_at = timezone.now()
            comment.save()
            return redirect('view_document', document_id=document_id)  # Redirect to the view_document page
        else:
            form = CommentForm()  # Clear the form for a new comment
            comments = document.comments.all()
            return render(request, 'view_document.html', {'document': document, 'comments': comments, 'form': form})
    else:
        return redirect('view_document', document_id=document_id)  # Redirect to the view_document page for invalid request method

def download_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    # Retrieve the file path
    file_path = document.file.path

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Set the appropriate content type for the response
        response = HttpResponse(file.read(), content_type='application/pdf')

        # Set the Content-Disposition header to prompt download
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(document.file.name)

        return response

@user_passes_test(is_author)
def submit_article(request, journal_id):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            print("VALID")
            print(request.user)
            journal = get_object_or_404(Journal, id=journal_id)
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.journal = journal
            new_article.state = STAGE_UNDER_REVIEW
            print(new_article)
            new_article.save()
            # send_review_email()
            return HttpResponseRedirect(reverse('author-profile'))
    else:
        form = ArticleForm()
        return render(request, 'author/article-form.html', {'form': form})


@login_required
@user_passes_test(is_editor)
def article_list(request):
    pending_articles = Article.objects.filter(state=STAGE_UNDER_REVIEW)
    accepted_articles = Article.objects.filter(state=STAGE_ACCEPTED)
    rejected_articles = Article.objects.filter(state=STAGE_REJECTED)
    context = {
        'pending_articles': pending_articles,
        'accepted_articles': accepted_articles,
        'rejected_articles': rejected_articles,
    }
    return render(request, 'editor/article-list.html', context)


@login_required
@user_passes_test(is_editor)
def review_pending_article(request, article_id):
    reviewed_article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_comment = form.cleaned_data['new_comment']
            if form.cleaned_data['approval'] == 'approve':
                reviewed_article.state = STAGE_ACCEPTED
            else:
                reviewed_article.state = STAGE_REJECTED
            reviewed_article.save()
            if new_comment:
                c = EditorNote(article=reviewed_article, text=new_comment)
                c.save()
            return HttpResponseRedirect(reverse('article-list'))
    else:
        form = ReviewForm()
        return render(request, 'editor/review-article.html', {'form': form, 'article': reviewed_article,
                                                                'comments': reviewed_article.Editornotes.all()})


@login_required
@user_passes_test(is_publisher)
def publisher_article_list(request):
    accepted_articles = Article.objects.filter(state=STAGE_ACCEPTED)
    published_article = Article.objects.filter(state=STAGE_PUBLISHED)
    context = {
        'accepted_articles': accepted_articles,
        'published_article': published_article,
    }
    return render(request, 'publisher/article-list.html', context)


def publisher_review(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        form = ArticleFormFinal(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('publisher-article-list'))
        else:
            print("FORM INVALID")
            return HttpResponse("FORM INVLID")
    else:
        form = ArticleFormFinal(instance=article)
        context = {
            'form': ArticleFormFinal(instance=article),
            'article': article
        }
        return render(request, 'publisher/review-article.html', context)
