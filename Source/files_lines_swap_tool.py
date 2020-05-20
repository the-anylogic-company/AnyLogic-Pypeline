import clipboard

# Just a helper file to convert between a file and quoted lines
# (Used to make edits to the server Python file and then be able
#   to quickly paste it back into the collection in the PyCommunicator agent)

# [Use]
# If you want to make changes to the Python server file:
# 1. Copy all the text from the "Initial contents" box of the "serverPyLines" collection inside the PyCommunicator agent.
# 2. Run the `to_file` function below. This will create a file called `file.py` in this directory.
# 3. Make your desired changes to the created `file.py`
# 4. Run the `to_lines` function below, passing in the path to the `file.py`. This will copy some text to your clipboard.
# 5. Delete the contents in the "Initial contents" box and paste the text copied to your clipboard.

def to_file(path="file.py"):
    cb = clipboard.paste().strip()
    if cb.startswith("{"):
        cb = cb[1:]
    if cb.endswith("}"):
        cb = cb[:-1]
        
    cb = "[" + cb + "]"
    lines = eval(cb)
    
    with open(path, "w") as f:
        f.write("\n".join(lines))


def to_lines(path="file.py"):
    with open(path) as f:
        lines = f.read().replace('"', '\\"').replace("\\", "\\\\").split("\n")

    body = '{\n"' + '",\n"'.join(lines) + '"\n}'
    clipboard.copy(body)
    print("Copied! Paste into 'Initial contents' field of serverPyLines collection")
