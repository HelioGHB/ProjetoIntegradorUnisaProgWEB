# Publicação simples no Render

A aplicação roda localmente com SQLite. No Render, utiliza PostgreSQL para
preservar dados entre reinícios. O serviço Flask é executado pelo Gunicorn.
Não é necessário Docker nem GitHub Pages.

## Antes de começar

- Código enviado ao [repositório do projeto](https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB).
- Acesso autenticado ao Render e escolha de um plano.
- Um banco PostgreSQL **novo**, separado dos bancos anteriores.

O `render.yaml` é uma configuração preparada, não um deploy já realizado.
Auto-Deploy está Off para permitir testar e revisar cada fase antes de publicar.
O arquivo não cria banco ou aplica mudanças no banco automaticamente.

## 1. PostgreSQL e custo

Crie um PostgreSQL no Render, preferencialmente versão principal 18, na mesma
região do serviço (o arquivo sugere Virginia). Use usuário próprio da aplicação;
o código recusa `postgres`. Guarde a URL em variáveis privadas.

Referência consultada em 6/11/2026: o serviço web gratuito pausa após 15 minutos
sem tráfego. O banco PostgreSQL gratuito expira em 30 dias, não possui backups
e pode ser excluído pelo provedor depois do prazo de recuperação. Para avaliação
por um período maior, considere banco pago. A referência inicial de computação
paga é cerca de US$ 7/mês para web e US$ 6/mês para banco, além de armazenamento
e eventuais adicionais. Confirme o preço final no painel antes de contratar.

## 2. Inicializar o banco vazio

Esta versão simples usa um comando explícito `init-db`, sem Alembic. Ele cria
as três tabelas somente em banco vazio e recusa outra estrutura existente.
Repeti-lo em uma estrutura reconhecida não modifica tabelas. Ele não atualiza
um esquema antigo: futuras alterações de estrutura precisarão de uma migração
planejada. Nenhum banco anterior foi apagado ou convertido durante o reinício.

Para preparar o banco remoto no computador local, crie um arquivo privado
`.env.hospedagem`, ignorado pelo Git, preenchido no editor com:

```dotenv
APP_ENV=production
DATABASE_URL=URL_EXTERNA_PRIVADA_DO_POSTGRESQL
SECRET_KEY=CHAVE_ALEATORIA_PRIVADA_COM_PELO_MENOS_32_CARACTERES
TRUSTED_HOSTS=localhost
DEMO_MODE=true
```

Os valores são marcadores, não credenciais utilizáveis. A produção adiciona
`sslmode=require` à URL caso o parâmetro não esteja presente; não permite modo
SSL inseguro. Se o provedor exigir verificação de certificado, configure a URL
conforme suas instruções. No Render, restrinja o acesso externo ao seu IP antes
de conectar do computador local.

Após confirmar que a URL aponta para o banco **novo de demonstração**, execute:

```bash
flask --env-file .env.hospedagem --app app preparar-demo
```

O comando cria as tabelas e pede uma senha oculta para as três contas fictícias.
Não existe senha padrão. Se já houver usuários, interrompe sem sobrescrever.
Variáveis já exportadas no terminal têm prioridade sobre esse arquivo; confira
que não há configurações de outro banco exportadas. Não use o banco antigo.
Depois da preparação, restrinja novamente o acesso externo ao banco.

No plano pago também é possível usar o Shell do Render, com as variáveis do
serviço e `DEMO_MODE=true`, executando `flask --app app preparar-demo`.
Desative DEMO_MODE depois. O plano gratuito não possui Shell remoto.

## 3. Web Service

No Render, crie **Web Service**, conecte o repositório e configure:

| Campo | Valor |
| --- | --- |
| Runtime | Python 3 |
| Região | Mesma do banco |
| Build | `pip install -r requirements-render.txt` |
| Start | `gunicorn --config gunicorn.conf.py 'sigetec:create_app()'` |
| Health Check | `/healthz` |
| Auto-Deploy | Off |

Variáveis privadas/configuração no painel:

- `APP_ENV=production`
- `PYTHON_VERSION=3.14.7` (versão usada nos testes locais)
- `DATABASE_URL`: URL **interna** do PostgreSQL do Render na mesma região.
- `SECRET_KEY`: chave privada aleatória com pelo menos 32 caracteres; o Blueprint
  pode gerá-la. Não copie um valor público de exemplo.
- `DEMO_MODE=false`, após criar a demonstração.

`RENDER_EXTERNAL_HOSTNAME` fornece o domínio padrão permitido. Para domínio
próprio, informe `TRUSTED_HOSTS` com os hosts separados por vírgula, incluindo o
domínio do Render e os domínios verificados usados pelos health checks.

Em produção, cookies são seguros, a chave é obrigatória, debug é recusado e
somente PostgreSQL com TLS é aceito. O proxy HTTPS frontal é reconhecido pelo
protocolo encaminhado; não se confia em Host ou IP encaminhados pelo cliente.
Esta configuração pressupõe hospedagem atrás de proxy confiável, como o Render.

O health check só responde 200 após conexão e acesso à tabela de usuários.
Prepare o banco **antes do primeiro deploy**, senão ele responderá 503.
Criar o serviço/Blueprint já inicia a primeira implantação; não basta o código
estar no GitHub. Depois, faça deploy manual para cada nova fase publicada.

## 4. Professor

Após o deploy, abra a URL HTTPS fornecida pelo Render e execute o roteiro do
README. Envie a URL e a senha escolhida ao professor por canal privado. Não
publique credenciais administrativas no GitHub. Acesso online só pode ser
confirmado depois de testar a implantação real. A execução local funciona
independentemente dessa hospedagem.

Fontes oficiais consultadas:
[Flask no Render](https://render.com/docs/deploy-flask),
[Python](https://render.com/docs/python-version),
[PostgreSQL](https://render.com/docs/postgresql-creating-connecting),
[limitações gratuitas](https://render.com/docs/free),
[preços](https://render.com/pricing),
[Blueprint](https://render.com/docs/blueprint-spec).
