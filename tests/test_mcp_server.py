import asyncio

import pytest

from monstermash.crypt import KeyPair
from monstermash.mcp_server import configure, decrypt, encrypt, generate_keypair, list_profiles, mcp


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """Point the Monstermash config file at a temporary location for the test."""
    cfg = tmp_path / 'monstermashcfg'
    monkeypatch.setenv('CONFIG_FILE', str(cfg))
    return cfg


def test_generate_keypair_stores_profile_and_hides_private_key(temp_config):
    result = generate_keypair('alice')
    assert set(result) == {'profile', 'public_key'}
    assert result['profile'] == 'alice'
    # private key never crosses the boundary
    assert 'private_key' not in result
    # but it was persisted server-side
    profiles = list_profiles()
    assert profiles == [{'profile': 'alice', 'public_key': result['public_key']}]


def test_encrypt_decrypt_roundtrip_via_profiles(temp_config):
    sender = generate_keypair('sender')
    recipient = generate_keypair('recipient')
    ciphertext = encrypt('hello monster', public_key=recipient['public_key'], profile='sender')
    assert ciphertext != 'hello monster'
    plaintext = decrypt(ciphertext, profile='recipient')
    assert plaintext == 'hello monster'
    # sender's public key is unused for decryption; recipient profile suffices
    assert sender['public_key'] != recipient['public_key']


def test_encrypt_to_own_profile_roundtrip(temp_config):
    # encrypting with no explicit public_key targets the profile's own key
    generate_keypair('self')
    ciphertext = encrypt('note to self', profile='self')
    assert decrypt(ciphertext, profile='self') == 'note to self'


def test_default_profile_from_env(temp_config, monkeypatch):
    generate_keypair('default')
    monkeypatch.setenv('MONSTERMASH_MCP_DEFAULT_PROFILE', 'default')
    ciphertext = encrypt('no profile arg needed')
    assert decrypt(ciphertext) == 'no profile arg needed'


def test_encrypt_requires_a_profile(temp_config):
    with pytest.raises(ValueError):
        encrypt('data')


def test_decrypt_requires_a_profile(temp_config):
    with pytest.raises(ValueError):
        decrypt('deadbeef')


def test_unknown_profile_raises_clear_error(temp_config):
    with pytest.raises(ValueError, match="profile 'ghost' not found"):
        decrypt('deadbeef', profile='ghost')


def test_configure_imports_existing_keys(temp_config, keypair_one: KeyPair, keypair_two: KeyPair):
    configure('sender', keypair_one.private_key.get_secret_value(), keypair_one.public_key)
    configure('recipient', keypair_two.private_key.get_secret_value(), keypair_two.public_key)
    ciphertext = encrypt('via import', profile='sender', public_key=keypair_two.public_key)
    assert decrypt(ciphertext, profile='recipient') == 'via import'


def test_list_profiles_hides_private_keys(temp_config, keypair_one: KeyPair):
    configure('default', keypair_one.private_key.get_secret_value(), keypair_one.public_key)
    profiles = list_profiles()
    assert profiles == [{'profile': 'default', 'public_key': keypair_one.public_key}]
    assert keypair_one.private_key.get_secret_value() not in str(profiles)


def test_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert names == {'generate_keypair', 'encrypt', 'decrypt', 'configure', 'list_profiles'}


def test_mcp_encrypt_decrypt_take_no_private_key_argument():
    # the security contract: no private_key parameter on the model-facing tools
    tools = asyncio.run(mcp.list_tools())
    by_name = {t.name: t for t in tools}
    assert 'private_key' not in by_name['encrypt'].inputSchema['properties']
    assert 'private_key' not in by_name['decrypt'].inputSchema['properties']
