
from fastapi import FastAPI
from model import Request
from fastapi.responses import JSONResponse
from model import AppUsers

app = FastAPI()

@app.get("/")
async def getServerRunningStatus():
  return JSONResponse(
    content={
      "message":"Server is Running",
      "endpoint-list": ["/identify", "/place-order"]
    }, status_code=200
  )

@app.post("/identify")
def fetchContactData(requestData: Request):
  email, phoneNumber = requestData.email, requestData.phoneNumber
  data = AppUsers.findContact(requestData)
  return JSONResponse(
    content=data, status_code=200
  )


if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

