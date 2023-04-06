##  🧟 Monstermash

> 1️⃣ version: 0.7.2

> ✍️ author: Mitchell Lisle

## Install
Install from PyPi

```shell
pip install monstermash
```

## Usage
Monstermash can generate keys, encrypt files or text with keys, and decrypt a file or text with keys

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

### Encrypt text or file
```shell
monstermash encrypt
```

```text
? Enter your private key: ****************************************************************
? Enter the public key: 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
? What type of data do you want to encrypt? (Use arrow keys)
 » file
   text
? Enter (or paste) the text to encrypt: *****

pjSSjlp65fgK/sfu3evw7QebzhqynviM5/GIh4QRvxUqpO2RLeEyY0ae4qpwWabMCg==
```

### Decryption text
```shell
monstermash decrypt
```

```text
? Enter your private key: ****************************************************************
? Enter the public key: 01765c67f451f3175f53bbe11d69d73a36d45074da935271473b4a1c460e3d79
? Enter the encrypted text: pjSSjlp65fgK/sfu3evw7QebzhqynviM5/GIh4QRvxUqpO2RLeEyY0ae4qpwWabMCg==

hello
```