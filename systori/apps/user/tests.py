from django.test import TestCase
from django.utils.translation import activate

from .models import User
from .forms import UserForm
from ..company.models import Company, Access


def create_user_data(self):
    self.company = Company.objects.create(schema="test", name="Test")
    self.company.activate()
    self.user = User.objects.create_superuser('test@damoti.com', 'pass')
    Access.objects.create(user=self.user, company=self.company)


class TestUserForm(TestCase):

    def setUp(self):
        create_user_data(self)

    def test_clean(self):
        activate('en')
        self.assertFalse(UserForm({}).is_valid())
        self.assertEquals('A name or email is required.',
                          UserForm({}).errors['__all__'][0])
        self.assertTrue(UserForm({'first_name': 'foo'}).is_valid())
        self.assertTrue(UserForm({'last_name': 'foo'}).is_valid())
        self.assertTrue(UserForm({'email': 'foo@bar.com'}).is_valid())

    def test_clean_password(self):
        self.assertEquals("The two password fields didn't match.",
                          UserForm({'first_name': 'foo', 'password1': 'foo'}).errors['password2'][0])
        self.assertTrue(UserForm({'first_name': 'foo', 'password1': 'foo', 'password2': 'foo'}).is_valid())
