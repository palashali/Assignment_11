import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont
from properties.models import Property, Favorite
from rentals.models import RentalRequest
from reviews.models import Review

User = get_user_model()


def generate_sample_image(title, subtitle, color=(37, 99, 235)):
    """
    Generates a high quality placeholder image using Pillow.
    """
    img = Image.new('RGB', (800, 500), color=color)
    draw = ImageDraw.Draw(img)

    # Draw simple gradient/overlay
    draw.rectangle([20, 20, 780, 480], outline=(255, 255, 255), width=3)
    
    # Draw text fallback
    draw.text((40, 200), title, fill=(255, 255, 255))
    draw.text((40, 250), subtitle, fill=(240, 240, 240))

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Seeds database with realistic sample users, properties, rental requests, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding database...'))

        # 1. Superuser / Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'OWNER',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # 2. Property Owners
        owner1, _ = User.objects.get_or_create(
            username='owner_sarah',
            defaults={
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': 'OWNER',
                'phone_number': '+1 (555) 234-5678',
                'bio': 'Real estate manager specializing in luxury downtown condos and suburban family homes.'
            }
        )
        owner1.set_password('owner123')
        owner1.save()

        owner2, _ = User.objects.get_or_create(
            username='owner_michael',
            defaults={
                'email': 'michael@example.com',
                'first_name': 'Michael',
                'last_name': 'Chang',
                'role': 'OWNER',
                'phone_number': '+1 (555) 876-5432',
                'bio': 'Owner of prime metropolitan apartments and commercial tech office spaces.'
            }
        )
        owner2.set_password('owner123')
        owner2.save()

        # 3. Tenants
        tenant1, _ = User.objects.get_or_create(
            username='tenant_emily',
            defaults={
                'email': 'emily@example.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'role': 'TENANT',
                'phone_number': '+1 (555) 345-6789',
                'bio': 'Software engineer looking for bright, well-located apartments.'
            }
        )
        tenant1.set_password('tenant123')
        tenant1.save()

        tenant2, _ = User.objects.get_or_create(
            username='tenant_alex',
            defaults={
                'email': 'alex@example.com',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'role': 'TENANT',
                'phone_number': '+1 (555) 987-6543',
                'bio': 'Graduate student and freelance designer seeking quiet rental homes.'
            }
        )
        tenant2.set_password('tenant123')
        tenant2.save()

        tenant3, _ = User.objects.get_or_create(
            username='tenant_lisa',
            defaults={
                'email': 'lisa@example.com',
                'first_name': 'Lisa',
                'last_name': 'Wang',
                'role': 'TENANT',
                'phone_number': '+1 (555) 456-7890',
                'bio': 'Marketing director relocating for work.'
            }
        )
        tenant3.set_password('tenant123')
        tenant3.save()

        # 4. Sample Properties
        properties_data = [
            {
                'owner': owner1,
                'title': 'Luxury Skyline 2-Bedroom Condo',
                'description': 'Breathtaking high-rise condominium with panoramic city skyline views, private balcony, hardwood flooring, in-unit washer/dryer, concierge service, and access to state-of-the-art rooftop pool and fitness center. Walking distance to subway station and downtown cafes.',
                'property_type': 'APARTMENT',
                'location': '742 Evergreen Terrace, Downtown Metro',
                'rent': 2450.00,
                'bedrooms': 2,
                'bathrooms': 2,
                'is_available': True,
                'color': (37, 99, 235)
            },
            {
                'owner': owner1,
                'title': 'Charming 4-Bedroom Suburban Family Villa',
                'description': 'Spacious and sun-filled 4-bedroom family home featuring a large fenced backyard, modern open-concept kitchen with stainless steel appliances, 2-car garage, and finished basement. Located in an award-winning school district with friendly parks nearby.',
                'property_type': 'HOUSE',
                'location': '124 Maple Wood Avenue, North Hills',
                'rent': 3800.00,
                'bedrooms': 4,
                'bathrooms': 3,
                'is_available': True,
                'color': (16, 185, 129)
            },
            {
                'owner': owner1,
                'title': 'Cozy Private Studio Room near University',
                'description': 'Quiet, fully furnished private room with dedicated ensuite bathroom and high-speed gigabit fiber internet. Includes utilities, shared gourmet kitchen, and bike storage. Ideal for quiet students or young professionals.',
                'property_type': 'ROOM',
                'location': '55 College Boulevard, University District',
                'rent': 850.00,
                'bedrooms': 1,
                'bathrooms': 1,
                'is_available': True,
                'color': (245, 158, 11)
            },
            {
                'owner': owner2,
                'title': 'Modern Tech Hub Co-Working & Private Office',
                'description': 'Turnkey creative office suite with glass partitioned conference room, acoustic phone booths, executive desks, and fiber optic connectivity. Building features 24/7 keycard access, secure elevator, and on-site cafe.',
                'property_type': 'OFFICE',
                'location': '500 Innovation Way, Suite 402, Silicon District',
                'rent': 4200.00,
                'bedrooms': 0,
                'bathrooms': 2,
                'is_available': True,
                'color': (99, 102, 241)
            },
            {
                'owner': owner2,
                'title': 'Waterfront 3-Bedroom Penthouse with Terrace',
                'description': 'Exceptional waterfront penthouse boasting wrap-around terrace, floor-to-ceiling glass windows, chef kitchen with marble island, smart home automation, and private underground parking. Unrivaled sunset views over the bay.',
                'property_type': 'APARTMENT',
                'location': '88 Marina Promenade, Harbor Bay',
                'rent': 5200.00,
                'bedrooms': 3,
                'bathrooms': 3,
                'is_available': True,
                'color': (14, 165, 233)
            },
            {
                'owner': owner2,
                'title': 'Minimalist Studio Apartment in Arts District',
                'description': 'Bright loft-style studio featuring exposed brick walls, 12-foot ceilings, polished concrete floors, and modern designer kitchen. Close to art galleries, microbreweries, and metro line.',
                'property_type': 'APARTMENT',
                'location': '210 Artisan Lane, Old Town Arts District',
                'rent': 1600.00,
                'bedrooms': 1,
                'bathrooms': 1,
                'is_available': True,
                'color': (168, 85, 247)
            },
            {
                'owner': owner1,
                'title': 'Contemporary 3-Bedroom Townhouse with Garden',
                'description': 'Recently renovated multi-level townhouse offering 3 bedrooms, 2.5 bathrooms, quartz countertops, central HVAC, private landscaped patio, and attached garage. Located in a quiet, tree-lined cul-de-sac.',
                'property_type': 'HOUSE',
                'location': '312 Willowbrook Court, Oakridge',
                'rent': 2950.00,
                'bedrooms': 3,
                'bathrooms': 2,
                'is_available': True,
                'color': (20, 184, 166)
            },
            {
                'owner': owner2,
                'title': 'Executive Corner Commercial Office Suite',
                'description': 'Prime commercial space suitable for consulting firms, law offices, or tech startups. Features executive meeting room, reception area, kitchenette, and floor-to-ceiling perimeter windows overlooking Central Plaza.',
                'property_type': 'OFFICE',
                'location': '100 Financial Center Blvd, 12th Floor',
                'rent': 3500.00,
                'bedrooms': 0,
                'bathrooms': 2,
                'is_available': False,
                'color': (100, 116, 139)
            },
        ]

        created_properties = []
        for p_data in properties_data:
            color = p_data.pop('color')
            prop, created = Property.objects.get_or_create(
                title=p_data['title'],
                defaults=p_data
            )
            if created or not prop.image:
                image_file = generate_sample_image(
                    prop.title[:30],
                    f"{prop.location[:35]} | ${prop.rent}/mo",
                    color=color
                )
                filename = f"sample_prop_{prop.id or 1}.jpg"
                prop.image.save(filename, image_file, save=True)
            created_properties.append(prop)

        # 5. Rental Requests
        # Emily requests Property 0 (Condo) -> ACCEPTED
        req1, _ = RentalRequest.objects.get_or_create(
            property=created_properties[0],
            tenant=tenant1,
            defaults={
                'message': 'Hi Sarah! I am a senior software developer looking to move in by the 1st of next month for a 12-month lease. Excellent credit and references ready.',
                'status': RentalRequest.STATUS_ACCEPTED,
            }
        )

        # Alex requests Property 0 (Condo) -> REJECTED
        req2, _ = RentalRequest.objects.get_or_create(
            property=created_properties[0],
            tenant=tenant2,
            defaults={
                'message': 'Hello, I would like to inquire about renting this condo starting next week.',
                'status': RentalRequest.STATUS_REJECTED,
            }
        )

        # Emily requests Property 1 (Villa) -> PENDING
        req3, _ = RentalRequest.objects.get_or_create(
            property=created_properties[1],
            tenant=tenant1,
            defaults={
                'message': 'Hello, my family is very interested in your 4-bedroom villa. Could we schedule a viewing this Saturday?',
                'status': RentalRequest.STATUS_PENDING,
            }
        )

        # Alex requests Property 2 (Studio Room) -> ACCEPTED
        req4, _ = RentalRequest.objects.get_or_create(
            property=created_properties[2],
            tenant=tenant2,
            defaults={
                'message': 'Hi Sarah, I am starting my Masters degree next semester and would love to rent this private room. Very quiet and responsible.',
                'status': RentalRequest.STATUS_ACCEPTED,
            }
        )

        # Lisa requests Property 4 (Penthouse) -> PENDING
        req5, _ = RentalRequest.objects.get_or_create(
            property=created_properties[4],
            tenant=tenant3,
            defaults={
                'message': 'Hi Michael, I am relocating for a corporate role and this penthouse looks ideal. Ready to sign a 2-year lease.',
                'status': RentalRequest.STATUS_PENDING,
            }
        )

        # 6. Reviews (Allowed for tenants with ACCEPTED rental requests)
        Review.objects.get_or_create(
            property=created_properties[0],
            tenant=tenant1,
            defaults={
                'rating': 5,
                'comment': 'Phenomenal property! The views are incredible, appliances are top tier, and Sarah was an exceptionally responsive and accommodating property owner. Highly recommended!',
            }
        )

        Review.objects.get_or_create(
            property=created_properties[2],
            tenant=tenant2,
            defaults={
                'rating': 5,
                'comment': 'Perfect location near campus, quiet study environment, and super fast WiFi. Everything promised was delivered.',
            }
        )

        # 7. Favorites
        Favorite.objects.get_or_create(user=tenant1, property=created_properties[1])
        Favorite.objects.get_or_create(user=tenant1, property=created_properties[4])
        Favorite.objects.get_or_create(user=tenant2, property=created_properties[0])

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
        self.stdout.write(self.style.SUCCESS("""
Sample Logins:
- Superuser / Admin: admin / admin123 (email: admin@example.com)
- Property Owner 1: owner_sarah / owner123 (email: sarah@example.com)
- Property Owner 2: owner_michael / owner123 (email: michael@example.com)
- Tenant 1: tenant_emily / tenant123 (email: emily@example.com)
- Tenant 2: tenant_alex / tenant123 (email: alex@example.com)
- Tenant 3: tenant_lisa / tenant123 (email: lisa@example.com)
        """))
