# Tomcat Bruteforcer

Bruteforce de credenciales para el panel de Apache Tomcat.

## Instalación
```bash
pip install requests rich
```

## Uso
```bash
# Usuario y pass únicos
python tomcat_enum.py --url http://10.10.10.10 -P /manager/html -u admin -p admin

# Con wordlists
python tomcat_enum.py --url http://10.10.10.10 -P /manager/html -u users.txt -p rockyou.txt

# Con proxy
python tomcat_enum.py --url http://10.10.10.10 -P /manager/html -u admin -p rockyou.txt -x http://127.0.0.1:8080
```

## Argumentos
| Flag | Descripción |
|---|---|
| `--url` | URL del target |
| `-P` | Path del manager (`/manager/html`, `/host-manager/html`) |
| `-u` | Usuario o wordlist |
| `-p` | Password o wordlist |
| `-t` | Timeout (default: 5) |
| `-x` | Proxy |

## Disclaimer
Solo para uso en entornos autorizados.
