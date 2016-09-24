from models.mesh import MeshObject


for i in MeshObject.select():
  i.registered = False
  i.save()
