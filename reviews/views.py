from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import tenant_required
from properties.models import Property
from rentals.models import RentalRequest
from .models import Review
from .forms import ReviewForm


@tenant_required
def add_review_view(request, property_id):
    """
    Allows a tenant to leave a review if they have an accepted rental request for this property.
    Enforces the rule that a tenant can review a property only once.
    """
    property_obj = get_object_or_404(Property, pk=property_id)

    # Check if tenant has an accepted rental request
    has_accepted_request = RentalRequest.objects.filter(
        property=property_obj,
        tenant=request.user,
        status=RentalRequest.STATUS_ACCEPTED
    ).exists()

    if not has_accepted_request:
        messages.error(request, "You can only leave a review for properties where your rental request was accepted.")
        return redirect('properties:property_detail', pk=property_id)

    # Check if tenant already reviewed this property
    already_reviewed = Review.objects.filter(
        property=property_obj,
        tenant=request.user
    ).exists()

    if already_reviewed:
        messages.warning(request, "You have already submitted a review for this property.")
        return redirect('properties:property_detail', pk=property_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property_obj
            review.tenant = request.user
            review.save()
            messages.success(request, f'Thank you for reviewing "{property_obj.title}"!')
            return redirect('properties:property_detail', pk=property_id)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'property': property_obj
    })
