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

## Fase 2 — Autenticação e chamados

Para preparar o SQLite local e três usuários fictícios:

```bash
flask --app app preparar-demo
```

Escolha uma senha de 12 a 128 caracteres no terminal. Ela não aparece na tela.
Entre em `/login` com `solicitante@example.com`, `admin@example.com` ou
`tecnico@example.com`, usando a senha escolhida. A senha compartilhada é apenas
uma conveniência para a demonstração acadêmica; não há senha fixa no código.

- Solicitante: abre chamados, visualiza e comenta os próprios.
- Administrador: visualiza todos, atribui técnicos e atualiza a situação.
- Técnico: visualiza, comenta e atualiza somente os chamados atribuídos.
- Somente o administrador reabre um chamado fechado.

Os comentários servem também para registrar a solução. Não há exclusão de
chamados ou cadastro público de usuários. O foco é demonstrar um atendimento
simples, sem relatórios, anexos, envio de e-mail ou outras integrações.

O SQLite fica em `instance/sigetec.sqlite3`. A preparação não redefine senhas ou
sobrescreve dados se já houver usuários. Um banco com estrutura diferente é
recusado. Os bancos PostgreSQL e o `.env` do projeto anterior são preservados;
no modo local, DATABASE_URL não é usada.
