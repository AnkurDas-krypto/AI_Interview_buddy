from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InterviewForm
from django.utils import timezone
import datetime
from django.http import HttpResponse
from zoneinfo import ZoneInfo
from .models import InterviewResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import pymongo
from bson import ObjectId
from django.conf import settings
from io import BytesIO
import tempfile
import os
from pymongo import MongoClient

@login_required
def interview_steps(request):
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid():
            start_timestamp = request.session.get('start_time')
            start_time = datetime.datetime.fromtimestamp(start_timestamp, tz=ZoneInfo('UTC'))
            
            if timezone.now() - start_time <= datetime.timedelta(seconds=40):
                response = form.save(commit=False)
                response.user = request.user  # Set the user before saving
                response.save()
                # Trigger PDF save after form save
                save_interview_pdf_to_mongo(request, response.id)  # Pass response id to PDF saving function
                return redirect('success_url')
            else:
                return redirect('timeout_url')
    else:
        request.session['start_time'] = timezone.now().timestamp()
        form = InterviewForm()

    return render(request, 'interview_steps.html', {'form': form})

def save_interview_pdf_to_mongo(request, response_id):
    # Fetch the response object from Django's database
    response = InterviewResponse.objects.get(id=response_id)  # Here response_id should be an integer

    # Render the HTML template to a string
    html_string = render_to_string('interview_response_template.html', {'response': response})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['resume_saver']  # Your MongoDB database name
    collection = db['applier_answers']

    # Convert Django model integer ID to string for MongoDB usage
    str_response_id = str(response_id)

    # Save PDF to MongoDB
    pdf_id = collection.insert_one({
        'username': request.user.username, 
        'response_id': str_response_id,  # Use the string version of the ID
        'pdf_file': pdf,
        'user_id': str(request.user.id)  # Also ensure user_id is a string if used as a reference
    }).inserted_id

    return pdf_id


def submission_success(request):
    return HttpResponse("Thank you for submitting your responses!")

def submission_timeout(request):
    return HttpResponse("Time has expired! Please try the interview again.")