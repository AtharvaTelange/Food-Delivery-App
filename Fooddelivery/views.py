from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from .models import menu
from django.contrib import auth, messages
from django.template.context_processors import csrf
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
	return render(request,'Fooddelivery/index.html')

@login_required(login_url="/login/")
def logout(request):
    """A view that logs the user out and redirects back to the index page"""
    auth.logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect(reverse('index'))

def login(request):
    """A view that manages the login form"""
    if request.method == 'POST':
        user_form = UserLoginForm(request.POST)

        if user_form.is_valid():
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

            if user is not None:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")

                if request.GET and request.GET['next'] !='':
                    next = request.GET['next']
                    return HttpResponseRedirect(next)
                else:
                    return redirect(reverse('index'))

            else:
                user_form.add_error(None, "Your username or password are incorrect")
    else:
        user_form = UserLoginForm()

    args = {'user_form': user_form, 'next': request.GET.get('next', '')}
    return render(request, 'Fooddelivery/login.html', args)

def register(request):
    """A view that manages the registration form"""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            user_form.save()

            user = auth.authenticate(username=request.POST.get('username'),password=request.POST.get('password1'))

            if user is not None:
                auth.login(request, user)
                messages.success(request, "You have successfully registered")
                return redirect(reverse('index'))
            else:
                messages.error(request, "Unable to log you in at this time!")

    else:
        user_form = UserRegistrationForm()

    args = {'user_form': user_form}
    return render(request, 'Fooddelivery/register.html', args)

@login_required(login_url="/login/")
def cart(request):
	return render(request,'Fooddelivery/cart.html')

@login_required(login_url="/login/")
def checkout(request):
	return render(request,'Fooddelivery/checkout.html')

@login_required(login_url="/login/")
def shop(request):
	content = {
		'products' : menu.objects.all(),
	}
	return render(request,'Fooddelivery/shop.html', content)

@login_required(login_url="/login/")
def add_to_cart(request, id):
    """Add a quantity of the specified product to the cart"""
    quantity = int(request.POST.get('quantity'))

    cart = request.session.get('cart',{})
    cart[id] = cart.get(id,quantity)

    request.session['cart'] = cart
    return redirect(reverse('shop'))

@login_required(login_url="/login/")
def adjust_cart(request, id):
    """
    Adjust the quantity of the specified product to the specified
    amount
    """
    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', {})

    if quantity > 0:
        cart[id] = quantity
    
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required(login_url="/login/")
def remove_item(request,id):
    cart = request.session.get('cart', {})
    cart.pop(str(id))
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required(login_url="/login/")
def purchase_complete(request):

    cart = request.session.get('cart', {})
    cart = {}
    total = 0
    product_count = 0
    discount = 0
    net = 0
    request.session['cart'] = cart
    messages.success(request,"Purchase completed!")
    return redirect(reverse('index'),{'product_count':product_count, 'total':total, 'discount':discount,'net':net})
