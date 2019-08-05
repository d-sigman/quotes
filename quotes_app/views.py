from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from .models import User, Quote

# Create your views here.

def index(request):
    return render(request, "index.html")

def register(request):
    
    check = User.objects.register(request.POST)
    print(check)
    if check['is_valid']:
        request.session['errors'] = {}
        request.session['uid'] = check['user'].id
        return redirect('/dashboard')
    else:
        request.session['errors'] = check['errors']
        return redirect('/')

def login(request):
    try:
        check = User.objects.login(request.POST)
        if check['is_valid']:
            request.session['errors'] = {}
            request.session['uid'] = check['user'].id
            return redirect('/dashboard')
    except:
        request.session['errors'] = "Please try again."
        return redirect('/')

def dashboard(request):
    if 'uid' not in request.session:
        return redirect('/')
    name = User.objects.get(id=request.session['uid']).name
    all_quotes = Quote.objects.all()
    favorites = User.objects.get(id=request.session['uid']).favorites.all()
    others = all_quotes.difference(favorites)

    context = {
        'all_quotes': all_quotes,
        'name': name,
        'others': others,
        'favorites': favorites
    }

    return render(request, 'dashboard.html', context)

def logout(request):
    request.session.clear()
    return redirect('/')

# def new(request):
#     return render(request, 'new.html')

def create(request):
    check = Quote.objects.add(request.POST, request.session['uid'])
    if type(check) == list:
        for error in check:
            messages.add_message(request, messages.ERROR, error)
        return redirect('/dashboard')
    
    else:
        check.favorites.add(User.objects.get(id=request.session['uid']))
        return redirect('/dashboard')

def view_user(request, id):
    poster = User.objects.get(id=id)
    count = Quote.objects.filter(poster=poster).count()
    user = User.objects.get(id=id)
    context = {
        "count": count,
        "user": user
    }
    return render(request, 'view_user.html', context, {'user':User.objects.get(id=id)})

def favorite(request, id):
    quote = Quote.objects.get(id=id)
    quote.favorites.add(User.objects.get(id=request.session['uid']))
    return redirect('/dashboard')

def unfavorite(request, id):
    quote = Quote.objects.get(id=id)
    quote.favorites.remove(User.objects.get(id=request.session['uid']))
    return redirect('/dashboard')

def remove(request, id):
    quote = Quote.objects.get(id=id)
    if quote.poster.id == request.session['uid']:
        quote.delete()
    return redirect('/dashboard')