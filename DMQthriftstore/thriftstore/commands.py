from abc import abstractmethod
from django.shortcuts import get_object_or_404, render, redirect
from .models import Review
from .forms import ReviewForm

#Command Interface
class CommandInterface:
    @abstractmethod
    def execute():
        pass

class ReviewReciever:
    def new_review(self, request):
         if request.method == 'POST':
             form = ReviewForm(request.POST)
             if form.is_valid():
                 form.save()  # Save the new review
                 return None  # Redirect to item list
         else:
             print(1)
             form = ReviewForm()  # Empty form for GET request
         return form

    def review_edit(self, request, review_id):
        # View to edit an existing review
        review = get_object_or_404(Review, id=review_id)  # Retrieve the review or show 404
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()  # Save the updated review
                return None  # Redirect to item list
        else:
            form = ReviewForm(instance=review)  # Pre-fill form with review data
        return form

class NewReviewCommand(CommandInterface):
    def __init__(self, ReviewReciever, request):
        self.ReviewReciever = ReviewReciever
        self.request = request

    def execute(self):
        return self.ReviewReciever.new_review(self.request)

class EditReviewCommand(CommandInterface):
    def __init__(self, ReviewReciever, request, review_id):
        self.ReviewReciever = ReviewReciever
        self.request = request
        self.review_id = review_id

    def execute(self):
        return self.ReviewReciever.review_edit(self.request, self.review_id)
    
class Invoker:
    def __init__(self):
        self._commands = {}

    def register_command(self, command_name, command):
        self._commands[command_name] = command

    def execute(self, command_name):
        return self._commands[command_name].execute()