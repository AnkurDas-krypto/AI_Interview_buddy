from django.shortcuts import render
from pymongo import MongoClient
from django.contrib.auth.decorators import login_required
import os

@login_required
def applied_status(request):
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client["resume_saver"]
    resumes = db.resumes

    user_resumes = resumes.find({"username": request.user.username})
    statuses = []

    for resume in user_resumes:
        if resume.get('match_percentage', 0) >= 70:
            status = {
                'name': request.user.username,
                'status': 'Selected for next round',
                'next_round': True  # Flag indicating the next round is applicable
            }
        else:
            status = {
                'name': request.user.username,
                'status': 'Rejected',
                'next_round': False
            }
        statuses.append(status)

    return render(request, 'applied_status.html', {'statuses': statuses})


@login_required
def next_round_view(request):
    # Here, you would typically prepare any data or perform actions required for the next round
    return render(request, 'next_round.html')
