# SIGETEC

Sistema de Gerenciamento de Chamados Técnicos — Projeto Integrador ADS / UNISA.

O projeto foi reiniciado com foco em simplicidade e execução local sem Docker,
PostgreSQL ou acesso a CDNs. A interface usa HTML e CSS locais.

## Fase 1 — Base da aplicação

```bash
python -m venv .venv
```

Ative o ambiente:

- Linux/macOS: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows Prompt de Comando: `.venv\Scripts\activate.bat`

```bash
python -m pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000/. Use Python 3.11 ou superior. Não é necessário
configurar variáveis para testar a página inicial.

A fábrica `create_app()` monta a aplicação. `app.py` inicia o servidor local.
As funcionalidades serão adicionadas em fases registradas por commits.
