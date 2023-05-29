import nfc
import binascii

def on_connect(tag):
    print("Tag conectada!")
    uid = binascii.hexlify(tag.identifier).decode("utf-8")
    print("UID do cartão:", uid)
    global tag_value
    tag_value = uid

tag_value = None
clf = nfc.ContactlessFrontend("ttyUSB0")

try:
    print("Aproxime o cartão...")
    clf.connect(rdwr={'on-connect': on_connect})
except KeyboardInterrupt:
    pass
finally:
    clf.close()
    print("Valor da tag:", tag_value)

