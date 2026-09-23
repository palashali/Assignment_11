from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import owner_required, property_owner_required
from .models import Property, Favorite
from .forms import PropertyForm, PropertyFilterForm
from rentals.forms import RentalRequestForm
from rentals.models import RentalRequest
from reviews.forms import ReviewForm
from reviews.models import Review


def property_list_view(request):
    """
    Public Property Listing Page with Search, Filtering, and Pagination.
    """
    properties = Property.objects.filter(is_available=True)
    filter_form = PropertyFilterForm(request.GET or None)

    q = request.GET.get('q', '').strip()
    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q)
        )

    property_type = request.GET.get('property_type')
    if property_type:
        properties = properties.filter(property_type=property_type)

    min_rent = request.GET.get('min_rent')
    if min_rent:
        try:
            properties = properties.filter(rent__gte=float(min_rent))
        except ValueError:
            pass

    max_rent = request.GET.get('max_rent')
    if max_rent:
        try:
            properties = properties.filter(rent__lte=float(max_rent))
        except ValueError:
            pass

    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        try:
            properties = properties.filter(bedrooms__gte=int(bedrooms))
        except ValueError:
            pass

    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['-created_at', 'rent', '-rent', 'title']:
        properties = properties.order_by(sort_by)
    else:
        properties = properties.order_by('-created_at')

    # Pagination (6 properties per page)
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Favorite IDs for current user to show active heart icons
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'user_favorites': user_favorites,
        'total_count': properties.count(),
    }
    return render(request, 'properties/property_list.html', context)


def property_detail_view(request, pk):
    """
    Property Details Page showing detailed attributes, owner info, reviews,
    and actions (rental request, review submission, favorite).
    """
    property_obj = get_object_or_404(Property.objects.select_related('owner'), pk=pk)
    reviews = property_obj.reviews.select_related('tenant').all()

    is_favorited = False
    has_pending_request = False
    has_accepted_request = False
    has_reviewed = False
    can_request = False
    can_review = False

    rental_form = RentalRequestForm()
    review_form = ReviewForm()

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, property=property_obj).exists()

        if request.user.is_tenant and request.user != property_obj.owner:
            has_pending_request = RentalRequest.objects.filter(
                property=property_obj,
                tenant=request.user,
                status=RentalRequest.STATUS_PENDING
            ).exists()

            has_accepted_request = RentalRequest.objects.filter(
                property=property_obj,
                tenant=request.user,
                status=RentalRequest.STATUS_ACCEPTED
            ).exists()

            has_reviewed = Review.objects.filter(
                property=property_obj,
                tenant=request.user
            ).exists()

            can_request = property_obj.is_available and not has_pending_request
            can_review = has_accepted_request and not has_reviewed

    context = {
        'property': property_obj,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'has_pending_request': has_pending_request,
        'has_accepted_request': has_accepted_request,
        'has_reviewed': has_reviewed,
        'can_request': can_request,
        'can_review': can_review,
        'rental_form': rental_form,
        'review_form': review_form,
    }
    return render(request, 'properties/property_detail.html', context)


@owner_required
def property_create_view(request):
    """
    Owner adds a new property listing.
    """
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            messages.success(request, f'Property "{prop.title}" was listed successfully!')
            return redirect('properties:property_detail', pk=prop.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PropertyForm()

    return render(request, 'properties/property_form.html', {
        'form': form,
        'title': 'Add New Property Listing',
        'button_text': 'Publish Property'
    })


@property_owner_required
def property_update_view(request, pk):
    """
    Owner updates their existing property listing.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Property "{property_obj.title}" was updated successfully!')
            return redirect('properties:property_detail', pk=property_obj.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'property': property_obj,
        'title': f'Edit "{property_obj.title}"',
        'button_text': 'Save Changes'
    })


@property_owner_required
def property_delete_view(request, pk):
    """
    Owner deletes their existing property listing.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        title = property_obj.title
        property_obj.delete()
        messages.success(request, f'Property "{title}" was permanently deleted.')
        return redirect('rentals:owner_dashboard')

    return render(request, 'properties/property_confirm_delete.html', {'property': property_obj})


@property_owner_required
def toggle_availability_view(request, pk):
    """
    Quickly toggle availability status of a property from the owner dashboard.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property_obj.is_available = not property_obj.is_available
        property_obj.save()
        status_text = "Available" if property_obj.is_available else "Not Available"
        messages.success(request, f'Property status updated to "{status_text}".')
    return redirect('rentals:owner_dashboard')


@login_required
def toggle_favorite_view(request, pk):
    """
    Toggle saving/favoriting a property for a tenant or user.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    favorite = Favorite.objects.filter(user=request.user, property=property_obj).first()

    if favorite:
        favorite.delete()
        messages.info(request, f'Removed "{property_obj.title}" from your favorites.')
    else:
        Favorite.objects.create(user=request.user, property=property_obj)
        messages.success(request, f'Saved "{property_obj.title}" to your favorites!')

    next_url = request.META.get('HTTP_REFERER') or property_obj.get_absolute_url()
    return redirect(next_url)


@login_required
def my_favorites_view(request):
    """
    Display all properties favorited by the logged in user.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('property', 'property__owner')
    return render(request, 'properties/my_favorites.html', {'favorites': favorites})
