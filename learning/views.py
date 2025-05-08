from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm
from .models import Utilisateur

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            current_site = get_current_site(request)
            mail_subject = 'Activer votre compte Knowledge Learning'
            message = render_to_string('registration/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'registration/activation_sent.html')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'registration/activation_invalid.html')

def user_logout(request):
    logout(request)
    return redirect('home')

# Vues pour Stripe
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cursus, Lesson, Purchase

# Configurer Stripe avec la clé secrète
stripe.api_key = settings.STRIPE_SECRET_KEY

# learning/views.py
@login_required
def buy_cursus(request, cursus_id):
    cursus = get_object_or_404(Cursus, id=cursus_id)
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour effectuer un achat.")
        return redirect('home')

    if request.method == 'POST':
        try:
            print("Création de la session Stripe...")
            print(f"Clé secrète Stripe : {settings.STRIPE_SECRET_KEY}")  # Vérifie que la clé est bien lue
            print(f"Prix du cursus : {cursus.price}, après conversion : {int(cursus.price * 100)}")
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': cursus.name,
                        },
                        'unit_amount': int(cursus.price * 100),  # Montant en centimes
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            print(f"Session Stripe créée : {session.url}")
            Purchase.objects.create(
                utilisateur=request.user,
                cursus=cursus,
                amount=cursus.price,
                created_by=request.user.username,
                updated_by=request.user.username
            )
            return redirect(session.url, code=303)
        except Exception as e:
            print(f"Erreur lors de la création de la session Stripe : {str(e)}")  # Ajoute ce log
            messages.error(request, f"Erreur lors du paiement : {str(e)}")
            return redirect('home')

    return render(request, 'buy_cursus.html', {'cursus': cursus})

@login_required
def buy_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour effectuer un achat.")
        return redirect('home')

    if request.method == 'POST':
        try:
            print("Création de la session Stripe...")
            print(f"Clé secrète Stripe : {settings.STRIPE_SECRET_KEY}")
            print(f"Prix de la leçon : {lesson.price}, après conversion : {int(lesson.price * 100)}")
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': lesson.title,
                        },
                        'unit_amount': int(lesson.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            print(f"Session Stripe créée : {session.url}")
            Purchase.objects.create(
                utilisateur=request.user,
                lesson=lesson,
                amount=lesson.price,
                created_by=request.user.username,
                updated_by=request.user.username
            )
            return redirect(session.url, code=303)
        except Exception as e:
            print(f"Erreur lors de la création de la session Stripe : {str(e)}")
            messages.error(request, f"Erreur lors du paiement : {str(e)}")
            return redirect('home')

    return render(request, 'buy_lesson.html', {'lesson': lesson})

def payment_success(request):
    messages.success(request, "Paiement réussi ! Vous avez maintenant accès à votre contenu.")
    return redirect('home')

def payment_cancel(request):
    messages.error(request, "Paiement annulé.")
    return redirect('home')