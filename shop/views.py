from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Product, Category, Comment


def home(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    elif search_query:
        products = Product.objects.filter(title__icontains=search_query)
    else:
        products = Product.objects.all()
    
    cart = request.session.get('cart', {})
    cart_count = 0
    if cart:
        for item in cart.values():
            if isinstance(item, dict) and 'quantity' in item:
                cart_count += item['quantity']
    
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid = str(product_id)
    
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'title': product.title,
            'price': float(product.price),
            'quantity': 1
        }
        
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{product.title} ajouté au panier avec succès !")
    return redirect('home')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for key, item in cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_items.append({
            'id': key,
            'title': item['title'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal
        })
        
    cart_count = sum(item['quantity'] for item in cart_items)
    
    if request.method == 'POST':
        nom_client = request.POST.get('nom')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        payment_method = request.POST.get('payment_method')

        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, f"Félicitations {nom_client}, votre commande a été confirmée avec succès !")
        return redirect('success')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count
    })

def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    return redirect('home')

def add_comment(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        content = request.POST.get('content')
        rating = request.POST.get('rating', 5)
        
        Comment.objects.create(
            product=product, 
            user=request.user, 
            content=content, 
            rating=int(rating)
        )
        messages.success(request, "Votre commentaire a été ajouté avec succès !")
    else:
        messages.error(request, "Vous devez être connecté pour laisser un avis.")
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé et connecté avec succès !")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Ravi de vous revoir, {username} !")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('home')


def success_view(request):
    return render(request, 'success.html')

def contact_view(request):
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_count = 0
    if cart:
        for item in cart.values():
            if isinstance(item, dict) and 'quantity' in item:
                cart_count += item['quantity']

    if request.method == 'POST':
        nom = request.POST.get('nom')
        messages.success(request, f"Merci {nom}, votre message a été envoyé avec succès !")
        return redirect('home')

    return render(request, 'contact.html', {
        'categories': categories,
        'cart_count': cart_count
    })