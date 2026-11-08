> Migração de endereço em andamento: o novo serviço ainda aguarda configuração e validação online.
> As validações anteriores se referem à instância original. Veja [migração](migracao-endereco.md).

# Inicializar o PostgreSQL do sigetec-chamados sem Shell

Serviço informado pelo responsável: **sigetec-chamados**, já com status Live.
URL: https://sigetec-chamados.onrender.com

**Estado atual:** a inicialização e o primeiro login já foram concluídos e
validados. As flags foram desativadas e os três valores temporários de cadastro
foram esvaziados na entrega de 7/11/2026, preservando os dados e credenciais
principais. Este guia é referência para uma instalação nova ou recuperação
planejada; não repita o procedimento para usar o sistema já publicado.

O plano gratuito não disponibiliza Shell/SSH, tarefas avulsas ou comando de
pré-deploy pago. Usaremos o **Start Command do serviço existente**, sem criar
outro serviço, alterar plano ou abrir uma rota pública de administração.

## O que o código faz

`python -m flask --app app inicializar-deploy` é não interativo e controlado
por variáveis privadas, desativadas por padrão:

| Variável | Finalidade |
| --- | --- |
| INIT_DB_ON_START | Com `true`, permite criar as tabelas se o banco estiver vazio |
| CREATE_ADMIN_ON_START | Com `true`, permite criar o primeiro administrador |
| BOOTSTRAP_ADMIN_NAME | Nome do primeiro administrador |
| BOOTSTRAP_ADMIN_EMAIL | E-mail escolhido, validado e normalizado |
| BOOTSTRAP_ADMIN_PASSWORD | Senha privada de 12 a 128 caracteres, sem valor padrão |

As tabelas são `usuarios`, `chamados` e `comentarios`. A inicialização não usa
`DROP`, `TRUNCATE`, exclusões, redefinições de senha ou alterações de tabelas.
Se já houver o esquema reconhecido, preserva as tabelas. Se os nomes de tabelas
ou colunas não corresponderem ao modelo, interrompe para revisão. Essa checagem
não substitui uma ferramenta de migração nem uma comparação completa de tipos
e restrições. Não force a inicialização em um esquema incompatível.

Quando solicitado, o administrador é criado com hash de senha. Se já houver
um administrador, inclusive inativo, nenhuma conta, senha ou estado é alterado.
Se o e-mail escolhido pertencer a outro perfil, a operação é recusada sem
promover esse usuário. Dados de cadastro inválidos são recusados antes de criar
tabelas. Não são criados técnico ou solicitante automaticamente.

No PostgreSQL, as operações são feitas numa transação com bloqueio consultivo
para evitar disputa entre duas inicializações simultâneas. O bloqueio é liberado
pelo banco ao concluir a transação. Os logs mostram somente resultados genéricos;
não imprimem conexão, nome, e-mail, senha ou hash do administrador.

## 1. Confirmar o destino

No painel Render, abra o serviço **já existente** `sigetec-chamados`.
Confirme privadamente que `DATABASE_URL` aponta para o PostgreSQL hospedado
correto. Não copie seu valor para o repositório, comandos, prints ou mensagens.

Mantenha as configurações existentes:

- `APP_ENV=production`
- `DATABASE_URL`: conexão PostgreSQL do serviço, preferencialmente interna na
  mesma conta e região; o código exige TLS.
- `SECRET_KEY`: chave privada já configurada. **Não gere outra chave** para
  inicializar tabelas.

Não importe um novo Blueprint nem crie outro banco/serviço para esta operação.

## 2. Adicionar as variáveis temporárias

Em **Environment**, adicione:

```dotenv
INIT_DB_ON_START=true
CREATE_ADMIN_ON_START=true
```

Adicione também, com seus próprios valores privados:

- `BOOTSTRAP_ADMIN_NAME`: nome escolhido.
- `BOOTSTRAP_ADMIN_EMAIL`: e-mail válido que será usado no login.
- `BOOTSTRAP_ADMIN_PASSWORD`: senha forte escolhida, entre 12 e 128 caracteres.

Não use `ADMIN@example.com` ou uma senha publicada como cadastro padrão: nenhum
valor de conta é imposto pelo código. Guarde a senha em local privado.
Não é preciso habilitar `DEMO_MODE`.

Se desejar **somente as tabelas**, use `CREATE_ADMIN_ON_START=false` e não
adicione as três variáveis de administrador.

Se disponível no menu de salvar, escolha **Save only** enquanto prepara as
alterações. As novas variáveis serão aplicadas no próximo deploy. Não coloque
os valores das credenciais no Build Command ou no Start Command.

## 3. Ajustar o Start Command

Em **Settings > Build & Deploy**, confira:

**Build Command** (já utilizado pelo projeto):

```bash
pip install -r requirements-render.txt
```

**Start Command** (copie a linha completa):

```bash
python -m flask --app app inicializar-deploy && gunicorn --config gunicorn.conf.py 'sigetec:create_app()'
```

O `&&` só inicia o servidor se a inicialização terminar com sucesso. Com as duas
flags desativadas, o comando termina sem acessar o banco e inicia normalmente
o Gunicorn. Nenhuma inicialização foi colocada dentro de `create_app()`.

O `render.yaml` contém esse comando e mantém as flags `false` como padrão
seguro para novas configurações. Editar o YAML no GitHub **não garante** que um
serviço criado manualmente adote o comando: confira o campo no painel do
serviço atual. Não altere o plano de hospedagem.

## 4. Publicar a versão correta e verificar

Em **Manual Deploy > Deploy latest commit**, publique a versão da branch `main`
que contém o comando `inicializar-deploy`. Não use apenas um restart de um build
antigo: ele ainda pode não conter o código novo.

Nos logs, o primeiro sucesso deverá apresentar:

```text
Tabelas criadas.
Administrador criado.
```

Se já existirem, os resultados serão mensagens de preservação. Se houver erro,
o Gunicorn não iniciará nessa tentativa; revise variáveis, conexão, permissões
e estrutura sem apagar o banco. Não execute `drop_all()`, SQL de limpeza ou
redefinição de contas para contornar a falha.

Confirme:

1. https://sigetec-chamados.onrender.com/healthz — esperado: HTTP 200 e
   `{"status":"ok"}`.
2. https://sigetec-chamados.onrender.com/login — entre com o e-mail e senha escolhidos.
3. Verifique que a página de chamados mostra o perfil **administrador**.

O health check sozinho confirma conexão e tabela de usuários, mas não prova
que um administrador foi criado. Verifique também os logs e o login.

## 5. Desativar após o sucesso

Depois de confirmar o primeiro login, em **Environment**:

```dotenv
INIT_DB_ON_START=false
CREATE_ADMIN_ON_START=false
```

Remova `BOOTSTRAP_ADMIN_NAME`, `BOOTSTRAP_ADMIN_EMAIL` e
`BOOTSTRAP_ADMIN_PASSWORD`. Mantenha `SECRET_KEY`, `DATABASE_URL` e
`APP_ENV=production`. Salve e aplique as variáveis com novo deploy.

Mantenha o novo Start Command: com as flags desativadas, ele mostra que a
inicialização está desativada e inicia o servidor sem modificar o banco.
Faça login novamente para confirmar a persistência após o redeploy.
Os dados ficam no PostgreSQL, não no sistema de arquivos temporário do serviço.

O banco gratuito do Render tem prazo de validade próprio. Este procedimento
não altera esse prazo nem muda o plano.

## Alternativa: executar do computador local

É possível conectar à **URL externa** do mesmo banco com TLS e acesso externo
restrito ao seu IP. Isso não exige Shell no Render. Instale as dependências:

```bash
python -m pip install -r requirements-render.txt
```

Prepare privadamente `.env.hospedagem`, já ignorado pelo Git:

```dotenv
APP_ENV=production
DATABASE_URL=URL_EXTERNA_PRIVADA_DO_BANCO_CORRETO
SECRET_KEY=CHAVE_PRIVADA_DE_PELO_MENOS_32_CARACTERES_PARA_A_CLI
TRUSTED_HOSTS=localhost
```

Os valores são marcadores para preencher no editor, não credenciais reais.
A chave da CLI pode ser própria, pois esse processo não serve sessões web;
não substitua a SECRET_KEY do serviço. Variáveis já exportadas no terminal têm
prioridade sobre o arquivo: confira o ambiente antes de executar.

```bash
python -m flask --env-file .env.hospedagem --app app init-db
python -m flask --env-file .env.hospedagem --app app criar-admin
```

`criar-admin` pede nome, e-mail e senha oculta com confirmação. Ele não cria
contas de outros perfis e não altera um administrador já existente. Depois,
restrinja novamente o acesso externo ao banco. As variáveis `INIT_DB_ON_START`
e `CREATE_ADMIN_ON_START` não são necessárias nesta alternativa interativa.

## Validação e limites desta entrega

A entrega original do bootstrap executou 51 testes. A suíte atual executou
**69 testes aprovados**, em SQLite exclusivamente em memória, sem usar o
PostgreSQL hospedado. Cobrem o primeiro cadastro, repetição, preservação de
senhas/contas inativas, conflito de e-mail, esquema incompatível, flags
desativadas e falhas sem exposição de credenciais.
Também foram verificados num PostgreSQL temporário isolado a criação,
persistência, repetição sem redefinir senha, rollback completo de DDL após
falha simulada e duas inicializações simultâneas criando um único administrador.
Esse servidor de teste foi encerrado; nenhum banco existente foi acessado.
A inicialização hospedada foi posteriormente confirmada pelos logs do Render e
pelo login e roteiro de atendimento validados pelo responsável. O deploy e a
saúde HTTP também foram verificados. O registro atual está em `docs/entrega.md`.
Publicar código na `main`, isoladamente, não comprova uma inicialização.

Referências oficiais:
[limitações do plano gratuito](https://render.com/docs/free),
[variáveis privadas e aplicação no deploy](https://render.com/docs/configure-environment-variables),
[conexões PostgreSQL](https://render.com/docs/postgresql-creating-connecting).
