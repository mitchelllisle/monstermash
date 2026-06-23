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
        raise ValueError(f"profile '{profile}' is missing a private_key or public_key") from exc


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
) -> Tuple[str, str]:
    """Resolve the private and public keys required to encrypt a message.

    When a ``profile`` is supplied the keys are read from the configuration file; an explicitly
    supplied ``public_key`` always overrides the profile's stored public key.

    Args:
        config_manager (ConfigManager): Manager used to read stored profiles.
        profile (Optional[str]): The profile to read keys from, if any.
        private_key (Optional[str]): An explicit private key.
        public_key (Optional[str]): An explicit recipient public key.

    Returns:
        Tuple[str, str]: The resolved ``(private_key, public_key)`` pair.

    Raises:
        ValueError: If no private key or public key can be resolved.
    """
    if profile is not None:
        stored = read_profile(config_manager, profile)
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
        ValueError: If no private key can be resolved.
    """
    if profile is not None:
        private_key = read_profile(config_manager, profile).private_key.get_secret_value()

    if private_key is None:
        raise ValueError('you must specify either a private key or profile')

    return private_key
