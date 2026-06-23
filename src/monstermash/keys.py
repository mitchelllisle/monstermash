from typing import Optional, Tuple

from pydantic import ValidationError

from monstermash.config import Config
from monstermash.datamodels import ProfileConfig
from monstermash.parser import ConfigManager


def read_profile(config_manager: ConfigManager, profile: str) -> ProfileConfig:
    """Read and validate a stored profile from the configuration file.

    Args:
        config_manager (ConfigManager): Manager used to read stored profiles.
        profile (str): The name of the profile to read.

    Returns:
        ProfileConfig: The validated keys stored under the profile.

    Raises:
        ValueError: If the profile is missing or does not contain valid keys.
    """
    config = config_manager.read()
    if not config.has_section(profile):
        raise ValueError(f"profile '{profile}' not found in the Monstermash config file")
    try:
        return ProfileConfig.model_validate(dict(config[profile]))
    except ValidationError as exc:
        raise ValueError(f"profile '{profile}' is missing a public_key") from exc


def default_config_manager() -> ConfigManager:
    """Build a ConfigManager pointed at the configured ``~/.monstermashcfg`` file.

    Returns:
        ConfigManager: A manager for the default Monstermash configuration file.
    """
    return ConfigManager(Config().config_file)


def resolve_encrypt_keys(
    config_manager: ConfigManager,
    profile: Optional[str],
    private_key: Optional[str],
    public_key: Optional[str],
    recipient: Optional[str] = None,
) -> Tuple[str, str]:
    """Resolve the private and public keys required to encrypt a message.

    The sender's private key comes from ``profile`` (or an explicit ``private_key``). The recipient
    is, in order: a stored ``recipient`` profile's public key, an explicit ``public_key``, then the
    sender profile's own public key. ``recipient`` and ``public_key`` are two ways to name the same
    thing and may not be combined.

    Args:
        config_manager (ConfigManager): Manager used to read stored profiles.
        profile (Optional[str]): The sender profile to read keys from, if any.
        private_key (Optional[str]): An explicit sender private key.
        public_key (Optional[str]): An explicit recipient public key.
        recipient (Optional[str]): A stored profile/contact whose public key is the recipient.

    Returns:
        Tuple[str, str]: The resolved ``(private_key, public_key)`` pair.

    Raises:
        ValueError: If the sender profile is a contact (no private key), if both ``recipient`` and
            ``public_key`` are given, or if no private/public key can be resolved.
    """
    if recipient is not None and public_key is not None:
        raise ValueError('pass either recipient or public_key, not both')

    if recipient is not None:
        public_key = read_profile(config_manager, recipient).public_key

    if profile is not None:
        stored = read_profile(config_manager, profile)
        if stored.private_key is None:
            raise ValueError(
                f"profile '{profile}' is a contact (public key only) and cannot encrypt; "
                'use one of your own profiles'
            )
        private_key = stored.private_key.get_secret_value()
        public_key = stored.public_key if public_key is None else public_key

    if private_key is None:
        raise ValueError('you must specify either a private key or profile')

    if public_key is None:
        raise ValueError('a public key is required for encryption')

    return private_key, public_key


def resolve_decrypt_key(
    config_manager: ConfigManager,
    profile: Optional[str],
    private_key: Optional[str],
) -> str:
    """Resolve the private key required to decrypt a message.

    Args:
        config_manager (ConfigManager): Manager used to read stored profiles.
        profile (Optional[str]): The profile to read the private key from, if any.
        private_key (Optional[str]): An explicit private key.

    Returns:
        str: The resolved private key.

    Raises:
        ValueError: If the profile is a contact (no private key) or no private key can be resolved.
    """
    if profile is not None:
        stored = read_profile(config_manager, profile)
        if stored.private_key is None:
            raise ValueError(f"profile '{profile}' is a contact (public key only) and cannot decrypt")
        private_key = stored.private_key.get_secret_value()

    if private_key is None:
        raise ValueError('you must specify either a private key or profile')

    return private_key
