# Python program to find SHA256 hash string of a file
import hashlib;
import base64;
print(
 base64.urlsafe_b64encode(
 hashlib.sha256(open('_pokereval_2_4.pyd', 'rb').read()).digest())
 .decode('latin1')
 .rstrip(b'=')
 )