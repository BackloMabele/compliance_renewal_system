from django.db.models import F, ExpressionWrapper, IntegerField, DurationField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Renewal
from .forms import RenewalForm, CustomUserCreationForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        logger.info("Signup form submitted.")  # Debugging step
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  # Save user
                logger.info(f"User {user.username} created successfully.")
                messages.success(request, 'Account created. Awaiting admin approval.')
                return redirect('login')  # Redirect to login page
            except Exception as e:
                logger.error(f"Error saving user: {e}")
                messages.error(request, 'An unexpected error occurred. Please try again.')
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'There was an error with your registration.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'renewals/signup.html', {'form': form})  # Ensure correct template path


@login_required
def bulk_delete_renewals(request):
    # Ensure only superusers can perform bulk delete
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete multiple renewals.")
        return redirect('dashboard')

    if request.method == 'POST':
        selected_renewals = request.POST.getlist('selected_renewals')

        if selected_renewals:
            try:
                selected_ids = [int(renewal_id) for renewal_id in selected_renewals]
                Renewal.objects.filter(pk__in=selected_ids).delete()
                messages.success(request, 'Selected renewals have been deleted.')
            except Exception as e:
                messages.error(request, f'Error deleting renewals: {str(e)}')
        else:
            messages.error(request, 'No renewals were selected for deletion.')

    return redirect('dashboard')

@login_required
def dashboard(request):
    # Search and filter renewals
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')

    today = timezone.now().date()

    # Annotating renewals with calculated remaining days
    renewals = Renewal.objects.annotate(
        calculated_days_remaining=ExpressionWrapper(
            F('expiration_date') - today,
            output_field=DurationField()
        )
    ).annotate(
        calculated_days_remaining_int=ExpressionWrapper(
            F('calculated_days_remaining') / timezone.timedelta(days=1),  
            output_field=IntegerField()
        )
    )

    if query:
        renewals = renewals.filter(Q(renewal_title__icontains=query)).distinct()

    if sort:
        if sort == "days_remaining":
            renewals = renewals.order_by("calculated_days_remaining_int")
        elif sort == "-days_remaining":
            renewals = renewals.order_by("-calculated_days_remaining_int")
        else:
            renewals = renewals.order_by(sort)

    return render(request, 'renewals/dashboard.html', {'renewals': renewals, 'query': query, 'sort': sort})

@login_required
def create_renewal(request):
    if request.method == 'POST':
        form = RenewalForm(request.POST, request.FILES)
        if form.is_valid():
            renewal = form.save(commit=False)
            renewal.user = request.user
            renewal.save()
            form.save_m2m()

            # Store the renewal ID in the session for undo functionality
            request.session['last_created_renewal_id'] = renewal.pk
            request.session['undo_available_until'] = (timezone.now() + timezone.timedelta(seconds=10)).isoformat()

            messages.success(request, 'Renewal created successfully. <a href="#" id="undo-button" class="alert-link">Undo</a>')
            return redirect('dashboard')
    else:
        form = RenewalForm()
    return render(request, 'renewals/create_renewal.html', {'form': form})

@login_required
def undo_create_renewal(request):
    if request.method == 'POST':
        renewal_id = request.session.get('last_created_renewal_id')
        undo_available_until = request.session.get('undo_available_until')

        if renewal_id and undo_available_until and timezone.now() <= timezone.datetime.fromisoformat(undo_available_until):
            renewal = get_object_or_404(Renewal, pk=renewal_id)
            renewal.delete()
            messages.success(request, 'Renewal creation undone.')
        else:
            messages.error(request, 'Undo is no longer available.')
    return redirect('dashboard')

@login_required
def delete_renewal(request, pk):
    renewal = get_object_or_404(Renewal, pk=pk)

    # Ensure only the creator or an admin can delete the renewal
    if request.user.is_superuser or request.user == renewal.user:
        renewal.delete()
        messages.success(request, "Renewal deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this renewal.")

    return redirect('dashboard')

class CustomLoginView(auth_views.LoginView):
    template_name = 'renewals/login.html'
    redirect_authenticated_user = True

@login_required
def renewal_detail(request, pk):
    renewal = get_object_or_404(Renewal, pk=pk)
    return render(request, 'renewals/renewal_detail.html', {'renewal': renewal})

@login_required
def update_renewal(request, pk):
    renewal = get_object_or_404(Renewal, pk=pk)
    if request.method == 'POST':
        form = RenewalForm(request.POST, request.FILES, instance=renewal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Renewal updated successfully.')
            return redirect('renewal_detail', pk=renewal.pk)
    else:
        form = RenewalForm(instance=renewal)
    return render(request, 'renewals/update_renewal.html', {'form': form, 'renewal': renewal})

