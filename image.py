
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# On sert les fichiers du dossier monté dans /app/output_images
app.mount("/images", StaticFiles(directory="/app/images"), name="images")

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=9999)
import os
from fastapi.responses import JSONResponse

@app.get("/list")
def list_images():
    return JSONResponse(content=os.listdir("/app/images"))  # adapte ici aussi
