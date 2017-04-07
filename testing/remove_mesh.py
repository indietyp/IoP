from mesh_network.dedicated import MeshDedicatedDispatch
from models.plant import Plant

target = Plant.get(name='gertrud')
MeshDedicatedDispatch().remove('remove', target)
