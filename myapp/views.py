from random import randint
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django import forms
from datetime import datetime
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Publisher, Book, Member, Order, Review
from .forms import SearchForm, OrderForm, ReviewForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def index(request):
    if 'last_login' in request.session:
        last_login = request.session['last_login']
    else:
        last_login = "Your last login was more than one hour ago!!"
    username = request.user.username
    booklist = Book.objects.all().order_by('id')[:10]
    return render(request, 'myapp/index.html', {'booklist': booklist, 'username':username, 'last_login':last_login})

def about(request):
    response = HttpResponse()
    if 'number' in request.COOKIES:
        mynum = request.COOKIES['number']
    else:
        mynum = randint(1, 100)
        response.set_cookie('number', mynum, 30)
    lucky_number = render_to_string('myapp/about.html', {'mynum': mynum})
    response.write(lucky_number)
    return response

def detail(request, book_id):
    book_Detail = get_object_or_404(Book, id=book_id)
    return render(request, 'myapp/detail.html', {'book_title': book_Detail.title.upper(), 'book_price': book_Detail.price, 'book_publisher':book_Detail.publisher, 'book_id': book_id})

def findbooks(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            categoryName =''
            name = form.cleaned_data['your_name']
            category = form.cleaned_data['Select_category']
            max_price = form.cleaned_data['Maximum_Price']
            booklist = Book.objects.filter(price__lte=max_price)
            if category:
                booklist = booklist.filter(category=category)
                categoryName = dict(form.fields['Select_category'].choices)[category]
            return render(request, 'myapp/results.html', {'booklist':booklist, 'name':name, 'category':categoryName})
        else:
            return HttpResponse('Invalid data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findbooks.html', {'form':form})

def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            books = form.cleaned_data['books']
            order = form.save(commit=True)
            member = order.member
            type = order.order_type
            order.save()
            if type == 1:
                for b in order.books.all():
                    member.borrowed_books.add(b)
            return render(request, 'myapp/order_response.html', {'books': books, 'order':order})
        else:
            return render(request, 'myapp/placeorder.html', {'form':form})

    else:
        form = OrderForm()
        return render(request, 'myapp/placeorder.html', {'form':form})

def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            book = form.cleaned_data['book']
            reviewer = form.cleaned_data['reviewer']
            rating = form.cleaned_data['rating']
            comments = form.cleaned_data['comments']
            try:
                if Member.objects.get(id=request.user.id):  # Option feature: 08
                    if 1 <= rating <= 5 :
                        review.save()
                        book.num_reviews = book.num_reviews + 1
                        book.save(update_fields=['num_reviews'])
                        return index(request)
                    else:
                        return render(request, 'myapp/review.html', {'form':form, 'error':'You must enter a rating between 1 and 5!'})
            except Member.DoesNotExist:
                Member_err = "You are not a registered client"
                return render_to_response('template_name', message='Save complete')

    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form':form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        current_login_time = datetime.now()
        timestamp = current_login_time.strftime("%d-%b-%Y (%H:%M:%S)")
        request.session['last_login'] = 'Last Login: ' + timestamp
        request.session.set_expiry(3600)
        if user:
            if user.is_active:
                login(request, user)
                if request.session.get('bookid'):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '')) #required feature : 4 Go back to chk_reviews
                else:
                    return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(('myapp:index')))

def chk_reviews(request, book_id):
    request.session['bookid'] = book_id #required feature : 4
    try:
        if Member.objects.get(id=request.user.id):
            book = get_object_or_404(Book, id=book_id)
            total = 0
            avg_review = 0
            ratings = Review.objects.filter(book__id=book_id)
            if ratings:
                for r in ratings:
                    rate = r.rating
                    total += rate
                total_no_of_reviews = Book.objects.get(id=book_id).num_reviews
                avg_review = total/total_no_of_reviews
                del request.session['bookid'] #required feature : 4
                return render(request, 'myapp/chk_reviews.html', {'book': book, 'avg_review': avg_review})
            else:
                Rating_err = "There are no reviews as of now"
                return render(request, 'myapp/chk_reviews.html', {'book': book, 'Rating_Err': Rating_err })
        # else:
        #     return HttpResponse("You are not a registered Client")
    except Member.DoesNotExist:
        return render(request, 'myapp/login.html') #Go for the login page



