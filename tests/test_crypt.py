from monstermash.crypt import Crypt, KeyPair


def test_generate():
    key = Crypt.generate()
    assert isinstance(key, KeyPair)


def test_encrypt(keypair_one: KeyPair, keypair_two: KeyPair):
    crypt = Crypt(keypair_one.private_key.get_secret_value().encode())
    plaintext = 'test'
    ciphertext = crypt.encrypt(plaintext.encode(), keypair_two.public_key.encode())
    assert ciphertext != plaintext


def test_decrypt(keypair_one: KeyPair, keypair_two: KeyPair):
    ciphertext = b'c1c9855e4f410284c7bcbd80532774a4b4c006f0f61423e83bb784630f4bb13041c3b1070bab813ab5efc15f792d07176967b9f3ee6dd4ab858cba6889f79568bebc58470bb8c3e045cce4fc'
    crypt = Crypt(keypair_two.private_key.get_secret_value().encode())
    plaintext = crypt.decrypt(ciphertext)
    assert plaintext == b'test'
