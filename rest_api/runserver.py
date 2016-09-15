from models.plant import Plant

# exc = False
# try:
#   Plant.get(Plant.localhost == True)
#   exc = True
# except:
#   exc = False

# if exc is True:
from IoP import app
app.run(debug=True, port=2902, host='0.0.0.0')
