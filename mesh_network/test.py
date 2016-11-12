from tools.mesh import MeshAES

with open('./keys/localhost.iv') as out:
  iv = out.read()
with open('./keys/localhost.key') as out:
  key = out.read()

print(key)
print(iv)

MeshAES.decrypt_file('encrypted.enc', 'encrypted.unenc', key, iv)
