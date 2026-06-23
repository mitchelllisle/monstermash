"""Model Context Protocol (MCP) server exposing Monstermash encryption to LLMs.

This module is part of the optional ``mcp`` extra. Install it with::

    pip install "monstermash[mcp]"

It exposes the NaCl/Curve25519 ("Monstermash style") primitives used by the CLI as MCP tools so an
LLM can generate keypairs, encrypt, and decrypt data natively.

Security boundary: a tool argument flows into the model's context and transcript, so **private keys
never cross this boundary**. Secret material stays server-side — the model references keys by
*profile name* only (like ``ssh-agent``), and the server reads the private key from disk locally. A
default profile can be set with the ``MONSTERMASH_MCP_DEFAULT_PROFILE`` environment variable.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from monstermash.crypt import Crypt
from monstermash.keys import default_config_manager, resolve_decrypt_key, resolve_encrypt_keys
from monstermash.utils.file import NEW_LINE_EXPR

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised only when extra is missing
    raise ImportError(
        'The Monstermash MCP server requires the optional "mcp" extra. '
        'Install it with: pip install "monstermash[mcp]"'
    ) from exc


class MCPSettings(BaseSettings):
    """Settings for the Monstermash MCP server, sourced from the environment.

    Attributes:
        default_profile (Optional[str]): Profile used by encrypt/decrypt when none is given.
            Set via ``MONSTERMASH_MCP_DEFAULT_PROFILE``.
    """

    model_config = SettingsConfigDict(env_prefix='MONSTERMASH_MCP_')

    default_profile: Optional[str] = None


mcp = FastMCP('monstermash')


def _require_profile(profile: Optional[str]) -> str:
    """Resolve the profile to use, falling back to the configured default.

    Args:
        profile (Optional[str]): An explicitly requested profile name.

    Returns:
        str: The profile name to use.

    Raises:
        ValueError: If no profile is given and no default is configured.
    """
    profile = profile or MCPSettings().default_profile
    if profile is None:
        raise ValueError(
            'no profile specified and no MONSTERMASH_MCP_DEFAULT_PROFILE set; '
            'create one with the configure tool first'
        )
    return profile


@mcp.tool()
def generate_keypair(profile: str) -> dict:
    """Generate a new Monstermash (NaCl/Curve25519) keypair and store it under a profile.

    The private key is written to the local config file and never returned, so it never enters the
    model's context. Use the returned public key to receive encrypted messages.

    Args:
        profile (str): The profile name to create or overwrite with the new keypair.

    Returns:
        dict: A mapping with the ``profile`` name and the hex-encoded ``public_key``.
    """
    keys = Crypt.generate()
    config_manager = default_config_manager()
    config = config_manager.read()
    config[profile] = {
        'private_key': keys.private_key.get_secret_value(),
        'public_key': keys.public_key,
    }
    config_manager.write(config)
    return {'profile': profile, 'public_key': keys.public_key}


@mcp.tool()
def encrypt(
    data: str,
    public_key: Optional[str] = None,
    profile: Optional[str] = None,
    recipient: Optional[str] = None,
) -> str:
    """Encrypt text using the Monstermash style of encryption.

    The sender's private key is sourced from a stored profile (never passed as an argument). The
    recipient is, in order: a stored ``recipient`` profile/contact's public key, an explicit
    ``public_key``, or the sender profile's own key. Pass ``recipient`` to target a contact added
    with ``add_contact``. ``recipient`` and ``public_key`` may not be combined.

    Args:
        data (str): The plaintext to encrypt.
        public_key (Optional[str]): Hex-encoded recipient public key. Defaults to the profile's.
        profile (Optional[str]): Profile to source the sender key from. Falls back to the configured
            default profile.
        recipient (Optional[str]): Name of a stored profile/contact whose public key is the recipient.

    Returns:
        str: The hex-encoded ciphertext.
    """
    profile = _require_profile(profile)
    private_key, public_key = resolve_encrypt_keys(default_config_manager(), profile, None, public_key, recipient)
    crypt = Crypt(private_key.encode())
    encrypted = crypt.encrypt(data.encode(), public_key.encode())
    return encrypted.decode()


@mcp.tool()
def decrypt(data: str, profile: Optional[str] = None) -> str:
    """Decrypt a Monstermash ciphertext.

    The recipient's private key is sourced from a stored profile (never passed as an argument). The
    sender's public key is read from the ciphertext, so no public key is required.

    Args:
        data (str): The hex-encoded ciphertext to decrypt.
        profile (Optional[str]): Profile to source the private key from. Falls back to the configured
            default profile.

    Returns:
        str: The decrypted plaintext.
    """
    profile = _require_profile(profile)
    private_key = resolve_decrypt_key(default_config_manager(), profile, None)
    crypt = Crypt(private_key.encode())
    decrypted = crypt.decrypt(NEW_LINE_EXPR.sub('', data).encode())
    return decrypted.decode()


@mcp.tool()
def configure(profile: str, private_key: str, public_key: str) -> str:
    """Store an existing keypair under a named profile in the Monstermash config file.

    Use this to import keys you already hold. To create fresh keys without ever exposing the private
    key, use ``generate_keypair`` instead.

    Args:
        profile (str): The profile name to create or overwrite.
        private_key (str): Hex-encoded private key to store.
        public_key (str): Hex-encoded public key to store.

    Returns:
        str: A confirmation message.
    """
    config_manager = default_config_manager()
    config = config_manager.read()
    config[profile] = {'private_key': private_key, 'public_key': public_key}
    config_manager.write(config)
    return f"Stored profile '{profile}' in the Monstermash config file."


@mcp.tool()
def add_contact(profile: str, public_key: str) -> str:
    """Store a recipient's public key under a profile name (a contact).

    A contact holds only a public key — no private key — so it can be used as an encryption
    recipient (via the ``encrypt`` tool's ``recipient`` argument) but can never decrypt. Use this
    when someone shares their public key with you. To import a keypair you own, use ``configure``.

    Args:
        profile (str): The contact name to create or overwrite.
        public_key (str): Hex-encoded public key shared by the recipient.

    Returns:
        str: A confirmation message.
    """
    config_manager = default_config_manager()
    config = config_manager.read()
    config[profile] = {'public_key': public_key}
    config_manager.write(config)
    return f"Stored contact '{profile}' in the Monstermash config file."


@mcp.tool()
def list_profiles() -> list:
    """List the names of stored configuration profiles.

    Private keys are never returned; only profile names and their public keys are exposed.

    Returns:
        list: A list of ``{"profile": name, "public_key": key}`` mappings.
    """
    config = default_config_manager().read()
    return [{'profile': section, 'public_key': config[section].get('public_key')} for section in config.sections()]


def main() -> None:
    """Run the Monstermash MCP server over stdio."""
    mcp.run()


if __name__ == '__main__':
    main()
