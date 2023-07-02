from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import UserCreationForm


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy("room-list"))
        return super().dispatch(request, *args, **kwargs)
