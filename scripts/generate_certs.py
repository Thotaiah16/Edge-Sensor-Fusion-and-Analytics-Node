import pathlib
import shutil
import subprocess

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
CERT_DIR = BASE_DIR / "docker" / "certs"

CERT_DIR.mkdir(parents=True, exist_ok=True)

ca_key = CERT_DIR / "ca.key"
ca_crt = CERT_DIR / "ca.crt"
server_key = CERT_DIR / "server.key"
server_csr = CERT_DIR / "server.csr"
server_crt = CERT_DIR / "server.crt"
client_key = CERT_DIR / "client.key"
client_csr = CERT_DIR / "client.csr"
client_crt = CERT_DIR / "client.crt"

use_docker = shutil.which("openssl") is None


def build_command(args):
    if not use_docker:
        return ["openssl", *args]
    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{CERT_DIR}:/certs",
        "alpine/openssl",
        *args,
    ]


def path_for(arg_path):
    if not use_docker:
        return str(arg_path)
    return f"/certs/{arg_path.name}"


commands = [
    build_command(["genrsa", "-out", path_for(ca_key), "2048"]),
    [
        *build_command(
            [
                "req",
        "-x509",
        "-new",
        "-nodes",
                "-key",
                path_for(ca_key),
        "-sha256",
        "-days",
        "365",
        "-subj",
        "/CN=EdgeSensorCA",
                "-out",
                path_for(ca_crt),
            ]
        ),
    ],
    build_command(["genrsa", "-out", path_for(server_key), "2048"]),
    [
        *build_command(
            [
                "req",
        "-new",
        "-key",
        path_for(server_key),
        "-subj",
        "/CN=mosquitto",
        "-out",
        path_for(server_csr),
            ]
        ),
    ],
    [
        *build_command(
            [
                "x509",
        "-req",
        "-in",
        path_for(server_csr),
        "-CA",
        path_for(ca_crt),
        "-CAkey",
        path_for(ca_key),
        "-CAcreateserial",
        "-out",
        path_for(server_crt),
        "-days",
        "365",
        "-sha256",
            ]
        ),
    ],
    build_command(["genrsa", "-out", path_for(client_key), "2048"]),
    [
        *build_command(
            [
                "req",
        "-new",
        "-key",
        path_for(client_key),
        "-subj",
        "/CN=edge-sensor",
        "-out",
        path_for(client_csr),
            ]
        ),
    ],
    [
        *build_command(
            [
                "x509",
        "-req",
        "-in",
        path_for(client_csr),
        "-CA",
        path_for(ca_crt),
        "-CAkey",
        path_for(ca_key),
        "-CAcreateserial",
        "-out",
        path_for(client_crt),
        "-days",
        "365",
        "-sha256",
            ]
        ),
    ],
]

for cmd in commands:
    subprocess.run(cmd, check=True)

print(f"Certificates generated in: {CERT_DIR}")
