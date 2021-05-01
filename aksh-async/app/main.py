from fastapi import FastAPI

from . import acts


app = FastAPI()

app.include_router(acts.routes.router, prefix='/acts')

# Add websockets
app.websocket('/acts/ws/')(acts.routes.ws)
