from django.shortcuts import render
from django.http import HttpResponse
from .forms import ResumeForm
from django.core.files.uploadedfile import InMemoryUploadedFile
import base64
import io
import pdf2image
import google.generativeai as genai
from pymongo import MongoClient
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
import os
from pymongo import MongoClient


mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client["resume_saver"]
resumes = db.resumes  # 'resumes' is the collection

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        uploaded_file.seek(0)  # Reset file pointer to the start
        try:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            if not images:
                raise ValueError("No images could be converted from the PDF. The PDF may be empty or corrupted.")
            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }]
            return pdf_parts
        except Exception as e:
            raise Exception(f"Failed to convert PDF to images: {str(e)}")
    else:
        raise FileNotFoundError("No file uploaded")

def get_uploaded_file_from_session(session):
    encoded_file = session.get('resume')
    if encoded_file:
        decoded_file = base64.b64decode(encoded_file)
        file_name = session.get('resume_name')
        file = InMemoryUploadedFile(
            file=io.BytesIO(decoded_file),
            field_name=None,
            name=file_name,
            content_type='application/pdf',
            size=len(decoded_file),
            charset=None
        )
        return file
    return None

@login_required
def home_view(request):
    response = None
    resume_name = ''
    job_description = ''
    form = ResumeForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        job_description = form.cleaned_data['job_description']
        uploaded_file = request.FILES.get('resume') or get_uploaded_file_from_session(request.session)

        if uploaded_file and uploaded_file.size > 0:
            try:
                pdf_content = input_pdf_setup(uploaded_file)
                prompt_type = request.POST.get('prompt_type')

                if prompt_type == 'analysis':
                    input_prompt = """
                    You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description.
                    Please share your professional evaluation on whether the candidate's profile aligns with the role.
                    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
                    """
                elif prompt_type == 'match':
                    input_prompt = """
                    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
                    your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
                    the job description. First the output should come as percentage and then keywords missing and last final thoughts.
                    """
                else:
                    return HttpResponse("Invalid prompt type", status=400)

                response = get_gemini_response(input_prompt, pdf_content, job_description)
                if prompt_type == 'match':
                    match_percentage = int(response.split('Percentage Match: ')[1].split('%')[0])
                    if match_percentage >= 70:
                        # Saving the username along with the resume details
                        resumes.insert_one({
                            "username": request.user.username,  # Save the username of the logged-in user
                            "name": uploaded_file.name,
                            "content": base64.b64encode(uploaded_file.read()).decode(),
                            "match_percentage": match_percentage,
                            "response": response
                        })
            except Exception as e:
                return HttpResponse(f"Error processing the PDF: {str(e)}", status=500)
        else:
            response = "No file uploaded or file is empty."
    else:
        # Clear session data on initial GET request
        request.session.pop('job_description', None)
        request.session.pop('resume', None)
        request.session.pop('resume_name', None)
        request.session.pop('response', None)

    # Get the name of the uploaded file from session if available
    resume_name = request.session.get('resume_name', '')

    return render(request, 'home.html', {'form': form, 'response': response, 'resume_name': resume_name})



def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # or any other appropriate URL

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')  # or any other appropriate URL
        else:
            return HttpResponse("Invalid login details.", status=401)

    return render(request, 'login.html', {'form': form})



def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                return redirect('login')  # Redirect to login if user exists
            form.save()
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                return redirect('home')
            return HttpResponse("Account created successfully, please login.", status=201)
        else:
            return HttpResponse("Form is not valid. Please check your data.", status=400)

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



def base_view(request):
    return render(request, 'base.html')