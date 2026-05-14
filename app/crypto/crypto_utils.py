from cryptography.fernet import Fernet


key = Fernet.generate_key()

cipher = Fernet(key)


def encrypt_message(message):

    encrypted_message = cipher.encrypt(
        message.encode()
    )

    return encrypted_message.decode()


def decrypt_message(encrypted_message):

    decrypted_message = cipher.decrypt(
        encrypted_message.encode()
    )

    return decrypted_message.decode()