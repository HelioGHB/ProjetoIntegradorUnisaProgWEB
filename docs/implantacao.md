# Operação do SIGETEC no Render

## Instalação atual

- Serviço existente: **sigetec-unisa**.
- URL: https://sigetec-unisa.onrender.com.
- Fonte: branch `main` de https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB.
- Execução: Flask/Gunicorn, com PostgreSQL hospedado separado, na mesma região.
- Planos existentes preservados; nenhum serviço adicional é necessário.
- Banco e contas já inicializados. O responsável validou o atendimento online.

O professor usa o navegador e recebe acessos privadamente. Não precisa instalar
Python ou conectar diretamente ao banco para testar online.
Para executar localmente, siga o README: SQLite é usado por padrão, sem Docker.

## Configuração de referência

| Campo | Valor |
| --- | --- |
| Build | `pip install -r requirements-render.txt` |
| Start | `python -m flask --app app inicializar-deploy && gunicorn --config gunicorn.conf.py 'sigetec:create_app()'` |
| Porta | Gunicorn usa `0.0.0.0:$PORT` |
| Prontidão da aplicação | `/healthz` |

O arquivo `render.yaml` é referência para provisionamento. Ele não substitui
automaticamente configurações de um serviço criado manualmente. **Não importe
um Blueprint para recriar este serviço só para atualizar documentação.**

Variáveis necessárias em produção:

| Variável | Uso |
| --- | --- |
| APP_ENV | `production` |
| DATABASE_URL | URL PostgreSQL privada, preferencialmente interna na mesma região |
| SECRET_KEY | Chave privada estável com pelo menos 32 caracteres |
| PYTHON_VERSION | `3.14.7`, versão usada na validação Linux |
| TRUSTED_HOSTS | Opcional para o domínio padrão; obrigatório incluir domínios próprios quando usados |

O Render fornece o hostname padrão. A aplicação exige TLS na conexão
PostgreSQL, cookies seguros e debug desativado em produção. A configuração de
proxy pressupõe um proxy frontal confiável, como o Render, e não confia em Host
ou IP encaminhados pelo cliente. Nunca publique URLs de banco ou chaves.

`/healthz` faz consultas somente de leitura para confirmar conexão e acesso à
tabela de usuários. HTTP 200 não substitui a validação do login e das permissões.
O serviço real deve usar essa rota como health check se a configuração no painel
for atualizada; a consulta de inventário anterior mostrou o campo do painel
vazio, embora a rota esteja funcionando. Não é necessário alterar o serviço
para apresentar esta versão já validada.

## Depois da inicialização

Mantenha:

```dotenv
INIT_DB_ON_START=false
CREATE_ADMIN_ON_START=false
```

Os três valores `BOOTSTRAP_ADMIN_*` devem ficar vazios ou removidos. A limpeza
foi aplicada e seu redeploy confirmado nesta entrega, preservando `SECRET_KEY`,
`DATABASE_URL` e demais variáveis. O Start Command pode permanecer: com as flags
desativadas, não executa alterações no banco e inicia o Gunicorn.

Use **Usuários → Cadastrar usuário** para novos técnicos/solicitantes. Não use
`preparar-demo` no banco hospedado que já contém contas. A inicialização sem
Shell está documentada em [inicializacao-render.md](inicializacao-render.md),
apenas como referência para necessidade futura.

## Publicar uma nova versão

1. Teste localmente e confirme que não há credenciais entre os arquivos.
2. Faça commit e push para `main`, preservando o histórico.
3. Confira os eventos do serviço e o commit efetivamente implantado.
4. Se a execução automática não iniciar, revise as credenciais Git no painel.
   A fase 4 precisou de **Manual Deploy → Deploy latest commit**.
5. Aguarde o deploy terminar como Live; valide `/healthz`, `/login` e o fluxo
   alterado. Não dispare outro deploy se já houver um em andamento.

O Blueprint usa Auto-Deploy Off para novos serviços. O serviço existente indicou
automático por commit, mas isso não iniciou a fase 4; a causa não foi comprovada.
A configuração visível não é evidência de que um deploy já começou.
Commits somente de documentação podem usar `[skip render]` para evitar rebuild.

## Persistência e limites

Dados ficam no PostgreSQL e não no sistema de arquivos temporário do serviço.
Nenhum plano foi alterado nesta entrega. Planos gratuitos têm limites e a
validade do banco deve ser conferida no painel antes da avaliação. O inventário
consultado em 7/11/2026 informa expiração do PostgreSQL gratuito em **6/12/2026**. A hospedagem
pode demorar no primeiro acesso após inatividade. Consulte as condições atuais
do provedor antes de depender de uma data de disponibilidade.

O acesso externo ao banco permanece restrito. Não amplie a allowlist apenas
para demonstrar a aplicação. Antes de alterações futuras de esquema, planeje
migração e uma exportação privada quando aplicável. `init-db` não converte
esquemas antigos e não deve ser usado para contornar uma incompatibilidade.

## Referências oficiais

- [Flask no Render](https://render.com/docs/deploy-flask)
- [Variáveis e segredos](https://render.com/docs/configure-environment-variables)
- [Deploys e eventos](https://render.com/docs/deploys)
- [Health checks](https://render.com/docs/health-checks)
- [PostgreSQL e conexões](https://render.com/docs/postgresql-creating-connecting)
- [Limitações gratuitas](https://render.com/docs/free)
