import hashlib
import os


RESOURCES_VERSIONED = {
    "style.css": True,
    "script.js": True,
    "favicon.ico": False,
}


def get_resource_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), name)


def file_digest(path: str) -> str:
    gen = hashlib.sha1()
    with open(path, "rb") as f:
        while data := f.read(8192):
            gen.update(data)
    return gen.hexdigest()[:8]


def get_resource_target_name(name: str, is_versioned: bool) -> str:
    if not is_versioned:
        return name
    root, ext = os.path.splitext(name)
    digest = file_digest(get_resource_path(name))
    return f"{root}.{digest}{ext}"


def get_resources(rv: dict[str, bool]) -> dict[str, str]:
    return {
        name: get_resource_target_name(name, is_versioned)
        for name, is_versioned
        in rv.items()
    }
