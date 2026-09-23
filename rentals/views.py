from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import owner_required, tenant_required
from properties.models import Property, Favorite
from .models import RentalRequest
from .forms import RentalRequestForm
from reviews.models import Review


@tenant_required
def send_rental_request(request, property_id):
    """
    Handles submission of a rental request from a tenant to a property owner.
    """
    property_obj = get_object_or_404(Property, pk=property_id)

    # Rule: Tenant cannot request their own property
    if property_obj.owner == request.user:
        messages.error(request, "You cannot send a rental request for a property you own.")
        return redirect('properties:property_detail', pk=property_id)

    # Rule: Check property availability
    if not property_obj.is_available:
        messages.error(request, "This property is currently not available for rent.")
        return redirect('properties:property_detail', pk=property_id)

    # Rule: Tenant cannot send multiple pending requests for the same property
    existing_pending = RentalRequest.objects.filter(
        property=property_obj,
        tenant=request.user,
        status=RentalRequest.STATUS_PENDING
    ).exists()

    if existing_pending:
        messages.warning(request, "You already have a pending rental request for this property.")
        return redirect('properties:property_detail', pk=property_id)

    if request.method == 'POST':
        form = RentalRequestForm(request.POST)
        if form.is_valid():
            rental_request = form.save(commit=False)
            rental_request.property = property_obj
            rental_request.tenant = request.user
            rental_request.status = RentalRequest.STATUS_PENDING
            rental_request.save()
            messages.success(request, f'Your rental request for "{property_obj.title}" has been submitted successfully!')
            return redirect('rentals:tenant_dashboard')
        else:
            messages.error(request, "Please provide a valid message for your request.")
    else:
        form = RentalRequestForm()

    return render(request, 'rentals/rental_request_form.html', {
        'form': form,
        'property': property_obj
    })


@login_required
def cancel_rental_request(request, pk):
    """
    Tenant can cancel a pending rental request.
    """
    rental_request = get_object_or_404(RentalRequest, pk=pk)

    if rental_request.tenant != request.user and not request.user.is_superuser:
        raise PermissionDenied("You can only cancel your own rental requests.")

    if rental_request.status != RentalRequest.STATUS_PENDING:
        messages.error(request, f"Cannot cancel a request that is already {rental_request.get_status_display().lower()}.")
        return redirect('rentals:tenant_dashboard')

    if request.method == 'POST':
        rental_request.status = RentalRequest.STATUS_CANCELLED
        rental_request.save()
        messages.success(request, f'Rental request for "{rental_request.property.title}" has been cancelled.')

    return redirect('rentals:tenant_dashboard')


@owner_required
def accept_rental_request(request, pk):
    """
    Property owner accepts a rental request.
    """
    rental_request = get_object_or_404(RentalRequest.objects.select_related('property'), pk=pk)

    if rental_request.property.owner != request.user and not request.user.is_superuser:
        raise PermissionDenied("You can only accept requests for properties you own.")

    if request.method == 'POST':
        rental_request.status = RentalRequest.STATUS_ACCEPTED
        rental_request.save()
        messages.success(
            request,
            f'You accepted the rental request from {rental_request.tenant.get_full_name() or rental_request.tenant.username} for "{rental_request.property.title}".'
        )

    return redirect('rentals:owner_dashboard')


@owner_required
def reject_rental_request(request, pk):
    """
    Property owner rejects a rental request.
    """
    rental_request = get_object_or_404(RentalRequest.objects.select_related('property'), pk=pk)

    if rental_request.property.owner != request.user and not request.user.is_superuser:
        raise PermissionDenied("You can only reject requests for properties you own.")

    if request.method == 'POST':
        rental_request.status = RentalRequest.STATUS_REJECTED
        rental_request.save()
        messages.info(
            request,
            f'You rejected the rental request from {rental_request.tenant.get_full_name() or rental_request.tenant.username} for "{rental_request.property.title}".'
        )

    return redirect('rentals:owner_dashboard')


@owner_required
def owner_dashboard_view(request):
    """
    Dashboard for Property Owners:
    - Total properties
    - Available properties
    - Total rental requests
    - Pending requests
    - Accepted requests
    - Property management list
    - Rental requests management list
    """
    properties = Property.objects.filter(owner=request.user)
    rental_requests = RentalRequest.objects.filter(
        property__owner=request.user
    ).select_related('property', 'tenant')

    # Metrics
    total_properties = properties.count()
    available_properties = properties.filter(is_available=True).count()
    total_requests = rental_requests.count()
    pending_requests = rental_requests.filter(status=RentalRequest.STATUS_PENDING).count()
    accepted_requests = rental_requests.filter(status=RentalRequest.STATUS_ACCEPTED).count()
    rejected_requests = rental_requests.filter(status=RentalRequest.STATUS_REJECTED).count()

    # Filter requests by status if requested via tab/query param
    status_filter = request.GET.get('status')
    if status_filter in [RentalRequest.STATUS_PENDING, RentalRequest.STATUS_ACCEPTED, RentalRequest.STATUS_REJECTED, RentalRequest.STATUS_CANCELLED]:
        filtered_requests = rental_requests.filter(status=status_filter)
    else:
        filtered_requests = rental_requests

    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
        'properties': properties,
        'rental_requests': filtered_requests,
        'status_filter': status_filter or 'ALL',
    }
    return render(request, 'rentals/owner_dashboard.html', context)


@tenant_required
def tenant_dashboard_view(request):
    """
    Dashboard for Tenants:
    - Total rental requests
    - Pending requests
    - Accepted requests
    - Rejected requests
    - Request history with action to cancel pending & review accepted
    - Saved / Favorite properties
    """
    requests_qs = RentalRequest.objects.filter(tenant=request.user).select_related('property', 'property__owner')
    favorites = Favorite.objects.filter(user=request.user).select_related('property', 'property__owner')

    # Metrics
    total_requests = requests_qs.count()
    pending_requests = requests_qs.filter(status=RentalRequest.STATUS_PENDING).count()
    accepted_requests = requests_qs.filter(status=RentalRequest.STATUS_ACCEPTED).count()
    rejected_requests = requests_qs.filter(status=RentalRequest.STATUS_REJECTED).count()
    cancelled_requests = requests_qs.filter(status=RentalRequest.STATUS_CANCELLED).count()

    # Review status map for accepted requests
    reviewed_property_ids = set(Review.objects.filter(tenant=request.user).values_list('property_id', flat=True))

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
        'cancelled_requests': cancelled_requests,
        'rental_requests': requests_qs,
        'favorites': favorites,
        'reviewed_property_ids': reviewed_property_ids,
    }
    return render(request, 'rentals/tenant_dashboard.html', context)
