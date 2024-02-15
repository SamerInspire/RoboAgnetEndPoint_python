import rsa

from Core.Config import settings


def enc(str):

    encMessage = rsa.encrypt(str.encode(),
                         settings.loadingAnimationPub)

    print("original string: ", str)
    print("encrypted string: ", encMessage)
    return encMessage

def dec(msg):
    str = rsa.decrypt(msg, settings.loadingAnimationPrv).decode()
    print("decrypted string: ", decMessage)
    return decMessage

encMessage = enc('Siminzo ===> sss')
print('encMessage ===> ',encMessage)
decMessage = dec(encMessage)
print('decMessage ===> ',decMessage)
