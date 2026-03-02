

print(bytes.fromhex('00'))

print(bytes.fromhex('2A'))

print(bytes.fromhex('20'))

my_byte = bytes.fromhex('00')
print(my_byte == b'\x00')
print(my_byte == b'')

my_byte2 = b''
print(my_byte2)