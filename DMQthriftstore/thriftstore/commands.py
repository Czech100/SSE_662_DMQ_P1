from abc import abstractmethod
from django.shortcuts import render, redirect
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
                 return redirect('item_list')  # Redirect to item list
         else:
             print(1)
             form = ReviewForm()  # Empty form for GET request
         return form

class NewReviewCommand(CommandInterface):
    def __init__(self, ReviewReciever, request):
        self.ReviewReciever = ReviewReciever
        self.request = request

    def execute(self):
        return self.ReviewReciever.new_review(self.request) #REQUEST!!!

class Invoker:
    def __init__(self):
        self._commands = {}

    def register_command(self, command_name, command):
        self._commands[command_name] = command

    def execute(self, command_name):
        return self._commands[command_name].execute()