from rest_framework import views
from rest_framework.permissions import IsAuthenticated, AllowAny
from django import forms
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validators


class ResetPassword(views.APIView):
    """View for entering and re-entering a new password. """
    permission_classes = [AllowAny]
    authentication_classes = []

    class PasswordForm(forms.Form):
        password = forms.CharField(widget=forms.PasswordInput)
        re_enter_password = forms.CharField(widget=forms.PasswordInput)

    def render_page(self, success=False, note='Enter & re-enter new password'):
        form = self.PasswordForm()
        return render(self.request, 'password/reset_password.html',
                      {'form': form, 'success': success, 'note': note})

    def get(self, *args, **kwargs):
        key = kwargs.get('validation_key')
        get_object_or_404(get_user_model(), validation_key=key)
        return self.render_page()

    def post(self, *args, **kwargs):
        data = args[0].POST.dict()
        password = data.get('password')
        re_entered = data.get('re_enter_password')
        if not password:
            return self.render_page()
        if password != re_entered:
            return self.render_page(False, 'Passwords do not match')
        validation_key = kwargs.get('validation_key')
        model = get_user_model()
        user = model.objects.get(validation_key=validation_key)
        try:
            validators.validate_password(password, user=model)
        except ValidationError as exc:
            return self.render_page(False, ' '.join(exc.messages))

        user.set_password(password)
        user.save()
        user.send_reset_password_success_email()
        return self.render_page(True, 'Your password has been updated.')
