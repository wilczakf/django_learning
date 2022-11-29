from django.contrib.auth import login
from django.shortcuts import render, redirect

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
