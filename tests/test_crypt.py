from monstermash import Crypt
from nacl.exceptions import CryptoError
import unittest
import pytest

KEY_LENGTH = 64


class TestCrypt(unittest.TestCase):
    def setUp(self) -> None:
        self.bob_private = '3354802bd4a609572b44799c120ace9e5b2a3a25ff1af069dd547ff863c0153d'
        self.bob_public = 'd7368b71c505ec4f3334665c10220e1cb8743ab0f40c0dadaa165becf7898e5b'

        self.dracula_private = 'a3b8b3fdb9d9c4856b44d9d4c3c5d09ad24a9eb9ab0479bf6abc602734b51126'
        self.dracula_public = 'e6359c06567ac7ac7a0f936846fb53f8ad9749f2b18704c866b92aee573b3437'

        self.message = b'Hi Dracula'
        self.encrypted = 'phMusaFZRvtUYzFibWOQbdGThFbH8XhtOCE+9JchDqw7pMHK5dDE7xqeLqUjx26B2XU='

        self.bad_private = 'bcf6482975f2fd1279f5057dbcc6b3f01af80d6a14565c77bbfbb15898e84f24'
        self.bad_public = '59984bda7a0aef4942ee4d58ec0609ca8338de04314114e195ee5a6cef3dd962'

    def test_generate(self):
        keys = Crypt.generate()
        assert len(keys) == 2
        assert len(keys.public_key) == KEY_LENGTH
        assert len(keys.private_key) == KEY_LENGTH

    def test_encrypt_suceeds(self):
        c = Crypt(self.bob_private)
        encrypted = c.encrypt(self.message, self.dracula_public)
        assert encrypted != self.message

    def test_bob_decrypt_suceeds(self):
        c = Crypt(self.bob_private)
        decrypted = c.decrypt(self.encrypted, self.dracula_public)
        assert decrypted == self.message

    def test_dracula_decrypt_suceeds(self):
        c = Crypt(self.dracula_private)
        decrypted = c.decrypt(self.encrypted, self.bob_public)
        assert decrypted == self.message

    def test_bad_public_fails(self):
        with pytest.raises(CryptoError):
            c = Crypt(self.dracula_private)
            c.decrypt(self.encrypted, self.bad_public)

    def test_bad_private_fails(self):
        with pytest.raises(CryptoError):
            c = Crypt(self.bad_private)
            c.decrypt(self.encrypted, self.bob_public)

    def test_bad_keys_fails(self):
        with pytest.raises(CryptoError):
            c = Crypt(self.bad_private)
            c.decrypt(self.encrypted, self.bad_public)
