from django.db import models
import re, bcrypt
from datetime import datetime, date
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
    def register(self, postData):
        valid = {
            "is_valid": True,
            "user": None,
            "errors": {}
        }
        print(valid)

        # validations
        if len(postData['name']) < 1:
            valid['errors']['name'] = "... is required!"
        elif len(postData['name']) < 2:
            valid['errors']['name'] = "Name must be at least 2 characters."

        if len(postData['alias']) < 1:
            valid['errors']['alias'] = "... required!"
        elif len(postData['alias']) < 2:
            valid['errors']['alias'] = "Alias must be at least 2 characters"

        if len(postData['email']) < 1:
            valid['errors']['email'] = "... is required!"
        elif not EMAIL_REGEX.match(postData['email']):
            valid['errors']['email'] = "Invalid email."
        else:
            valid['user'] = User.objects.filter(email=postData['email'].lower())
            if len(valid['user']) > 0:
                valid['errors']['email'] = "Email already exists."
        
        if len(postData['dob']) < 1:
            valid['errors']['dob'] = "... is required!"
        else:
            dob = datetime.strptime(postData['dob'], "%Y-%M-%d")
            if dob > datetime.now():
                valid['errors']['dob'] = "Date of birth must be in the past."

        if len(postData['password']) < 1:
            valid['errors']['password'] = "... is required!"
        elif len(postData['password']) < 8:
            valid['errors']['password'] = "Password must be at least 8 characters."

        if len(postData['password_confirm']) < 1:
            valid['errors']['password_confirm'] = "... is required!"
        elif postData['password'] != postData['password_confirm']:
            valid['errors']['password_confirm'] = "Password must match Password Confirmation."
        
        if len(valid['errors']) == 0:
            valid['user'] = User.objects.create(
                name=postData['name'],
                alias=postData['alias'],
                email=postData['email'],
                dob=postData['dob'],
                password=bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()).decode()
            )
        else:
            valid['is_valid'] = False

        return valid


    def login(self, postData):
        valid = {
            'is_valid': True,
            'user': None,
            'errors': {} 
        }

        # validations
        if len(postData['email']) < 1:
            valid['errors']['email'] = "... is required!"
        elif not EMAIL_REGEX.match(postData['email']):
            valid['errors']['email'] = "Invalid email."
        else:
            valid['user'] = User.objects.filter(email=postData['email'].lower())
            if len(valid['user']) == 0:
                valid['errors']['email'] = "Unknown email."
        
        if len(postData['password']) < 1:
            valid['errors']['password'] = "... is required!"
        
        if len(valid['errors']) == 0:
            valid['user'] = valid['user'][0]

            check = bcrypt.checkpw(postData['password'].encode(), valid['user'].password.encode())

            if not check:
                valid["is_valid"] = False
                valid['errors']['password'] = "Invalid login information."

        return valid


class User(models.Model):
    name = models.CharField(max_length=45)
    alias = models.CharField(max_length=45)
    email = models.CharField(max_length=255)
    dob = models.DateField()
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()


class QuoteManager(models.Manager):
    def add(self, postData, uid):
        errors = []
        if len(postData['attribution']) < 1:
            errors.append('Attribution is required.')
        elif len(postData['attribution']) < 4:
            errors.append('Attribution must be more than 3 characters.')
        if len(postData['message']) < 1:
            errors.append('Message is required.')
        elif len(postData['message']) < 11:
            errors.append('Message must be more than 10 characters.')

        matches = Quote.objects.filter(attribution=postData['attribution']).filter(message=postData['message'])
        if len(matches) > 0:
            errors.append("Quote already exists.")
        if len(errors) == 0:
            return Quote.objects.create(attribution=postData['attribution'], message=postData['message'], poster_id=uid)
        else:
            return errors


class Quote(models.Model):
    attribution = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    poster = models.ForeignKey(User, related_name="quotes", on_delete=models.CASCADE)
    favorites = models.ManyToManyField(User, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuoteManager()