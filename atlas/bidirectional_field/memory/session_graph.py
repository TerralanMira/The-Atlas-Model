def log(t, bio, ai, text, metrics, path):
    rec = {"t":t, "bio":bio, "ai":ai, "text":text, "metrics":metrics}
    with open(path, "a") as f: f.write(json.dumps(rec)+"\n")
