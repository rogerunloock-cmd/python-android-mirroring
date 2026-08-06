# 📱 Espelhamento Android com Python

Aplicação para controlar o espelhamento de dispositivos Android no Windows utilizando **Python**, **scrcpy** e **ADB**. 

## 📑 Índice

- [🎬 Demonstração](#-demonstração)
- [✨ Funcionalidades](#-funcionalidades)
- [⚙️ Requisitos](#-requisitos)
- [🛠️ Tecnologias](#-tecnologias)
- [▶️ Como usar](#-como-usar)
- [🚀 Como executar](#-como-executar)
- [📄 Licença](#-licença)

---

<p align="center">
  <img src="screenshots/interface.png" width="900">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge">
  <img src="https://img.shields.io/badge/Windows-10+-0078D6?style=for-the-badge">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</p>

---

## 🎬 Demonstração

<p align="center">
  <img src="screenshots/demo.gif" width="900">
</p>

---

## ✨ Funcionalidades

- 📱 Detecta dispositivos Android conectados
- 🖥️ Inicia o espelhamento da tela
- 🔒 Permite espelhar com a tela do celular desligada
- ⚠️ Exibe mensagens de erro e status
- 🖱️ Interface gráfica simples em Tkinter

---

## ⚙️ Requisitos

- Windows 10 ou superior
- Python 3.10 ou superior
- Celular Android
- Cabo USB
- Depuração USB ativada
- ADB e scrcpy instalados na pasta `C:\scrcpy`

---

## 🛠 Tecnologias

- Python
- Tkinter
- scrcpy
- ADB

## ▶️ Como usar

1. Ative a **Depuração USB** no Android.
2. Conecte o celular ao computador via USB.
3. Abra o programa.
4. Clique em **Verificar celular**.
5. Autorize a conexão no celular.
6. Clique em **Iniciar espelhamento**.
7. Para desligar a tela do aparelho mantendo o espelhamento, clique em **Espelhar e desligar tela**.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.

---

## 🚀 Como instalar

```bash
git clone https://github.com/rogerunlock-cmd/python-android-mirroring.git

cd python-android-mirroring

python main.py
```

---

## 📂 Estrutura

```
python-android-mirroring/
│
├── screenshots/
│   └── interface.png
├── main.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## 👨‍💻 Autor

Desenvolvido por **Roger Belchior Marcilio**

Se este projeto foi útil para vc deixe uma⭐no repositório!

GitHub:
https://github.com/rogerunloock-cmd