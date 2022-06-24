from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from .models import menu, OrderModel
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
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

            user = auth.authenticate(username=request.POST.get('username'),password=request.POST.get('password1'), 
                first_name=request.POST.get('first_name'), last_name=request.POST.get('last_name'))

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
    cart = request.session.get('cart',{})

    if quantity > 0:
        cart[id] = quantity
    
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required(login_url="/login/")
def remove_item(request,id):
    cart = request.session.get('cart',{})
    cart.pop(str(id))
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required(login_url="/login/")
def purchase_complete(request):
    cart = request.session.get('cart',{})
    firstname = request.user.first_name
    lastname = request.user.last_name
    email = request.user.email
    street = request.POST.get('street')
    city = request.POST.get('city')
    state = request.POST.get('state')
    zip_code = request.POST.get('zip')
    phone = request.POST.get('phone')
    username = request.user.get_username()

    total = 0
    item_ids= []
    for id, quantity in cart.items():
        item_ids.append(id)
        product = get_object_or_404(menu, pk=id)
        total = total + int(quantity)*product.price

    order = OrderModel.objects.create(
        price=total,
        firstname=firstname,
        lastname=lastname,
        username = username,
        email=email,
        street=street,
        city=city,
        state=state,
        zip_code=zip_code,
        phone=phone,
    )
    order.items.add(*item_ids)
    messages.success(request,"Purchase completed!")

    #sending a confirmation email
    body = ('Thank you for your order! Your food is being made and will be delivered soon!\n'
                f'Your total: $ {total}\n'
                'Thank you again for your order!')

    send_mail(
        'Thank You For Your Order!',
        body,
        'no_reply_coffeeblend@gmail.com',
        [email],
        fail_silently=False
    )

    request.session['cart'] = {}
    return redirect(reverse('index'))
