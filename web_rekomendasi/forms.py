from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PreferensiPengguna, Kategori

# Form Pendaftaran Akun Standar
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

# Form Pilih Kategori (Untuk KNN Cold Start)
class PreferensiForm(forms.ModelForm):
    # Menampilkan pilihan kategori sebagai Checkbox (bisa pilih lebih dari satu)
    kategori_disukai = forms.ModelMultipleChoiceField(
        queryset=Kategori.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Pilih kategori yang Anda minati"
    )

    class Meta:
        model = PreferensiPengguna
        fields = ['kategori_disukai']