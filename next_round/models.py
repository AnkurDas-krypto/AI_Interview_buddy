from django.db import models
from django.contrib.auth.models import User

class InterviewResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question1 = models.TextField(verbose_name="Describe a situation where you leveraged Flask or FastAPI for a micro-service architecture. What were the key challenges and how did you overcome them?")
    question2 = models.TextField(verbose_name="How do you implement concurrency in Python, and what are the advantages of using asyncio compared to traditional threading?")
    question3 = models.TextField(verbose_name="Can you explain the principles of test-driven development (TDD) and how you apply them in a Python project?")
    question4 = models.TextField(verbose_name="What are some modern design patterns you have used in your Python projects? Provide examples of how they were implemented")
    question5 = models.TextField(verbose_name="How do you handle RESTful service implementation in Django, and what tools or libraries do you use to enhance this process?")
    question6 = models.TextField(verbose_name="Describe a scenario where you used Docker and Kubernetes to deploy a Python application. What were the key steps and considerations?")
    question7 = models.TextField(verbose_name="How do you utilize mocking frameworks in your unit tests? Provide an example of a complex test case that involved mocking.")
    question8 = models.TextField(verbose_name="What are some challenges you have faced with version control using Git, and how did you address them?")
    question9 = models.TextField(verbose_name="Explain a project where you utilized GCP technologies like BigQuery or DataFlow. What were the objectives and outcomes?")
    question10 = models.TextField(verbose_name="How do you ensure your code adheres to modern design principles and is maintainable for future development?")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username  

