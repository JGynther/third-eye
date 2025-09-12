from multiprocessing import Process

import uvicorn


def run_embedding_server():
    uvicorn.run("tiny-embed-server.server:app", host="0.0.0.0", port=8000)


def run_matcher_server():
    uvicorn.run("matcher.matcher.server:app", host="0.0.0.0", port=8001)


if __name__ == "__main__":
    embedding_server_process = Process(target=run_embedding_server)
    matcher_server_process = Process(target=run_matcher_server)

    embedding_server_process.start()
    matcher_server_process.start()

    try:
        embedding_server_process.join()
        matcher_server_process.join()

    except KeyboardInterrupt:
        embedding_server_process.terminate()
        matcher_server_process.terminate()
