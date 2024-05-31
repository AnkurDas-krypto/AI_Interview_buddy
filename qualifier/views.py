# from django.shortcuts import render
# from django.http import JsonResponse
# from pymongo import MongoClient
# from bson import ObjectId
# import fitz  # PyMuPDF is intended for handling PDF documents
# import os
# from transformers import pipeline

# def get_llama_response(resume_text, job_desc_text, prompt_template):
#     prompt = prompt_template.format(resume=resume_text, job_description=job_desc_text)
#     generator = pipeline("text-generation", model="sentence-transformers/all-MiniLM-L6-v2", api_key=os.getenv("HUGGINGFACE_API_KEY"))
#     results = generator(prompt, max_length=500, num_return_sequences=1)
#     return results[0]['generated_text']

# # MongoDB connection parameters
# MONGO_URI = 'mongodb+srv://ankurdas8017:edRSd0Y9uL8XLbys@cluster0.nkajquc.mongodb.net/'
# DB_NAME = 'resume_saver'
# COLLECTION_NAME = 'applier_answers'

# def fetch_pdf_from_mongo(username):
#     client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)  # for testing purposes
#     db = client['resume_saver']
#     collection = db['applier_answers']
#     pdf_data = collection.find_one({'username': username})
#     if pdf_data:
#         return pdf_data['pdf_file']
#     else:
#         return None

# def extract_text_from_pdf(pdf_bytes):
#     text = ""
#     document = fitz.open(stream=pdf_bytes, filetype="pdf")
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         text += page.get_text()
#     return text

# def compare_pdfs(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({"error": "User is not authenticated."}, status=403)

#     username = request.user.username  # Fetch the username from the user model

#     # Fetch the PDF from MongoDB
#     pdf_bytes = fetch_pdf_from_mongo(username)
#     if not pdf_bytes:
#         return JsonResponse({"error": "PDF not found for the logged-in user."}, status=404)

#     # Extract text from the MongoDB PDF
#     text_mongodb_pdf = extract_text_from_pdf(pdf_bytes)
#     # Assuming 'Kronos_ques.pdf' is a local file that acts as a job description
#     with open('Kronos_ques.pdf', 'rb') as f:
#         local_pdf_bytes = f.read()
#     text_local_pdf = extract_text_from_pdf(local_pdf_bytes)

#     # Format the prompt for the Llama model
#     prompt_template = """
#     Analyze the match between the resume and the job description as per the requirements of an ATS:
#     Resume text:
#     {resume}

#     Job description:
#     {job_description}
#     Please provide the match percentage, missing keywords, and any additional insights.
#     """
#     # Call the Hugging Face API
#     response_text = get_llama_response(text_mongodb_pdf, text_local_pdf, prompt_template)

#     # Return the result in a JSON response
#     return JsonResponse({"result": response_text})



##################################################################################################################
from django.shortcuts import render
from django.http import JsonResponse
import fitz  # PyMuPDF
from transformers import LongformerTokenizer, LongformerForSequenceClassification, pipeline
import os

def get_llama_response(resume_text, job_desc_text, prompt_template):
    # Initialize tokenizer and model for Longformer which can handle longer contexts
    tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')
    model = LongformerForSequenceClassification.from_pretrained('allenai/longformer-base-4096')
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)

    # Prepare the prompt
    prompt = prompt_template.format(resume=resume_text, job_description=job_desc_text)

    # Classify using the model
    results = classifier(prompt, truncation=True)
    
    # Assuming the result format always returns a list of dictionaries under the 'result' key
    # We extract the 'score' from the first dictionary in the list
    score = results[0]['score']
    return score

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as document:
            for page in document:
                text += page.get_text()
    except Exception as e:
        print(f"Failed to extract PDF text: {e}")
        return None
    return text

def compare_pdfs(request):
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': 'User is not authenticated.'})

    username = request.user.username
    user_pdf_path = f'{username}.pdf'

    if not os.path.exists(user_pdf_path):
        return render(request, 'error.html', {'message': 'User-specific PDF not found.'})

    job_description_path = 'Kronos_ques.pdf'
    if not os.path.exists(job_description_path):
        return render(request, 'error.html', {'message': 'Job description PDF not found.'})

    text_user_pdf = extract_text_from_pdf(user_pdf_path)
    text_job_description_pdf = extract_text_from_pdf(job_description_path)

    if text_user_pdf is None or text_job_description_pdf is None:
        return render(request, 'error.html', {'message': 'Failed to extract text from one or both PDF files.'})

    prompt_template = """
    Analyze the match between the resume and the job description:
    Resume text: {resume}
    Job description: {job_description}
    """
    score = get_llama_response(text_user_pdf, text_job_description_pdf, prompt_template)
    return render(request, 'final.html', {'score': score})