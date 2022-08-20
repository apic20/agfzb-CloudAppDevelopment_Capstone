from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import get_dealers_from_cf, post_request, get_dealer_reviews_from_cf,get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html',context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html',context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('/djangoapp/')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://741d5822.us-south.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://741d5822.us-south.apigw.appdomain.cloud/api/dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id)
        context["dealer"] = dealer

        review_url = "https://741d5822.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(review_url, id)
        print(reviews)
        context["reviews"] = reviews

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, id):
    context = {}
    dealer_id = id
    dealer_url = "https://741d5822.us-south.apigw.appdomain.cloud/api/dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
    context["dealer"] = dealer
    if request.method == 'GET':
        cars = CarModel.objects.all()
        print(cars)
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            review_data = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review_data["time"] = datetime.utcnow().isoformat()
            review_data["name"] = username
            review_data["dealership"] = id
            review_data["id"] = id
            review_data["review"] = request.POST["content"]
            review_data["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    review_data["purchase"] = True
            review_data["purchase_date"] = request.POST["purchasedate"]
            review_data["car_make"] = car.make.name
            review_data["car_model"] = car.name
            review_data["car_year"] = int(car.year.strftime("%Y"))

            review_post = {}
            review_post["review"] = review_data
            review_post_url = "https://741d5822.us-south.apigw.appdomain.cloud/api/review"
            post_request(review_post_url, review_post, id=dealer_id)
        return redirect("djangoapp:dealer_details", id=dealer_id)


