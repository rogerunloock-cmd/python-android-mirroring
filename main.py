import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import secrets
import string
import time
import threading

import qrcode
from PIL import ImageTk


SCRCPY_PASTA = Path(r"C:\scrcpy")
SCRCPY_EXE = SCRCPY_PASTA / "scrcpy.exe"
ADB_EXE = SCRCPY_PASTA / "adb.exe"


def executar_comando(comando: list[str]) -> subprocess.CompletedProcess[str]:
    """Executa um comando e devolve o resultado."""
    return subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=False,
    )


def verificar_arquivos() -> bool:
    """Confere se scrcpy.exe e adb.exe existem."""
    if not SCRCPY_EXE.exists():
        messagebox.showerror(
            "Arquivo não encontrado",
            f"Não encontrei:\n{SCRCPY_EXE}",
        )
        return False

    if not ADB_EXE.exists():
        messagebox.showerror(
            "Arquivo não encontrado",
            f"Não encontrei:\n{ADB_EXE}",
        )
        return False

    return True


def listar_dispositivos() -> list[str]:
    """Retorna a lista de aparelhos autorizados pelo ADB."""
    resultado = executar_comando([str(ADB_EXE), "devices"])

    dispositivos = []

    for linha in resultado.stdout.splitlines()[1:]:
        partes = linha.split()

        if len(partes) >= 2 and partes[1] == "device":
            dispositivos.append(partes[0])

    return dispositivos


def atualizar_status() -> None:
    """Verifica se existe algum celular conectado."""
    if not verificar_arquivos():
        return

    dispositivos = listar_dispositivos()

    if dispositivos:
        texto_status.set(
            f"Celular conectado: {dispositivos[0]}"
        )
    else:
        texto_status.set("Nenhum celular autorizado")


def obter_ip_celular() -> str | None:
    """Obtém o endereço IP Wi-Fi do celular conectado por USB."""
    resultado = executar_comando(
        [
            str(ADB_EXE),
            "shell",
            "ip",
            "route",
        ]
    )

    for linha in resultado.stdout.splitlines():
        if "src" in linha:
            partes = linha.split()

            if "src" in partes:
                indice = partes.index("src")

                if indice + 1 < len(partes):
                    return partes[indice + 1]

    return None

def gerar_dados_pareamento_qr() -> tuple[str, str, str]:
    caracteres = string.ascii_letters + string.digits + "!@#$%&*+-_=<>?"
    
    sufixo = "".join(secrets.choice(caracteres) for _ in range(10))
    senha = "".join(secrets.choice(caracteres) for _ in range(12))

    nome_servico = f"studio-{sufixo}"
    conteudo_qr = f"WIFI:T:ADB;S:{nome_servico};P:{senha};;"

    return nome_servico, senha, conteudo_qr

def aguardar_e_parear_qr(nome_servico: str, senha: str) -> None:
    texto_status.set("Aguardando leitura do QR Code...")

    limite = time.time() + 60

    while time.time() < limite:
        resultado = executar_comando(
            [str(ADB_EXE), "mdns", "services"]
        )

        for linha in resultado.stdout.splitlines():
            if (
                nome_servico in linha
                and "_adb-tls-pairing._tcp" in linha
            ):
                partes = linha.split()

                if len(partes) >= 3:
                    endereco = partes[-1]

                    pareamento = executar_comando(
                        [
                            str(ADB_EXE),
                            "pair",
                            endereco,
                            senha,
                        ]
                    )

                    saida = (
                        pareamento.stdout
                        + pareamento.stderr
                    ).strip()

                if "Successfully paired" in saida:
                    texto_status.set("Pareamento por QR concluído!")
                    texto_status.set("Pareado! Conectando ao celular...")

                    time.sleep(2)

                    janela.after(0, atualizar_status)
                    janela.after(1000, iniciar_espelhamento)

                    return

                messagebox.showerror(
                "Erro no pareamento",
                saida,
            )
                return

        time.sleep(1)

    texto_status.set("Tempo de pareamento esgotado")

    messagebox.showwarning(
        "QR Code expirado",
        "O celular não foi encontrado em 60 segundos.",
    )
def iniciar_pareamento_qr() -> None:
    nome_servico, senha, conteudo_qr = gerar_dados_pareamento_qr()

    mostrar_qrcode(conteudo_qr)
    texto_status.set("Escaneie o QR Code no celular...")

    threading.Thread(
        target=aguardar_e_parear_qr,
        args=(nome_servico, senha),
        daemon=True,
    ).start()

def mostrar_qrcode(texto: str) -> None:
    """Cria e mostra o QR Code dentro da interface."""
    qr = qrcode.QRCode(
        version=None,
        box_size=7,
        border=2,
    )

    qr.add_data(texto)
    qr.make(fit=True)

    imagem = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    imagem = imagem.resize((190, 190))

    foto = ImageTk.PhotoImage(imagem)

    label_qrcode.configure(image=foto)
    label_qrcode.image = foto

    texto_qr.set(texto)


def conectar_wifi() -> None:
    """Ativa o ADB TCP/IP e conecta o celular pela rede Wi-Fi."""
    if not verificar_arquivos():
        return

    dispositivos = listar_dispositivos()

    # Precisamos primeiro de um aparelho conectado por USB.
    dispositivos_usb = [
        dispositivo
        for dispositivo in dispositivos
        if ":" not in dispositivo
    ]

    if not dispositivos_usb:
        messagebox.showwarning(
            "USB necessário",
            "Primeiro conecte o celular pelo cabo USB.\n\n"
            "Ative a Depuração USB e aceite a autorização "
            "que aparecer no celular.",
        )
        return

    texto_status.set("Obtendo IP do celular...")
    janela.update_idletasks()

    ip = obter_ip_celular()

    if not ip:
        messagebox.showerror(
            "IP não encontrado",
            "Não consegui encontrar o IP do celular.\n\n"
            "Verifique se o computador e o celular estão "
            "conectados à mesma rede Wi-Fi.",
        )
        return

    texto_status.set("Ativando conexão Wi-Fi...")
    janela.update_idletasks()

    resultado_tcpip = executar_comando(
        [
            str(ADB_EXE),
            "tcpip",
            "5555",
        ]
    )

    if resultado_tcpip.returncode != 0:
        messagebox.showerror(
            "Erro",
            "Não consegui ativar o ADB por Wi-Fi.\n\n"
            f"{resultado_tcpip.stderr}",
        )
        return

    endereco = f"{ip}:5555"

    resultado_connect = executar_comando(
        [
            str(ADB_EXE),
            "connect",
            endereco,
        ]
    )

    resposta = (
        resultado_connect.stdout
        + resultado_connect.stderr
    ).lower()

    if (
        "connected to" not in resposta
        and "already connected" not in resposta
    ):
        messagebox.showerror(
            "Erro de conexão",
            "Não consegui conectar ao celular por Wi-Fi.\n\n"
            f"{resultado_connect.stdout}\n"
            f"{resultado_connect.stderr}",
        )
        return

    mostrar_qrcode(
        f"adb://{endereco}"
    )

    texto_status.set(
        f"Wi-Fi conectado: {endereco}"
    )

    messagebox.showinfo(
        "Conectado",
        "Celular conectado por Wi-Fi!\n\n"
        "Agora você pode retirar o cabo USB.",
    )


def iniciar_espelhamento() -> None:
    """Abre o scrcpy para espelhar o aparelho."""
    if not verificar_arquivos():
        return

    dispositivos = listar_dispositivos()

    if not dispositivos:
        messagebox.showwarning(
            "Celular não encontrado",
            "Conecte o celular, ative a depuração USB "
            "e aceite a autorização na tela do aparelho.",
        )
        return

    dispositivo_wifi = next(
        (d for d in dispositivos if d[0].isdigit() and ":" in d),
        dispositivos[0],
    )

    comando = [
        str(SCRCPY_EXE),
        "-s",
        dispositivo_wifi,
        "--window-title=Meu espelhamento Python",
        "--max-size=1280",
    ]

    try:
        subprocess.Popen(
            comando,
            cwd=SCRCPY_PASTA,
        )

        texto_status.set("Espelhamento iniciado")

    except OSError as erro:
        messagebox.showerror(
            "Erro",
            f"Não foi possível iniciar o scrcpy:\n{erro}",
        )


def iniciar_tela_desligada() -> None:
    """Espelha mantendo a tela física do celular desligada."""
    if not verificar_arquivos():
        return

    dispositivos = listar_dispositivos()

    if not dispositivos:
        messagebox.showwarning(
            "Celular não encontrado",
            "Nenhum celular autorizado foi encontrado.",
        )
        return

    subprocess.Popen(
        [
            str(SCRCPY_EXE),
            "--turn-screen-off",
            "--window-title=Espelhamento privado",
        ],
        cwd=SCRCPY_PASTA,
    )

    texto_status.set(
        "Espelhamento iniciado com a tela desligada"
    )


def parear_sem_cabo() -> None:
    ip_porta = simpledialog.askstring(
    "Pareamento sem cabo",
    "Digite o IP e a PORTA de pareamento.\n\nExemplo: 192.168.100.168:45553",
)



    if not ip_porta:
        return

    codigo = simpledialog.askstring(
    "Código de pareamento",
    "Digite o código de pareamento de 6 dígitos:",
)

    if not codigo:
        return

    resultado = subprocess.run(
    [str(ADB_EXE), "pair", ip_porta],
    input=codigo + "\n",
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    creationflags=subprocess.CREATE_NO_WINDOW,
)

    saida = (resultado.stdout + resultado.stderr).strip()

    if "Successfully paired" in saida:
        messagebox.showinfo(
        "Pareamento concluído",
        "Celular pareado com sucesso!\n\nAgora podemos conectar por Wi-Fi.",
    )
    else:
        messagebox.showerror(
        "Erro no pareamento",
        f"Não foi possível parear.\n\n{saida}",
    )
        # =========================
# INTERFACE GRÁFICA
# =========================

janela = tk.Tk()
janela.title("Espelhamento Android")
janela.geometry("500x600")

texto_status = tk.StringVar(value="Nenhum celular conectado")
texto_qr = tk.StringVar(value="")

label_qrcode = tk.Label(janela)
label_qrcode.pack(pady=10)

label_status = tk.Label(
    janela,
    textvariable=texto_status,
    font=("Arial", 11),
)
label_status.pack(pady=10)

botao_atualizar = tk.Button(
    janela,
    text="Atualizar status",
    command=atualizar_status,
)
botao_qr = tk.Button(
    janela,
    text="Gerar QR Code",
    command=iniciar_pareamento_qr,
)
botao_qr.pack(pady=10)

botao_atualizar.pack(pady=10)
botao_iniciar = tk.Button(
    janela,
    text="Iniciar espelhamento",
    command=iniciar_espelhamento,
)
botao_iniciar.pack(pady=10)
botao_tela_desligada = tk.Button(
    janela,
    text="Iniciar    com tela desligada",
    command=iniciar_tela_desligada,
)
botao_tela_desligada.pack(pady=10)

janela.mainloop()