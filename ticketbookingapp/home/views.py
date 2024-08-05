
import logging
import json
import razorpay
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Cart, CartItems
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home(request):
    movies = Movie.objects.all()
    context = {'movies': movies}
    return render(request, "home.html", context)

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')
        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect('login')
    return render(request, "login.html")

def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is taken")
                return redirect('register')
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()
            messages.success(request, "Account created successfully")
            return redirect('login')
        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect('register')
    return render(request, "register.html")

@login_required(login_url='login')
def add_cart(request, movie_uid):
    user = request.user
    try:
        movie = Movie.objects.get(uid=movie_uid)
        logger.info(f"Movie found: {movie.movie_name}")
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        logger.info(f"Cart found or created: {cart.uid}, created: {created}")
        CartItems.objects.create(cart=cart, movie=movie)
        logger.info(f"Movie {movie.movie_name} added to cart {cart.uid}")
        messages.success(request, "Movie added to cart successfully")
    except Movie.DoesNotExist:
        logger.error(f"Movie with UID {movie_uid} not found")
        messages.error(request, "Movie not found")
    except Exception as e:
        logger.error(f"Error adding movie to cart: {str(e)}")
        messages.error(request, "Something went wrong")
    return redirect('/')

@login_required(login_url='login')
def cart(request):
    try:
        cart = Cart.objects.get(is_paid=False, user=request.user)
        context = {'carts': cart}
        return render(request, "cart.html", context)
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found")
        return redirect('/')

@login_required(login_url='login')
def remove_cart_item(request, cart_item_uid):
    try:
        CartItems.objects.get(uid=cart_item_uid).delete()
        return redirect('cart')
    except CartItems.DoesNotExist:
        messages.error(request, "Cart item not found")
        return redirect('cart')

def user_logout(request):
    logout(request)
    return redirect('home')

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_item_uid = data.get('cart_item_id', '')

        # Validate the UUID
        try:
            cart_item_uid = uuid.UUID(cart_item_uid)
        except (ValueError, TypeError):
            logger.error(f"Invalid UUID: {cart_item_uid}")
            return JsonResponse({'error': 'Invalid cart item ID'}, status=400)

        try:
            cart_item = CartItems.objects.get(uid=cart_item_uid)
            amount = int(cart_item.movie.price * 100)  # Amount in paise
            order = client.order.create(dict(
                amount=amount,
                currency='INR',
                payment_capture='1'
            ))
            return JsonResponse({'id': order['id'], 'amount': order['amount']})
        except CartItems.DoesNotExist:
            logger.error(f"Cart item with UID {cart_item_uid} not found")
            return JsonResponse({'error': 'Cart item not found'}, status=404)
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return JsonResponse({'error': 'Error creating order'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_item_uid = data.get('cart_item_id')
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')

        # Validate the UUID
        try:
            cart_item_uid = uuid.UUID(cart_item_uid)
        except (ValueError, TypeError):
            logger.error(f"Invalid UUID: {cart_item_uid}")
            return JsonResponse({'error': 'Invalid cart item ID'}, status=400)

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            # Update cart item status here if needed
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
