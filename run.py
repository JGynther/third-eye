import subprocess
from multiprocessing import Process

import uvicorn


def run_embedding_server():
    uvicorn.run("tiny-embed-server.server:app", host="0.0.0.0", port=8000)


def run_matcher_server():
    uvicorn.run("matcher.matcher.server:app", host="0.0.0.0", port=8001)


def run_ui():
    subprocess.run(["bun", "run", "dev"], cwd="ui")


if __name__ == "__main__":
    processes = [
        Process(target=run_embedding_server),
        Process(target=run_matcher_server),
        Process(target=run_ui),
    ]

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
