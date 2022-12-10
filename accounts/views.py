from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import SignUpForm


def signup(request):
    if post := request.POST:
        form = SignUpForm(post)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    fields = ("first_name", "last_name", "email")
    template_name = "account.html"
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user
