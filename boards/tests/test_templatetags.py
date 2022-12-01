from django import forms
from django.test import TestCase
from boards.templatetags.form_tags import field_type, input_class


class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ("name", "password")


class FieldTypeTests(TestCase):
    def test__field_widget_type(self):
        form = ExampleForm()
        self.assertEqual("TextInput", field_type(form["name"]))
        self.assertEqual("PasswordInput", field_type(form["password"]))


class InputClassTests(TestCase):
    def test__unbound_field_initial_state(self):
        form = ExampleForm()
        self.assertEqual("form-control", input_class(form["name"]))

    def test__valid_bound_field(self):
        form = ExampleForm({"name": "test_user", "password": "test_password_123"})
        self.assertEqual("form-control is-valid", input_class(form["name"]))
        self.assertEqual("form-control", input_class(form["password"]))

    def test__invalid_bound_fields(self):
        form = ExampleForm({"name": "", "password": "123"})
        self.assertEqual("form-control is-invalid", input_class(form["name"]))
