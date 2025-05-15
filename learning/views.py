"""Views for the Knowledge Learning application.

This module contains the views for handling user registration, authentication,
purchases, lesson validation, and certifications.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
import stripe
from .forms import RegistrationForm
from .models import Utilisateur, Cursus, Lesson, Purchase, Validation, Certification, Theme


def register(request):
    """Handle user registration and send activation email.

    Displays a registration form and, upon successful submission, creates a new user
    and sends an activation email to the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered registration form or activation sent page.
    """
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
    """Activate user account via email link.

    Verifies the activation token and activates the user account if valid.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): Base64-encoded user ID.
        token (str): Activation token.

    Returns:
        HttpResponse: Redirect to home or invalid activation page.
    """
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
    return render(request, 'registration/activation_invalid.html')


def user_logout(request):
    """Log out the user and redirect to home.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirect to the home page.
    """
    logout(request)
    return redirect('home')


# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def buy_cursus(request, cursus_id):
    """Handle the purchase of a cursus via Stripe.

    Allows a user to purchase a cursus, redirecting to Stripe for payment.

    Args:
        request (HttpRequest): The HTTP request object.
        cursus_id (int): The ID of the cursus to purchase.

    Returns:
        HttpResponse: Redirect to Stripe or render the purchase page.
    """
    cursus = get_object_or_404(Cursus, id=cursus_id)
    if not request.user.is_active:
        messages.error(request, "Account must be activated to purchase.")
        return redirect('home')

    if Purchase.objects.filter(utilisateur=request.user, cursus=cursus).exists():
        messages.error(request, "Cursus already purchased.")
        return redirect('list_cursuses')

    lessons = Lesson.objects.filter(cursus=cursus)
    purchased_lessons = Purchase.objects.filter(
        utilisateur=request.user,
        lesson__in=lessons
    ).values_list('lesson', flat=True)

    remaining_lessons = lessons.exclude(id__in=purchased_lessons)
    if remaining_lessons.exists() and purchased_lessons.exists():
        adjusted_price = sum(lesson.price for lesson in remaining_lessons)
    else:
        adjusted_price = cursus.price

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
    """Handle the purchase of a lesson via Stripe.

    Allows a user to purchase a lesson, redirecting to Stripe for payment.

    Args:
        request (HttpRequest): The HTTP request object.
        lesson_id (int): The ID of the lesson to purchase.

    Returns:
        HttpResponse: Redirect to Stripe or render the purchase page.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Account must be activated to purchase.")
        return redirect('home')

    if Purchase.objects.filter(utilisateur=request.user, lesson=lesson).exists():
        messages.error(request, "Lesson already purchased.")
        return redirect('list_cursuses')

    if Purchase.objects.filter(utilisateur=request.user, cursus=lesson.cursus).exists():
        messages.error(request, "Cursus containing this lesson already purchased.")
        return redirect('list_cursuses')

    if request.method == 'POST':
        try:
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
            request.session['stripe_session_id'] = session.id
            request.session['pending_purchase'] = {'type': 'lesson', 'id': lesson_id}
            return redirect(session.url, code=303)
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('home')

    return render(request, 'buy_lesson.html', {'lesson': lesson})


def payment_success(request):
    """Handle successful payment after Stripe redirection.

    Processes a successful payment and creates a purchase record.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirect to the home page with a success message.
    """
    session_id = request.session.get('stripe_session_id')
    pending_purchase = request.session.get('pending_purchase')

    if not session_id or not pending_purchase:
        messages.error(request, "Aucune session de paiement ou achat en attente trouvé.")
        return redirect('home')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != 'paid':
            messages.error(request, "Le paiement n'a pas été finalisé.")
            return redirect('home')

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
                messages.info(request, "Leçon déjà achetée.")
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
                messages.info(request, "Cursus déjà acheté.")
        else:
            messages.error(request, "Type d'achat invalide.")
            return redirect('home')

    except stripe.error.StripeError as e:
        messages.error(request, f"Erreur de vérification du paiement : {str(e)}")
        return redirect('home')

    request.session.pop('stripe_session_id', None)
    request.session.pop('pending_purchase', None)
    return redirect('home')


def payment_cancel(request):
    """Handle payment cancellation after Stripe redirection.

    Displays a cancellation message and redirects to home.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirect to the home page with a cancellation message.
    """
    messages.error(request, "Paiement annulé. Aucun achat enregistré.")
    return redirect('home')


@login_required
def view_lesson(request, lesson_id):
    """Display a lesson and allow marking it as completed.

    Args:
        request (HttpRequest): The HTTP request object.
        lesson_id (int): The ID of the lesson to view.

    Returns:
        HttpResponse: Rendered lesson page or redirect after marking as completed.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Account must be activated to access a lesson.")
        return redirect('home')

    has_access = Purchase.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists() or Purchase.objects.filter(
        utilisateur=request.user,
        cursus=lesson.cursus
    ).exists()

    if not has_access:
        messages.error(request, "Purchase this lesson or its cursus to access it.")
        return redirect('home')

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
            messages.success(request, "Lesson marked as completed! You can now validate it.")
        return redirect('view_lesson', lesson_id=lesson.id)

    return render(request, 'view_lesson.html', {'lesson': lesson, 'is_completed': is_completed})


@login_required
def validate_lesson(request, lesson_id):
    """Validate a lesson and check for theme certification.

    Args:
        request (HttpRequest): The HTTP request object.
        lesson_id (int): The ID of the lesson to validate.

    Returns:
        HttpResponse: Redirect to home or render validation page.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not request.user.is_active:
        messages.error(request, "Account must be activated to validate a lesson.")
        return redirect('home')

    has_access = Purchase.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists() or Purchase.objects.filter(
        utilisateur=request.user,
        cursus=lesson.cursus
    ).exists()

    if not has_access:
        messages.error(request, "Purchase this lesson or its cursus to validate it.")
        return redirect('home')

    is_completed = Validation.objects.filter(
        utilisateur=request.user,
        lesson=lesson
    ).exists()

    if not is_completed:
        messages.error(request, "Mark the lesson as completed before validating it.")
        return redirect('view_lesson', lesson_id=lesson.id)

    if request.method == 'POST':
        cursus = lesson.cursus
        all_lessons_in_cursus = Lesson.objects.filter(cursus=cursus)
        validated_lessons_in_cursus = Validation.objects.filter(
            utilisateur=request.user,
            lesson__cursus=cursus
        ).values_list('lesson', flat=True).distinct()

        if set(all_lessons_in_cursus.values_list('id', flat=True)) == set(validated_lessons_in_cursus):
            messages.success(request, f"Cursus {cursus.name} validated successfully!")

        theme = cursus.theme
        all_lessons_in_theme = Lesson.objects.filter(cursus__theme=theme)
        validated_lessons_in_theme = Validation.objects.filter(
            utilisateur=request.user,
            lesson__cursus__theme=theme
        ).values_list('lesson', flat=True).distinct()

        if set(all_lessons_in_theme.values_list('id', flat=True)) == set(validated_lessons_in_theme):
            Certification.objects.get_or_create(
                utilisateur=request.user,
                theme=theme,
                defaults={
                    'created_by': request.user.username,
                    'updated_by': request.user.username
                }
            )
            messages.success(request, f"Congratulations! Certification earned for theme {theme.name}.")
        else:
            messages.success(request, f"Lesson {lesson.title} validated successfully.")

        return redirect('home')

    return render(request, 'validate_lesson.html', {'lesson': lesson})


@login_required
def list_certifications(request):
    """List certifications earned by the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered certifications page.
    """
    if not request.user.is_active:
        messages.error(request, "Account must be activated to view certifications.")
        return redirect('home')

    certifications = Certification.objects.filter(utilisateur=request.user)
    return render(request, 'list_certifications.html', {'certifications': certifications})


def list_cursuses(request):
    """List all available cursus for browsing and purchase.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered cursus list page.
    """
    themes = Theme.objects.all()
    themes_data = []

    for theme in themes:
        cursuses = Cursus.objects.filter(theme=theme)
        cursuses_data = []

        for cursus in cursuses:
            lessons = Lesson.objects.filter(cursus=cursus)
            purchased_lessons = Purchase.objects.filter(
                utilisateur=request.user if request.user.is_authenticated else None,
                lesson__in=lessons
            ).values_list('lesson', flat=True)
            has_purchased_cursus = Purchase.objects.filter(
                utilisateur=request.user if request.user.is_authenticated else None,
                cursus=cursus
            ).exists()
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

            lessons_data = []
            for idx, lesson in enumerate(lessons, start=1):
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'price': lesson.price,
                    'is_purchased': lesson.id in purchased_lessons,
                    'index': idx
                })

            cursuses_data.append({
                'cursus': cursus,
                'adjusted_price': adjusted_price,
                'has_purchased_cursus': has_purchased_cursus,
                'lessons': lessons_data,
            })

        themes_data.append({
            'theme': theme,
            'cursuses': cursuses_data,
        })

    return render(request, 'list_cursuses.html', {'themes_data': themes_data})