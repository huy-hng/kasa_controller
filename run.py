from src.app import app
from src.periodic_runner import tl

tl.start()
app.run(debug=True, host='0.0.0.0')