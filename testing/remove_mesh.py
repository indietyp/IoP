from mesh_network.dedicated import MeshDedicatedDispatch
from models.plant import Plant

target = Plant.get(name='holger')
MeshDedicatedDispatch().remove('remove', target)
