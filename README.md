# SIGETEC

**Sistema de Gerenciamento de Chamados Técnicos** — Projeto Integrador do curso
de Análise e Desenvolvimento de Sistemas da UNISA.

Versão acadêmica simples: login, três perfis e um fluxo básico de suporte.
**Para executar localmente não precisa de PostgreSQL, Docker, Render ou arquivo
`.env`.** O banco SQLite é preparado por um comando e fica na própria máquina.
A interface usa HTML e CSS locais, sem depender de CDN.

## Executar na máquina do professor

Requisito: **Python 3.11 ou superior**, com pip e venv. A instalação das
bibliotecas precisa de internet; depois, a aplicação local funciona sem serviços
externos. A validação foi feita em Linux com Python 3.14.7; não foi executada em
Windows/macOS, mas os comandos de ativação correspondentes estão abaixo.

1. Baixe o código ou clone o repositório, entre na pasta e crie o ambiente:

   ```bash
   git clone https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB.git
   cd ProjetoIntegradorUnisaProgWEB
   python -m venv .venv
   ```

   O clone exige que os commits já tenham sido publicados; se recebeu o projeto
   em ZIP, extraia-o e abra o terminal na pasta que contém `app.py`.
   Se `python` não existir no Linux/macOS, use `python3` para criar o ambiente.
   No Windows, também é possível usar `py -3 -m venv .venv`.

2. Ative o ambiente:

   | Sistema | Comando |
   | --- | --- |
   | Linux/macOS | `source .venv/bin/activate` |
   | Windows PowerShell | `.venv\Scripts\Activate.ps1` |
   | Windows Prompt de Comando | `.venv\Scripts\activate.bat` |

   Se o PowerShell bloquear o script, use o Prompt de Comando ou execute
   diretamente `.venv\Scripts\python.exe` nos comandos Python. Não é necessário
   alterar políticas do sistema.

3. Instale e prepare a demonstração:

   ```bash
   python -m pip install -r requirements.txt
   python -m flask --app app preparar-demo
   ```

   Escolha e confirme uma senha de **12 a 128 caracteres** no terminal.
   A digitação fica oculta. As três contas fictícias usarão essa senha escolhida,
   apenas para facilitar a avaliação. **Não existe senha administrativa fixa no
   código ou neste README.** O comando não altera contas se já houver usuários.

4. Inicie:

   ```bash
   python app.py
   ```

   Abra **http://127.0.0.1:5000/**. Pare o servidor com `Ctrl+C`.
   Nas próximas execuções basta ativar o ambiente e executar `python app.py`.

O banco fica em `instance/sigetec.sqlite3` e não é enviado ao GitHub. Não apague
esse arquivo se quiser manter os chamados. A preparação é explícita; iniciar o
servidor não cria usuários ou recria tabelas.

## Roteiro rápido de avaliação

| Conta fictícia | Perfil |
| --- | --- |
| solicitante@example.com | Solicitante |
| admin@example.com | Administrador |
| tecnico@example.com | Técnico |

Use a senha escolhida durante `preparar-demo`:

1. Entre como **solicitante**, clique em **Abrir chamado** e preencha título,
   descrição e prioridade.
2. Saia e entre como **administrador**. Abra o chamado e atribua **Técnico Demo**.
3. Entre como **técnico**. Atualize a situação para **em andamento**, registre a
   solução nos comentários e marque **resolvido**.
4. Entre novamente como **solicitante** para conferir a solução e comentar.
5. O administrador pode fechar e reabrir o chamado. Um técnico não pode reabrir
   um chamado fechado.

O solicitante visualiza somente os próprios chamados; o técnico visualiza
somente os atribuídos a ele; o administrador visualiza todos. Essas regras
são verificadas no servidor, inclusive ao acessar IDs diretamente pela URL.
O botão **Sair** encerra a sessão.

Não há cadastro público, exclusão de registros, anexos, relatórios ou envio de
e-mail. Para manter o projeto pequeno, categorias e histórico separado ficaram
fora desta versão. Os comentários permitem registrar a conversa e a solução.

## Estrutura e conceitos

```text
app.py                    Inicia o servidor local
config.py                 SQLite local e variáveis da hospedagem
sigetec/
    __init__.py           Fábrica Flask, extensões e tratamento de erros
    models.py             Usuario, Chamado e Comentario
    forms.py              Validação e proteção CSRF dos formulários
    routes.py             Login, chamados e permissões
    cli.py                Inicialização explícita e preparação da demonstração
templates/                HTML e estilo local compartilhado
tests/                    Testes com banco em memória
docs/
    fases.md              Fases, commits e situação da publicação
    modelagem.md          Tabelas e regras de acesso
    implantacao.md        Publicação opcional no Render
gunicorn.conf.py          Servidor para hospedagem
render.yaml               Configuração do serviço Render
requirements.txt          Bibliotecas para execução local
requirements-render.txt   Bibliotecas adicionais para hospedagem
requirements-dev.txt      Bibliotecas adicionais para testes
```

- **Fábrica:** `create_app()` configura a aplicação; nos testes recebe um banco
  diferente, sem acessar dados reais.
- **ORM:** os modelos Python representam tabelas. SQLAlchemy faz consultas e
  controla transações com `commit()` e `rollback()`.
- **Autenticação:** Flask-Login mantém a identidade na sessão. Werkzeug salva
  hash de senha; Flask-WTF protege os formulários com CSRF.
- **Autorização:** as rotas conferem o perfil e a relação do usuário com o chamado.

As restrições do banco e o modelo estão em [docs/modelagem.md](docs/modelagem.md).

## Configuração opcional e dados anteriores

Localmente, uma chave de sessão aleatória é gerada a cada inicialização se
SECRET_KEY não estiver configurada; reiniciar encerra as sessões antigas, mas
preserva usuários e chamados. Para manter a chave entre reinícios, copie
`.env.example` para **`.env.local`** e configure SECRET_KEY privadamente.
Nunca publique esses arquivos. Não é necessário fazer isso para a avaliação local.

Os arquivos `.env` e bancos do projeto anterior foram preservados. A fábrica
local lê apenas `.env.local`; a CLI do Flask também pode carregar `.env`, mas,
em `APP_ENV=development`, DATABASE_URL é ignorada e o banco é sempre SQLite.
Não defina APP_ENV=production para o teste local do professor.

`python -m flask --app app init-db` cria somente as tabelas de um banco vazio.
Não apaga tabelas ou dados. Se encontrar estrutura incompatível, recusa o banco.
Não é uma migração automática: alterações futuras precisam de atualização de
esquema planejada. Não aponte esta versão para bancos antigos para tentar
convertê-los. O reinício não executou comandos nos bancos PostgreSQL anteriores.

## Testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip check
```

Os testes usam exclusivamente **SQLite em memória**, com CSRF e chaves
estrangeiras habilitados. Cobrem login, logout, inativos, perfis, privacidade,
abertura, atribuição, comentários, status, reabertura, validação, integridade,
preparação da demonstração e preservação de estrutura incompatível.
A configuração PostgreSQL é montada sem conectar a servidor real.

Verificação realizada em 6/11/2026:

- **36 testes aprovados** em uma cópia do código com ambiente virtual novo.
- Dependências instaladas a partir dos requirements, sem incompatibilidades.
- Preparação de três contas com senha oculta em SQLite temporário.
- Servidor Gunicorn real: início, health check, login com CSRF e abertura de
  chamado aprovados por HTTP na cópia isolada.
- Configuração Gunicorn e compilação dos módulos verificadas sem erro.

Esses testes não acessaram bancos anteriores nem PostgreSQL hospedado.
Windows/macOS e deploy no Render ainda não foram executados.

## GitHub, fases e hospedagem

As entregas são separadas por commits com descrição da fase e da validação.
Veja [docs/fases.md](docs/fases.md) para o histórico e eventuais impedimentos
reais de publicação. Depois de autenticar o Git, o envio normal é:

```bash
git push -u origin main
```

Não use force push. Publicar código no GitHub não cria um endereço web executável.
A execução online precisa de Render e PostgreSQL hospedado, descritos em
[docs/implantacao.md](docs/implantacao.md). O arquivo Render usa Gunicorn e
mantém deploy automático desativado, para publicar cada fase após sua verificação.
Nada depende de GitHub Pages. A execução local funciona sem hospedagem.


## Entrega por ZIP

Quando a publicação no GitHub ainda não estiver disponível, use
`entrega/SIGETEC.zip`, gerado a partir do commit final. O ZIP contém código,
templates, testes e instruções, sem `.env`, `.venv`, histórico Git ou banco.
Extraia e siga a seção **Executar na máquina do professor**. A instalação das
bibliotecas ainda precisa de internet. O ZIP é um artefato local e não faz
parte dos arquivos versionados.
