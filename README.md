# MonsterMash

🧟 A simple wrapper around PyNaCl for encryption and decryption

‍🧟‍ Can also generate Private/Public Keys for use.

## Installation

```shell script
pip install monstermash
```

## Usage
Generate a new Private/Public Keypair

First generate a KeyPair for Bob, who wants to send some lyrics to Dracula
```shell script
monstermash --action=generate
#PrivateKey: b'3354802bd4a609572b44799c120ace9e5b2a3a25ff1af069dd547ff863c0153d'
#PublicKey: b'd7368b71c505ec4f3334665c10220e1cb8743ab0f40c0dadaa165becf7898e5b'
```

Dracula also does the same thing:
```shell script
monstermash --action=generate
#PrivateKey: b'a3b8b3fdb9d9c4856b44d9d4c3c5d09ad24a9eb9ab0479bf6abc602734b51126'
#PublicKey: b'e6359c06567ac7ac7a0f936846fb53f8ad9749f2b18704c866b92aee573b3437'
```

Bob and Dracula exchange public keys - Bob then encrypts a File fo Dracula using Dracula's public key, and Bobs Private Key.
```shell script
monstermash \
--action=encrypt \
--private-key=3354802bd4a609572b44799c120ace9e5b2a3a25ff1af069dd547ff863c0153d \
--public-key=e6359c06567ac7ac7a0f936846fb53f8ad9749f2b18704c866b92aee573b3437 \
--file=sample/lyrics.txt
```

Dracula can then decrypt the file using his Private Key and Bobs Public Key.
```shell script
monstermash \
--action=decrypt \
--private-key=a3b8b3fdb9d9c4856b44d9d4c3c5d09ad24a9eb9ab0479bf6abc602734b51126 \
--public-key=d7368b71c505ec4f3334665c10220e1cb8743ab0f40c0dadaa165becf7898e5b \
--file=sample/encrypted_lyrics.txt
```

If Bob wants to later decrypt the message he encrypted, he can also do this with his Private Key and Draculas Public Key:
```shell script
monstermash \
--action=decrypt \
--private-key=3354802bd4a609572b44799c120ace9e5b2a3a25ff1af069dd547ff863c0153d \
--public-key=e6359c06567ac7ac7a0f936846fb53f8ad9749f2b18704c866b92aee573b3437 \
--file=sample/encrypted_lyrics.txt
```