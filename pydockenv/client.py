import docker


class Client:

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = docker.from_env()

        return cls._instance
