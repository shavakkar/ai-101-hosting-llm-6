import os

def create_file(filename, content=""):
    with open(filename, "w") as f:
        f.write(content)
    return {"status": "success", "message": f"File '{filename}' created."}

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return {"status": "success", "message": f"File '{filename}' deleted."}
    else:
        return {"status": "error", "message": f"File '{filename}' not found."}
