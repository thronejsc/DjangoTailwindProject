from django.db import models
from django.urls import reverse
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.files.base import ContentFile

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email
        and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class MyUser(AbstractBaseUser):
    name = models.CharField(max_length=100)
    username = models.CharField(default="", max_length=100)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    USER_TYPE_CHOICES = (
    ('STUDENT', 'student'),
    ('PUBLISHER', 'publisher'),
    )
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=64, default='student')
    bio = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_student(self):
        return self.user_type=="STUDENT"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# Main models starts here - ---------------

STAGE_UNSUBMITTED = 'Unsubmitted'
STAGE_UNDER_REVIEW = 'Under Review'
STAGE_UNDER_REVISION = 'Under Revision'
STAGE_REJECTED = 'Rejected'
STAGE_ACCEPTED = 'Accepted'
STAGE_TYPESETTING = 'Typesetting'
STAGE_READY_FOR_PUBLICATION = 'pre_publication'
STAGE_PUBLISHED = 'Published'
STAGE_CHOICES = [
    (STAGE_UNSUBMITTED, 'Unsubmitted'),
    (STAGE_UNDER_REVIEW, 'Peer Review'),
    (STAGE_UNDER_REVISION, 'Revision'),
    (STAGE_REJECTED, 'Rejected'),
    (STAGE_ACCEPTED, 'Accepted'),
    (STAGE_TYPESETTING, 'Typesetting'),
    (STAGE_READY_FOR_PUBLICATION, 'Pre Publication'),
    (STAGE_PUBLISHED, 'Published'),
]


class Keyword(models.Model):
    word = models.CharField(max_length=200)

    def __str__(self):
        return self.word


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Journal(models.Model):
    code = models.CharField(max_length=300, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    j_image = models.ImageField(upload_to='j_images', height_field=None, width_field=None,)
    description = models.TextField(null=True, blank=True, verbose_name="Journal Description")
    keywords = models.ManyToManyField(Keyword, blank=True)

    class Meta:
        pass

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return f"/profiles/journal/{self.id}"


class Article(models.Model):
    volume = models.IntegerField(default=1)
    issue = models.IntegerField(default=1)
    issue_title = models.CharField(blank=True, max_length=300)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=500)
    student = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    abstract = models.TextField()
    text = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=15, choices=STAGE_CHOICES, default=STAGE_UNSUBMITTED)
    published_at = models.DateTimeField(null=True)
    keywords = models.ManyToManyField(Keyword, related_name="keywords")

    def get_absolute_url(self):
        return f"/profiles/article/{self.id}"


class EditorNote(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='Editornotes')
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text

    def __str__(self):
        return "Article {article_pk} note at {created_at}".format(article_pk=self.article.pk,
                                                                    created_at=self.created_at)

class DatabaseStorage(models.FileField):
    def _save(self, name, content):
        self.name = self.generate_filename(self.instance, name)
        self.instance.file = self.name
        self.instance.file.save(name, ContentFile(content))
    
    def generate_filename(self, instance, filename):
        return filename



class Document(models.Model):
    title = models.CharField(default = '', max_length=255)
    subject = models.CharField(max_length=100)
    year_level = models.PositiveIntegerField()
    file = models.FileField(upload_to='')
    brief_info = models.CharField(default='', max_length=255)
    embedded_url = models.URLField(blank=True)
    uploader = models.ForeignKey(MyUser, on_delete=models.CASCADE, default=12)


    def __str__(self):
        return self.file.name

    def get_file_content(self):
        with open(self.file.path, 'rb') as file:
            content = file.read()
        return content
    
    def get_absolute_url(self):
        return f"/profiles/document/{self.id}/"


    def get_description(self):
        return f"Subject: {self.subject}\n, Year Level: {self.year_level}\n, Brief Info: {self.brief_info}\n, (Uploaded By:{self.uploader})"
    

class Comment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.email} on {self.document.subject}'

