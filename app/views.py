from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.views import View

from app.forms import MyUserCreationForm, ArticleForm, ReviewForm, ArticleFormFinal
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q, Count

from app.models import MyUser, STAGE_UNDER_REVIEW, Journal, Article, STAGE_PUBLISHED, EditorNote, STAGE_REJECTED, \
    STAGE_ACCEPTED

from .models import Subject, Document
from .forms import DocumentForm, CommentForm, SearchForm, ArticleSearchForm
from django.shortcuts import render, get_object_or_404
from .models import Document
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.base import ContentFile
import requests
from django.conf import settings
import os
from django.contrib.auth import logout, login
from social_django.models import UserSocialAuth
from allauth.socialaccount.models import SocialAccount
# ----DECORATOR

from social_django.utils import psa

def signup_google(request):
    return redirect('social:begin', backend='google-oauth2')

def is_student(user):
    if user.user_type == "STUDENT":
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

    def form_valid(self, form):
        # Call the parent form_valid method to save the user
        response = super().form_valid(form)

        # Check if the user signed up using a Google account
        if self.request.POST.get('provider') == 'google':
            # Get the UserSocialAuth associated with the user
            social_auth = UserSocialAuth.objects.get(user=self.object)

            if social_auth.provider == 'google-oauth2':
                # Set the user type as 'student'
                self.object.user_type = 'student'

                # Obtain the name or username from the Google account
                extra_data = social_auth.extra_data
                name = extra_data.get('name')
                username = extra_data.get('username')

                # Set the name or username in the MyUser object
                if name:
                    self.object.name = name
                elif username:
                    self.object.username = username

                self.object.save()

                # Log in the user
                login(self.request, self.object)

        return response
        
@login_required
def where_next(request):
    """Simple redirector to figure out where the user goes next."""
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('login'))
    elif request.user.is_admin:
        # Allow admin users access to anything
        return HttpResponseRedirect(reverse('admin:index'))
    elif request.user.user_type == "STUDENT":
        return HttpResponseRedirect(reverse('student-profile'))
    elif request.user.user_type == "PUBLISHER":
        return HttpResponseRedirect(reverse('publisher-profile'))
    else:
        # Check if user signed in with a Google account
        try:
            social_account = UserSocialAuth.objects.get(user=request.user, provider='google-oauth2')
            if social_account:
                # Set the user type as 'STUDENT' for Google sign-in
                request.user.user_type = "STUDENT"
                request.user.save()
                return HttpResponseRedirect(reverse('student-profile'))  # Redirect to the student profile
        except UserSocialAuth.DoesNotExist:
            # Redirect for users without specific roles
            raise Http404("Unauthorized")




@user_passes_test(is_student)
def student_base(request):
    articles_accepted = Article.objects.filter(state='Accepted').filter(student=request.user).count()
    articles_in_queue = Article.objects.filter(state='Under Review').filter(student=request.user).count()
    articles_rejected = Article.objects.filter(state='Rejected').filter(student=request.user).count()
    articles_published = Article.objects.filter(state='Published').filter(student=request.user).count()
    articles = Article.objects.filter(student=request.user)
    documents = Document.objects.filter(uploader=request.user).count()
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
        'documents': documents,
        'labels': labels,
        'data': data,
    }
    return render(request, 'student/student.html', context)


"""@user_passes_test(is_publisher)
def editor_base(request):
    articles_accepted = Article.objects.filter(state='Accepted').count()
    articles_in_queue = Article.objects.filter(state='Under Review').count()
    articles_rejected = Article.objects.filter(state='Rejected').count()
    articles_published = Article.objects.filter(state='Published').count()
    articles = Article.objects.filter(student=request.user)
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
    return render(request, 'editor/editor.html', context)"""


@user_passes_test(is_publisher)
def publisher_base(request):
    articles_accepted = Article.objects.filter(state='Accepted').count()
    articles_in_queue = Article.objects.filter(state='Under Review').count()
    articles_rejected = Article.objects.filter(state='Rejected').count()
    articles_published = Article.objects.filter(state='Published').count()
    articles = Article.objects.filter(student=request.user)
    document_count = Document.objects.count()

    students = MyUser.objects.filter(user_type='STUDENT').count()
    editors = MyUser.objects.filter(user_type='PUBLISHER').count()

    labels = ["Articles In Peer Review", "Articles Accepted", "Articles Published", "Articles Rejected"]
    data = [articles_in_queue, articles_accepted, articles_published, articles_rejected]

    context = {
        'students': students,
        'editors': editors,
        'articles_published': articles_published,
        'articles_accepted': articles_accepted,
        'articles_in_queue': articles_in_queue,
        'articles_rejected': articles_rejected,
        'articles': articles,
        'document_count': document_count,
        'labels': labels,
        'data': data,
    }

    return render(request, 'publisher/publisher.html', context)



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

@login_required
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

@login_required
def search_articles(request):
    form = ArticleSearchForm(request.GET or None)
    articles = Article.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        search_option = form.cleaned_data['search_option']

        if search_option == 'text':
            # Search articles by text
            articles = articles.filter(text__icontains=query)
        elif search_option == 'title':
            # Search articles by title
            articles = articles.filter(title__icontains=query)
        elif search_option == 'keywords':
            # Search articles by title
            articles = articles.filter(title__icontains=query)

    context = {
        'form': form,
    }

    if articles.exists():
        context['articles'] = articles

    return render(request, 'search_article.html', context)


@login_required
def journal_search(request):
    template_name = 'journal_search.html'
    query = request.GET.get('q')
    schoolworks = Journal.objects.all()
    
    if query:
        schoolworks = schoolworks.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(student__icontains=query)
        )
    
    context = {
        'schoolworks': schoolworks,
        'query': query
    }
    
    return render(request, template_name, context)

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_document')  # Redirect to the upload_document page
    else:
        form = DocumentForm()

    documents = Document.objects.all()

    return render(request, 'upload_document.html', {'form': form, 'documents': documents})


@login_required
def search_documents(request):
    form = SearchForm(request.GET or None)
    documents = Document.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        search_option = form.cleaned_data['search_option']

        if search_option == 'title':
            # Search documents by title
            documents = documents.filter(title__icontains=query)
        elif search_option == 'subject':
            # Search documents by subject
            documents = documents.filter(subject__icontains=query)

    context = {
        'form': form,
        'documents': documents,
    }

    return render(request, 'student/search-form.html', context)



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
            return redirect('view_document', document_id=document_id)  # Redirect to the view_document page
    else:
        form = CommentForm()

    # Generate the URL for the PDF file
    pdf_url = document.file.url

    return render(request, 'view_document.html', {'document': document, 'comments': comments, 'form': form, 'pdf_url': pdf_url})

@login_required
def comment_submit(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            comment.save()
            return redirect('view_document', document_id=document_id)  # Redirect to the view_document page
    else:
        form = CommentForm()

    comments = document.comments.all()

    return render(request, 'view_document.html', {'document': document, 'comments': comments, 'form': form})


@login_required
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

@user_passes_test(is_student)
def submit_article(request, journal_id):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            print("VALID")
            print(request.user)
            journal = get_object_or_404(Journal, id=journal_id)
            new_article = form.save(commit=False)
            new_article.student = request.user
            new_article.journal = journal
            new_article.state = STAGE_UNDER_REVIEW
            print(new_article)
            new_article.save()
            # send_review_email()
            return HttpResponseRedirect(reverse('student-profile'))
    else:
        form = ArticleForm()
        return render(request, 'student/article-form.html', {'form': form})


@login_required
@user_passes_test(is_publisher)
def article_list(request):
    pending_articles = Article.objects.filter(state=STAGE_UNDER_REVIEW)
    accepted_articles = Article.objects.filter(state=STAGE_ACCEPTED)
    rejected_articles = Article.objects.filter(state=STAGE_REJECTED)
    context = {
        'pending_articles': pending_articles,
        'accepted_articles': accepted_articles,
        'rejected_articles': rejected_articles,
    }
    return render(request, 'publisher/article-list(e).html', context)


@login_required
@user_passes_test(is_publisher)
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
        return render(request, 'publisher/review-article(e).html', {'form': form, 'article': reviewed_article,
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

@login_required
@user_passes_test(is_publisher)
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

@login_required
def document_list(request):
    documents = Document.objects.all()
    context = {
        'documents': documents
    }
    return render(request, 'document-list.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

"""class GoogleLoginView(View):
    def get(self, request):
        # Handle the Google login process here
        # Authenticate the user using the access token or any other necessary steps

        # Assuming the user is authenticated successfully, you can log them in
        user = request.user  # Replace this with your user object
        login(request, user)

        return HttpResponseRedirect('home')  # Replace 'home' with your desired redirect URL"""