"""
Accounts - Forms for Registration, Login, Password Reset, Email Verification
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# import re  # ── DISABLED: roll number regex validation removed

User = get_user_model()


# ──────────────────────────────────────────────────────────────────────────────
# REGISTRATION
# ──────────────────────────────────────────────────────────────────────────────

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Password (min 8 chars)',
            'id': 'id_password',
        }),
        min_length=8,
        help_text='Minimum 8 characters. Mix letters, numbers & symbols.',
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Confirm Password',
            'id': 'id_confirm_password',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'branch', 'year', 'phone']  # ── roll_number removed
        widgets = {
            # ── roll_number widget removed (field no longer in registration form)
            'first_name': forms.TextInput(attrs={
                'class': 'form-control cyber-input',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control cyber-input',
                'placeholder': 'Last Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control cyber-input',
                'placeholder': 'your@email.com',  # ── any email accepted
            }),
            'branch': forms.Select(attrs={'class': 'form-select cyber-select'}),
            'year': forms.Select(attrs={'class': 'form-select cyber-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control cyber-input',
                'placeholder': '10-digit mobile number',
            }),
        }

    # ── DISABLED: roll number validation removed for open registration
    # def clean_roll_number(self):
    #     roll = self.cleaned_data['roll_number'].upper()
    #     pattern = r'^\d{2}[A-Z]{2}\d[A-Z]\d{4}$'
    #     if not re.match(pattern, roll):
    #         raise forms.ValidationError('Invalid roll number. Format: 25NU1A4401')
    #     if User.objects.filter(roll_number=roll).exists():
    #         raise forms.ValidationError('This roll number is already registered.')
    #     return roll

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        # ── DISABLED: @nsrit.edu.in restriction removed for open registration
        # if not email.endswith('@nsrit.edu.in'):
        #     raise forms.ValidationError('Please use your NSRIT email address (@nsrit.edu.in)')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError({'confirm_password': 'Passwords do not match.'})
        return cleaned_data

    def save(self, commit=True):
        import uuid
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.email_verified = True  # ── auto-verified (email auth disabled for launch)
        # ── Auto-generate a unique roll_number placeholder since field is now optional
        if not user.roll_number:
            user.roll_number = f"USR-{str(uuid.uuid4())[:12].upper()}"
        if commit:
            user.save()
        return user


# ──────────────────────────────────────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────────────────────────────────────

class NSRITLoginForm(AuthenticationForm):
    # ── UPDATED: login by email instead of roll number
    username = forms.CharField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Your email address',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Password',
        })
    )


# ──────────────────────────────────────────────────────────────────────────────
# PROFILE UPDATE
# ──────────────────────────────────────────────────────────────────────────────

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control cyber-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control cyber-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-control cyber-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control cyber-input'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
# PASSWORD RESET — REQUEST (step 1)
# ──────────────────────────────────────────────────────────────────────────────

class PasswordResetRequestForm(forms.Form):
    roll_number_or_email = forms.CharField(
        label='Roll Number or Email',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Enter your email address',
            'autofocus': True,
        }),
        help_text='Enter the email address you registered with.'
    )

    def clean_roll_number_or_email(self):
        value = self.cleaned_data['roll_number_or_email'].strip()
        # Try to find the user (but don't reveal if they exist — anti-enumeration)
        return value

    def get_user(self):
        # ── UPDATED: lookup by email only (roll_number removed)
        value = self.cleaned_data.get('roll_number_or_email', '').strip()
        User = get_user_model()
        return User.objects.filter(email__iexact=value, is_active=True).first()


# ──────────────────────────────────────────────────────────────────────────────
# PASSWORD RESET — SET NEW PASSWORD (step 2)
# ──────────────────────────────────────────────────────────────────────────────

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'New Password (min 8 chars)',
            'autofocus': True,
            'id': 'id_new_password',
        }),
        help_text='Minimum 8 characters. Mix letters, numbers & symbols.',
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Confirm New Password',
            'id': 'id_confirm_password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('new_password')
        pw2 = cleaned_data.get('confirm_password')
        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
        return cleaned_data


# ──────────────────────────────────────────────────────────────────────────────
# RESEND VERIFICATION EMAIL
# ──────────────────────────────────────────────────────────────────────────────

class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control cyber-input',
            'placeholder': 'Your registered email address',
            'autofocus': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        # ── DISABLED: @nsrit.edu.in restriction removed
        # if not email.endswith('@nsrit.edu.in'):
        #     raise forms.ValidationError('Must be a valid @nsrit.edu.in address.')
        return email
