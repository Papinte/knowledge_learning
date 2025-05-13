from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm
from .models import Utilisateur, Cursus, Lesson, Purchase, Validation, Certification

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

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cursus, Lesson, Purchase

stripe.api_key = settings.STRIPE_SECRET_KEY

# learning/views.py
@login_required
def buy_cursus(request, cursus_id):
    cursus = get_object_or_404(Cursus, id=cursus_id)
    if not request.user.is_active:
        messages.error(request, "Account must be activated to purchase.")
        return redirect('home')

    # Check if user already purchased the cursus
    if Purchase.objects.filter(utilisateur=request.user, cursus=cursus).exists():
        messages.error(request, "Cursus already purchased.")
        return redirect('list_cursuses')

    # Get lessons and check purchased ones
    lessons = Lesson.objects.filter(cursus=cursus)
    purchased_lessons = Purchase.objects.filter(
        utilisateur=request.user,
        lesson__in=lessons
    ).values_list('lesson', flat=True)

    # Set price: use cursus price if no lessons purchased, otherwise sum remaining lessons
    remaining_lessons = lessons.exclude(id__in=purchased_lessons)
    if remaining_lessons.exists() and purchased_lessons.exists():
        adjusted_price = sum(lesson.price for lesson in remaining_lessons)
    else:
        adjusted_price = cursus.price  # Use initial price if no lessons purchased

    if request.method == 'POST':
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': cursus.name,
                        },
                        'unit_amount': int(adjusted_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/success/?cursus_id={cursus_id}'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            request.session['stripe_session_id'] = session.id
            request.session['pending_purchase'] = {'type': 'cursus', 'id': cursus_id}
            return redirect(session.url, code=303)
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('home')

    return render(request, 'buy_cursus.html', {'cursus': cursus, 'adjusted_price': adjusted_price})

@login_required
def buy_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour effectuer un achat.")
        return redirect('home')

    # Check if the user has already purchased the lesson
    if Purchase.objects.filter(utilisateur=request.user, lesson=lesson).exists():
        messages.error(request, "Vous avez déjà acheté cette leçon.")
        return redirect('list_cursuses')

    # Check if the user has already purchased the cursus
    if Purchase.objects.filter(utilisateur=request.user, cursus=lesson.cursus).exists():
        messages.error(request, "Vous avez déjà acheté le cursus contenant cette leçon.")
        return redirect('list_cursuses')

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
                success_url=request.build_absolute_uri(f'/success/?lesson_id={lesson_id}'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            print(f"Session Stripe créée : {session.url}")
            # Stocker l'ID de la session dans la session Django
            request.session['stripe_session_id'] = session.id
            request.session['pending_purchase'] = {'type': 'lesson', 'id': lesson_id}
            return redirect(session.url, code=303)
        except Exception as e:
            print(f"Erreur lors de la création de la session Stripe : {str(e)}")
            messages.error(request, f"Erreur lors du paiement : {str(e)}")
            return redirect('home')

    return render(request, 'buy_lesson.html', {'lesson': lesson})

def payment_success(request):
    session_id = request.session.get('stripe_session_id')
    pending_purchase = request.session.get('pending_purchase')

    if not session_id or not pending_purchase:
        messages.error(request, "Erreur : aucune session de paiement ou achat en attente trouvé.")
        return redirect('home')

    try:
        # Récupérer la session Stripe pour vérifier son statut
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != 'paid':
            messages.error(request, "Le paiement n'a pas été finalisé.")
            return redirect('home')

        # Enregistrer l'achat uniquement si le paiement est confirmé
        if pending_purchase['type'] == 'lesson':
            lesson = get_object_or_404(Lesson, id=pending_purchase['id'])
            if not Purchase.objects.filter(utilisateur=request.user, lesson=lesson).exists():
                Purchase.objects.create(
                    utilisateur=request.user,
                    lesson=lesson,
                    amount=lesson.price,
                    created_by=request.user.username,
                    updated_by=request.user.username
                )
                messages.success(request, f"Paiement réussi ! Vous avez maintenant accès à la leçon {lesson.title}.")
            else:
                messages.info(request, "Vous avez déjà acheté cette leçon.")
        elif pending_purchase['type'] == 'cursus':
            cursus = get_object_or_404(Cursus, id=pending_purchase['id'])
            if not Purchase.objects.filter(utilisateur=request.user, cursus=cursus).exists():
                lessons = Lesson.objects.filter(cursus=cursus)
                purchased_lessons = Purchase.objects.filter(
                    utilisateur=request.user,
                    lesson__in=lessons
                ).values_list('lesson', flat=True)
                remaining_lessons = lessons.exclude(id__in=purchased_lessons)
                adjusted_price = sum(lesson.price for lesson in remaining_lessons) if remaining_lessons.exists() else 0
                Purchase.objects.create(
                    utilisateur=request.user,
                    cursus=cursus,
                    amount=adjusted_price,
                    created_by=request.user.username,
                    updated_by=request.user.username
                )
                messages.success(request, f"Paiement réussi ! Vous avez maintenant accès au cursus {cursus.name}.")
            else:
                messages.info(request, "Vous avez déjà acheté ce cursus.")
        else:
            messages.error(request, "Erreur : type d'achat invalide.")
            return redirect('home')

    except stripe.error.StripeError as e:
        messages.error(request, f"Erreur lors de la vérification du paiement : {str(e)}")
        return redirect('home')

    # Nettoyer la session après l'achat
    request.session.pop('stripe_session_id', None)
    request.session.pop('pending_purchase', None)
    return redirect('home')

def payment_cancel(request):
    messages.error(request, "Paiement annulé. Aucun achat n'a été enregistré.")
    return redirect('home')

@login_required
def view_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour accéder à une leçon.")
        return redirect('home')

    # Vérifier si l'utilisateur a acheté la leçon ou le cursus associé
    has_access = Purchase.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists() or Purchase.objects.filter(
        utilisateur=request.user,
        cursus=lesson.cursus
    ).exists()

    if not has_access:
        messages.error(request, "Vous devez acheter cette leçon ou son cursus pour y accéder.")
        return redirect('home')

    # Vérifier si la leçon a été marquée comme terminée
    is_completed = Validation.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists()

    if request.method == 'POST' and 'mark_completed' in request.POST:
        if not is_completed:
            Validation.objects.get_or_create(
                utilisateur=request.user,
                lesson=lesson,
                defaults={
                    'created_by': request.user.username,
                    'updated_by': request.user.username
                }
            )
            messages.success(request, "Leçon marquée comme terminée ! Vous pouvez maintenant la valider.")
        return redirect('view_lesson', lesson_id=lesson.id)

    return render(request, 'view_lesson.html', {'lesson': lesson, 'is_completed': is_completed})

@login_required
def validate_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour valider une leçon.")
        return redirect('home')

    has_access = Purchase.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists() or Purchase.objects.filter(
        utilisateur=request.user,
        cursus=lesson.cursus
    ).exists()

    if not has_access:
        messages.error(request, "Vous devez acheter cette leçon ou son cursus pour la valider.")
        return redirect('home')

    is_completed = Validation.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists()

    if not is_completed:
        messages.error(request, "Vous devez d'abord marquer la leçon comme terminée avant de la valider.")
        return redirect('view_lesson', lesson_id=lesson.id)

    if request.method == 'POST':
        cursus = lesson.cursus
        all_lessons_in_cursus = Lesson.objects.filter(cursus=cursus)
        validated_lessons_in_cursus = Validation.objects.filter(
            utilisateur=request.user,
            lesson__cursus=cursus
        ).values_list('lesson', flat=True).distinct()

        if set(all_lessons_in_cursus.values_list('id', flat=True)) == set(validated_lessons_in_cursus.values_list('id', flat=True)):
            messages.success(request, f"Le cursus {cursus.name} est validé avec succès !")

        theme = cursus.theme
        all_lessons_in_theme = Lesson.objects.filter(cursus__theme=theme)
        validated_lessons_in_theme = Validation.objects.filter(
            utilisateur=request.user,
            lesson__cursus__theme=theme
        ).values_list('lesson', flat=True).distinct()

        print(f"All lessons in theme {theme.name}: {list(all_lessons_in_theme.values_list('id', flat=True))}")
        print(f"Validated lessons in theme {theme.name}: {list(validated_lessons_in_theme)}")

        if set(all_lessons_in_theme.values_list('id', flat=True)) == set(validated_lessons_in_theme):
            Certification.objects.get_or_create(
                utilisateur=request.user,
                theme=theme,
                defaults={
                    'created_by': request.user.username,
                    'updated_by': request.user.username
                }
            )
            messages.success(request, f"Félicitations ! Vous avez obtenu une certification pour le thème {theme.name}.")
        else:
            messages.success(request, f"La leçon {lesson.title} a été validée avec succès.")

        return redirect('home')

    return render(request, 'validate_lesson.html', {'lesson': lesson})

@login_required
def list_certifications(request):
    if not request.user.is_active:
        messages.error(request, "Vous devez activer votre compte pour voir vos certifications.")
        return redirect('home')

    certifications = Certification.objects.filter(utilisateur=request.user)
    return render(request, 'list_certifications.html', {'certifications': certifications})

def list_cursuses(request):
    cursuses = Cursus.objects.all()
    cursuses_data = []
    for cursus in cursuses:
        # Get all lessons in this cursus
        lessons = Lesson.objects.filter(cursus=cursus)
        # Check which lessons the user has already purchased
        purchased_lessons = Purchase.objects.filter(
            utilisateur=request.user if request.user.is_authenticated else None,
            lesson__in=lessons
        ).values_list('lesson', flat=True)
        # Check if the user has already purchased the cursus
        has_purchased_cursus = Purchase.objects.filter(
            utilisateur=request.user if request.user.is_authenticated else None,
            cursus=cursus
        ).exists()
        # Calculate the adjusted price
        if has_purchased_cursus:
            adjusted_price = 0
        else:
            remaining_lessons = lessons.exclude(id__in=purchased_lessons)
            if remaining_lessons.exists():
                adjusted_price = sum(lesson.price for lesson in remaining_lessons)
            else:
                adjusted_price = 0
                has_purchased_cursus = True
            if not purchased_lessons:
                adjusted_price = cursus.price

        cursuses_data.append({
            'cursus': cursus,
            'adjusted_price': adjusted_price,
            'has_purchased_cursus': has_purchased_cursus,
            'purchased_lessons': purchased_lessons,
        })

    return render(request, 'list_cursuses.html', {'cursuses_data': cursuses_data})