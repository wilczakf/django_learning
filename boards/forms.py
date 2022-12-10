from django import forms
from boards.models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "...make it meaningful..."}
        ),
        max_length=4000,
        help_text="The maximum length of the text is 4000 characters.",
    )

    class Meta:
        model = Topic
        fields = ["subject", "message"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["message", ]
