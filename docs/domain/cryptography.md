# Cryptography — Domain Documentation

## What this domain does

Cryptography in Monstermash is about making a safe, battle-tested cryptography technique (NaCl)
easy to use and genuinely useful for developers, engineers, and now AI. Monstermash owns **no
cryptographic primitives** — it wraps PyNaCl/libsodium (Curve25519 + XSalsa20-Poly1305) behind an
ergonomic facade, adds a self-describing ciphertext envelope, profile-based key storage, and three
access surfaces (CLI, Python library, MCP server) so the same guarantees hold no matter how the
encryption is invoked.

## Ubiquitous Language

**Keypair**
Definition: A matched `(private_key, public_key)` pair generated together via `Crypt.generate()`; modelled as `KeyPair` (private as `SecretStr`, public as `str`).
Not to be confused with: a *profile*, which is a named, persisted home for one keypair.

**Private key**
Definition: A 32-byte Curve25519 secret, hex-encoded (64 chars), held by one party and never shared. Used to decrypt, and as the sender's half when encrypting.
Alias / external term: "secret key" in NaCl/libsodium docs.

**Public key**
Definition: The 32-byte Curve25519 value derived from a private key, hex-encoded, freely shareable. Identifies the recipient when encrypting.

**Plaintext**
Definition: The unencrypted message bytes going into `encrypt` / coming out of `decrypt`.

**Ciphertext**
Definition: The hex-encoded output of `encrypt`. In Monstermash this is a *Mashed Envelope* (see below), not a bare NaCl Box output.

**Mashed Envelope**
Definition: Monstermash's ciphertext format — the sender's raw 32-byte public key prepended to a NaCl Box output (nonce + Poly1305 MAC + encrypted bytes), the whole thing hex-encoded. Because the sender's public key travels *inside* the envelope, the recipient decrypts using only their own private key (`Crypt.decrypt` slices off the leading `key_length` bytes to recover the sender key). This is the one primitive Monstermash adds on top of NaCl.
Not to be confused with: a raw NaCl `Box` ciphertext, which carries no key and requires the decrypter to already know the sender's public key out-of-band.

**Box**
Definition: NaCl's authenticated public-key encryption primitive (`nacl.public.Box`): X25519 ECDH between sender-private and recipient-public → shared secret → XSalsa20-Poly1305 authenticated encryption.
Alias / external term: `crypto_box` (libsodium).

**Profile**
Definition: A named section in `~/.monstermashcfg` storing a `private_key` + `public_key`, so commands/tools can reference keys by name instead of passing raw key material.

**Encoder**
Definition: The byte-encoding scheme for keys and messages; Monstermash uses `HexEncoder` throughout, split into `key_encoder` and `message_encoder` on `Crypt`.

**Crypt**
Definition: The facade class wrapping NaCl. Holds one private key and exposes `generate`, `encrypt`, `decrypt`, and key properties — the single entry point engineers (and the MCP server) use.

**Nonce**
Definition: The per-message random value NaCl generates inside `Box.encrypt` and prepends to the ciphertext; never reused, never managed by the caller.

## Bounded Context

```
[Cryptography — Monstermash]
  subdomains:
    - Key Management      (generate, store, profiles)
    - Encryption Ops      (Crypt facade, Mashed Envelope, encode/decode)
    - Access Surfaces     (CLI, library API, MCP server)

  owns:
    - Mashed Envelope format (sender-public-key-prepended ciphertext)
    - Profile / config scheme (~/.monstermashcfg)
    - CLI contract, library API (Crypt), MCP tool contract

  depends on:
    - PyNaCl / libsodium   (the actual primitives — deliberately NOT owned;
                            this is the "safe, battle-tested" guarantee)
    - pydantic / pydantic-settings (boundary models, SecretStr, config)
    - click (CLI), mcp (optional MCP server)

  provides to:
    - developers/engineers (CLI + Python library)
    - AI / LLMs (MCP stdio server tools)

  integration style:
    - CLI args + stdin/stdout
    - config file (~/.monstermashcfg)
    - file in/out (--file)
    - MCP over stdio (tools: generate_keypair, encrypt, decrypt, configure, list_profiles)
```

## Domain Events

| Event | Triggered by | Consumed by |
| --- | --- | --- |
| `KeypairGenerated` | `generate` / `generate_keypair` | User stores or shares the keys |
| `ProfileConfigured` | `configure` | Later encrypt/decrypt that reference the profile |
| `MessageEncrypted` | `encrypt` | Recipient / transport |
| `MessageDecrypted` | `decrypt` | The reading application |
| `DecryptionFailed` | Tampered/wrong-key ciphertext (NaCl `CryptoError`) | Caller, as a loud error |

`DecryptionFailed` is part of the security story: authenticated encryption *fails loudly* rather
than returning corrupted plaintext.

## Key Decisions

**Decision: Build on NaCl, own no primitives**
Context: Hand-rolled crypto is the classic footgun; the goal is *ease of use*, not novel cryptography.
Decision: Wrap PyNaCl/libsodium (Curve25519 + XSalsa20-Poly1305). Monstermash only adds ergonomics.
Consequences: Security rests on an audited library; upgrades track PyNaCl. No custom cipher code to review.
Constraints: Must not expose raw primitive misuse (e.g. caller-managed nonces).

**Decision: The Mashed Envelope (prepend sender public key)**
Context: Standard NaCl decryption requires the recipient to already know the sender's public key out-of-band — awkward for a CLI/tool.
Decision: Prepend the sender's raw public key to the ciphertext; `decrypt` slices off the first `key_length` (32) bytes to recover it.
Consequences: Recipient decrypts with only their private key. **But** key length is hard-coded to 32 — changing the encoder/key size silently breaks the split. Anyone parsing ciphertext must know the leading 32 bytes are *not* secret.
Constraints: Envelope format is now a compatibility contract — changing it breaks all existing ciphertexts.

**Decision: Hex encoding everywhere**
Context: Keys and ciphertext must survive CLI args, config files, JSON, and copy-paste.
Decision: `HexEncoder` for both keys and messages.
Consequences: Text-safe but ~2x size vs. base64. Consistent and debuggable.

**Decision: Secrets as `SecretStr`, keys via profiles/env, never logged**
Context: Private keys are the whole ballgame; leaking one in a log or repr is catastrophic.
Decision: Private key is `SecretStr` in `KeyPair`; profiles live in `~/.monstermashcfg`; config via `BaseSettings`. `list_profiles` returns public keys only.
Consequences: Private key won't show in tracebacks/reprs.
Constraints (privacy/security): See the two security decisions below for the residual risks (plaintext-at-rest, MCP argument boundary).

**Decision: Authenticated encryption fails loudly**
Context: Silent corruption is worse than an error.
Decision: Rely on Poly1305 MAC; tampered or wrong-key input raises rather than returning garbage.
Consequences: Callers must handle the exception; integrity is guaranteed, not optional.

**Decision: Private keys on disk in plaintext — ACCEPTED**
Context: Profiles must persist usable key material; an encrypted keystore needs a master secret, which just moves the problem.
Decision: Store private keys plaintext in `~/.monstermashcfg`, same trust model as `~/.ssh/` private keys — the filesystem and file permissions are the security boundary.
Consequences: Acceptable and familiar. **Mitigation: the file must be `0600`.** `ConfigManager.write` currently opens with the default umask, *not* an enforced `0600` — SSH refuses to use over-permissive key files, Monstermash does not. Flagged for hardening (see Open Questions).

**Decision (to implement): MCP must not take private keys as tool arguments**
Context: An MCP tool argument flows *into the model's context* and transcript. Passing a raw private key as an `encrypt`/`decrypt` argument leaks it to the LLM — backwards from the SSH model where the secret never leaves the local agent.
Decision: On the MCP surface, secret material stays server-side. `encrypt`/`decrypt` accept a **`profile` name only** (or a server-configured default via `BaseSettings`/env); the server reads the private key from disk locally. Drop the `private_key` parameter from the MCP `encrypt`/`decrypt` tools (`public_key` may stay — it is public). `generate_keypair` may optionally write straight to a profile so a fresh private key never round-trips through the model.
Consequences: Mirrors `ssh-agent` — the model orchestrates by reference, the daemon holds the secret. The Python library API keeps explicit-key parameters; only the MCP boundary is restricted.
Constraints (privacy/security): No private key should ever cross the model boundary.

## Goals & Success Criteria

What "good" looks like:

- **Safe by default** — hard to misuse: no caller-managed nonces, no raw primitive access, secrets typed as `SecretStr`, authenticated encryption that fails loudly.
- **Easy to use** — one `Crypt` facade, one-command keygen, profiles instead of juggling raw key strings; the Mashed Envelope means "decrypt with just your private key."
- **Battle-tested foundation** — zero custom cryptography; all primitives ride on PyNaCl/libsodium.
- **Reach across surfaces** — identical guarantees from CLI, Python library, or MCP (AI) without re-implementing crypto per surface.

Working well = a developer or LLM encrypts/decrypts correctly on the first try without touching a
cryptographic knob. Struggling = anyone needs to understand NaCl internals, hand-manage
nonces/encoders, or pass raw secrets through an untrusted boundary to get the job done.

## Open Questions

- **MCP key handling** — implement the profile/env-only design so private keys never cross the model boundary; remove the `private_key` argument from the MCP `encrypt`/`decrypt` tools. (Decision made above; implementation pending — candidate for the conduit review pass.)
- **Config file permissions** — enforce `0600` on `~/.monstermashcfg` when writing (and ideally refuse to read an over-permissive file, as SSH does). Currently relies on the ambient umask.
- **`key_length` coupling** — the Mashed Envelope hard-codes a 32-byte split; document/guard against encoder or key-size changes that would silently corrupt decryption.
