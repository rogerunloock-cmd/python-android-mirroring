import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


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

    comando = [
        str(SCRCPY_EXE),
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

    texto_status.set("Espelhamento iniciado com a tela desligada")


# Criação da janela
janela = tk.Tk()
janela.title("Espelhamento Android")
janela.geometry("430x300")
janela.resizable(False, False)

titulo = tk.Label(
    janela,
    text="Controle de espelhamento",
    font=("Arial", 18, "bold"),
)
titulo.pack(pady=20)

texto_status = tk.StringVar(
    value="Clique em verificar celular"
)

status = tk.Label(
    janela,
    textvariable=texto_status,
    font=("Arial", 11),
)
status.pack(pady=10)

botao_verificar = tk.Button(
    janela,
    text="Verificar celular",
    command=atualizar_status,
    width=30,
    height=2,
)
botao_verificar.pack(pady=5)

botao_espelhar = tk.Button(
    janela,
    text="Iniciar espelhamento",
    command=iniciar_espelhamento,
    width=30,
    height=2,
)
botao_espelhar.pack(pady=5)

botao_tela_off = tk.Button(
    janela,
    text="Espelhar e desligar tela do celular",
    command=iniciar_tela_desligada,
    width=30,
    height=2,
)
botao_tela_off.pack(pady=5)

janela.mainloop()
