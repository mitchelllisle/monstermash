```
███▄ ▄███▓ ▒█████   ███▄    █   ██████ ▄▄▄█████▓▓█████  ██▀███   ███▄ ▄███▓ ▄▄▄        ██████  ██░ ██ 
▓██▒▀█▀ ██▒▒██▒  ██▒ ██ ▀█   █ ▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒▓██▒▀█▀ ██▒▒████▄    ▒██    ▒ ▓██░ ██▒
▓██    ▓██░▒██░  ██▒▓██  ▀█ ██▒░ ▓██▄   ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒▓██    ▓██░▒██  ▀█▄  ░ ▓██▄   ▒██▀▀██░
▒██    ▒██ ▒██   ██░▓██▒  ▐▌██▒  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  ▒██    ▒██ ░██▄▄▄▄██   ▒   ██▒░▓█ ░██ 
▒██▒   ░██▒░ ████▓▒░▒██░   ▓██░▒██████▒▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒▒██▒   ░██▒ ▓█   ▓██▒▒██████▒▒░▓█▒░██▓
░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░   ░  ░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒
░  ░      ░  ░ ▒ ▒░ ░ ░░   ░ ▒░░ ░▒  ░ ░    ░     ░ ░  ░  ░▒ ░ ▒░░  ░      ░  ▒   ▒▒ ░░ ░▒  ░ ░ ▒ ░▒░ ░
░      ░   ░ ░ ░ ▒     ░   ░ ░ ░  ░  ░    ░         ░     ░░   ░ ░      ░     ░   ▒   ░  ░  ░   ░  ░░ ░
       ░       ░ ░           ░       ░              ░  ░   ░            ░         ░  ░      ░   ░  ░  ░
```

> _"He did the mash. He did the monster mash."_

**Encryption that doesn't bite.** Monstermash wraps the battle-tested [NaCl](https://nacl.cr.yp.to/)
(libsodium) cryptography in a friendly CLI, a clean Python API, and an MCP server — so developers,
engineers, and now AI agents can encrypt things correctly without touching a single cryptographic
knob.

> 1️⃣ version: 2.0.0 &nbsp;·&nbsp; ✍️ author: Mitchell Lisle

![PyPI](https://img.shields.io/pypi/v/monstermash)
![Python](https://img.shields.io/pypi/pyversions/monstermash)

---

## Why Monstermash?

- 🔒 **Safe by default** — built on NaCl's `Box` (Curve25519 + XSalsa20-Poly1305). No hand-rolled
  crypto, no caller-managed nonces, no footguns.
- 🪄 **Decrypt with just your private key** — the sender's public key rides *inside* the ciphertext
  (the "Mashed Envelope"), so the recipient needs nothing extra.
- 🧰 **One tool, three surfaces** — the same guarantees from the CLI, the Python library, and an
  optional MCP server for LLMs.
- 🗝️ **Profiles, not key-juggling** — store keypairs once (mode `0600`, just like your SSH keys) and
  reference them by name.
- 🚨 **Tamper-evident** — authenticated encryption fails *loudly*; a corrupted or wrong-key
  ciphertext raises, it never returns garbage.

## Install

```shell
pip install monstermash
```

Want the MCP server for AI agents? Grab the optional extra:

```shell
pip install "monstermash[mcp]"
```

## Quickstart

### 1. Generate a keypair

```shell
monstermash generate
```

```text
-----------------
Private Key (keep it secret, keep it safe)
a715a3d11d0f9c13de3bd6d390e36ba4e3322f4f2e4f1a13a54ba85be606de87
Public Key (you can share this one)
01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
-----------------
```

### 2. Save it as a profile (optional, but nice)

Profiles live in `~/.monstermashcfg` and are written with owner-only (`0600`) permissions.

```shell
monstermash configure \
  --profile default \
  --private-key a715a3d11d0f9c13de3bd6d390e36ba4e3322f4f2e4f1a13a54ba85be606de87 \
  --public-key 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
```

### 3. Encrypt

```shell
monstermash encrypt --profile default --data "hello world"
```

Or pass keys explicitly, or encrypt a whole file:

```shell
monstermash encrypt \
  --private-key a715a3d11d0f9c13de3bd6d390e36ba4e3322f4f2e4f1a13a54ba85be606de87 \
  --public-key 03ab4b8a77456729678a8022c2bfe22f64ed2db72692903e5f69e4a92649e646 \
  --file ./secret-plans.txt
```

### 4. Decrypt

```shell
monstermash decrypt \
  --private-key 91c7b2534454587a3330537bce60056e9da9a9bf75d32507152f49e85514970d \
  --data 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d797bee92fa7ff1216eb5324b247fd41cce283adbcc4df92baacfea27765360a7c0feb226cccc1538c0397783003d0283d2841d2a
```

The `--profile` flag works here too — no public key needed, it's baked into the ciphertext.

## How it works

Monstermash owns **no cryptographic primitives** — it leans entirely on NaCl. What it adds is
ergonomics:

```text
plaintext ──▶ NaCl Box (Curve25519 + XSalsa20-Poly1305) ──▶ [ sender public key │ nonce │ MAC │ ciphertext ] ──▶ hex
                                                                └──────────── the "Mashed Envelope" ────────────┘
```

Because the sender's public key travels inside the envelope, the recipient decrypts with only their
private key. See [`docs/domain/cryptography.md`](docs/domain/cryptography.md) for the full domain
model and design decisions.

## MCP Server

Monstermash ships an optional [Model Context Protocol](https://modelcontextprotocol.io) server so an
LLM can do real encryption natively — without ever handling raw private keys.

**Security model:** tool arguments flow into the model's context, so private keys **never cross the
boundary**. The model works by *profile name* (à la `ssh-agent`); the server reads the key from disk
locally. Set a default with `MONSTERMASH_MCP_DEFAULT_PROFILE`.

Run it over stdio:

```shell
monstermash-mcp
```

Register it with an MCP client (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "monstermash": {
      "command": "monstermash-mcp"
    }
  }
}
```

### Tools

| Tool | Description |
| --- | --- |
| `generate_keypair` | Generate a keypair, store it under a profile, and return only the public key. |
| `encrypt` | Encrypt text using a profile's keys (recipient defaults to the profile; override with `public_key`). |
| `decrypt` | Decrypt a ciphertext using a profile's private key. |
| `configure` | Import an existing keypair under a named profile. |
| `list_profiles` | List profile names and public keys — **private keys are never returned**. |

## License

See the repository for license details.
