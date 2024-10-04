from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from django.shortcuts import render, redirect
from django.contrib import messages


from django.http import JsonResponse

def contact_us(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Save the message to the database
        contact_message = ContactMessage(
            full_name=full_name,
            email=email,
            phone=phone,
            message=message
        )
        contact_message.save()

        # Send email notification to the admin
        subject = f"New Contact Message from {full_name}"
        message_body = f"Name: {full_name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}"
        send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])

        # Return a JSON response
        return JsonResponse({'message': 'Your message has been sent successfully!'})

    return render(request, 'contact-us.html')

