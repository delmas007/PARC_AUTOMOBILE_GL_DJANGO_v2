from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.eva_uuid) + six.text_type(timestamp) + six.text_type(user.fin)
        )


account_activation_tokens = AccountActivationTokenGenerator()
