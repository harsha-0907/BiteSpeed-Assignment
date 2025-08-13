from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from model import Request
from logic import AppUsers

app = FastAPI()

@app.get("/")
async def getServerRunningStatus():
    return JSONResponse(
        content={
            "message": "Server is Running",
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

@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: FastAPIRequest, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url="/docs")
    return JSONResponse(
        content={"detail": exc.detail}, status_code=exc.status_code
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
