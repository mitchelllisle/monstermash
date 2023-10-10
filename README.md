##  🧟 Monstermash

> 1️⃣ version: 1.12.0

> ✍️ author: Mitchell Lisle

## Install
Install from PyPi

```shell
pip install monstermash
```

## Usage
Monstermash can generate keys, encrypt files or text with keys, and decrypt a file or text

### Generate Keys
```shell
monstermash generate
```

```text
-----------------
Private Key (keep is secret, keep it safe)
a715a3d11d0f9c13de3bd6d390e36ba4e3322f4f2e4f1a13a54ba85be606de87
Public Key (you can share this one)
01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
-----------------
```

### Store configuration
```text
Usage: monstermash configure [OPTIONS]

Options:
  --profile TEXT      The name of the profile you want to create.
  --private-key TEXT  Your private key.
  --public-key TEXT   Your public key.
  --help              Show this message and exit.

```
```shell
monstermash configure \
  --profile default \
  --private-key a715a3d11d0f9c13de3bd6d390e36ba4e3322f4f2e4f1a13a54ba85be606de87 \
  --public-key 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
```

### Encrypt text or file
```text
Usage: monstermash encrypt [OPTIONS]

Options:
  --profile TEXT
  --private-key TEXT  Your private key.
  --public-key TEXT   Your public key.
  --file TEXT         The path to the file you want to encrypt
  --data TEXT         Input data you want to encrypt
  --help              Show this message and exit.
```

```shell
monstermash encrypt \
  --profile default \
  --public-key 03ab4b8a77456729678a8022c2bfe22f64ed2db72692903e5f69e4a92649e646 \
  --data "hello world"
```

### Decryption text
```text
Usage: monstermash decrypt [OPTIONS]

Options:
  --profile TEXT
  --private-key TEXT  Your private key.
  --file TEXT         The path to the file you want to encrypt
  --data TEXT         Input data you want to encrypt
  --help              Show this message and exit.
```

```shell
monstermash decrypt \
  --private-key 91c7b2534454587a3330537bce60056e9da9a9bf75d32507152f49e85514970d
  --data 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d797bee92fa7ff1216eb5324b247fd41cce283adbcc4df92baacfea27765360a7c0feb226cccc1538c0397783003d0283d2841d2a
```
