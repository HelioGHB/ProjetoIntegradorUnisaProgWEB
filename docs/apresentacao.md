> Migração de endereço em andamento: o novo serviço ainda aguarda configuração e validação online.
> As validações anteriores se referem à instância original. Veja [migração](migracao-endereco.md).

# Roteiro de apresentação do SIGETEC

Duração sugerida: **8–10 minutos**, adaptável ao tempo definido pelo professor.
Este roteiro apresenta somente recursos implementados e testados.

## Antes da apresentação

- Abra https://sigetec-chamados.onrender.com e confira `/healthz`.
- Tenha acesso privado às contas de administrador, técnico e solicitante já
  cadastradas. Não mostre senhas, variáveis do Render ou arquivos `.env`.
- Use **Sair** ao trocar de perfil, ou três perfis separados de navegador.
  Janelas anônimas do mesmo navegador podem compartilhar cookies.
- Reutilize as contas existentes; não execute bootstrap ou `preparar-demo` no
  banco hospedado já inicializado.
- Prepare um chamado fictício para contingência e tenha as três imagens do
  README disponíveis. Não use informações reais de pessoas ou incidentes.
- Tenha a execução local preparada caso a internet ou hospedagem não responda.
  A instalação de dependências precisa ser feita antes, com internet.
- Os planos gratuitos têm limites próprios. Confira disponibilidade e validade
  do banco no painel antes do dia da avaliação, sem mudar de plano por impulso.

## Sequência e fala sugerida

| Tempo | Mostrar | Fala sugerida |
| --- | --- | --- |
| 0:00–0:45 | Página inicial | “Este é o SIGETEC, Sistema de Gerenciamento de Chamados Técnicos, desenvolvido como projeto independente.” |
| 0:45–1:30 | Problema e objetivo | “O objetivo é organizar solicitações de suporte, indicar um responsável e permitir que o solicitante acompanhe o atendimento.” |
| 1:30–2:15 | README ou estrutura | “Usei Flask no backend, SQLAlchemy no acesso aos dados e HTML/CSS na interface. Localmente o projeto usa SQLite; na hospedagem usa PostgreSQL.” |
| 2:15–6:15 | Demonstração abaixo | “Vou demonstrar o mesmo chamado passando pelos três perfis, com permissões diferentes.” |
| 6:15–7:15 | Usuários e acesso negado | “O administrador cadastra técnicos e solicitantes. O backend protege as ações; esconder um botão não seria suficiente.” |
| 7:15–8:15 | Testes e modelagem | “Há 69 testes automatizados isolados, cobrindo login, permissões, integridade e atendimento. O modelo usa usuários, chamados e comentários.” |
| 8:15–9:00 | Conclusão e limites | “O fluxo básico foi entregue e validado online. Mantive o escopo acadêmico sem anexos, relatórios ou notificações por e-mail.” |

Ajuste as falas ao seu modo de explicar; não é necessário decorar o texto.
Reserve o tempo restante para perguntas.

## Demonstração prática — um chamado do início ao fim

### 1. Solicitante: abrir e acompanhar

Entre como solicitante e clique em **Abrir chamado**:

- Título: `Demonstração do PI — computador sem acesso à rede`.
- Descrição: `O computador do laboratório não acessa a rede. Solicito verificação da conexão.`
- Prioridade: `alta`.

Registre e aponte o número, o autor e a situação inicial **aberto**.
Explique: “O solicitante é obtido da sessão, não informado pelo navegador.”
Use **Sair**.

### 2. Administrador: atribuir o atendimento

Entre como administrador, abra o chamado e selecione o técnico fictício já
cadastrado. Clique em **Salvar responsável**.
Explique: “O administrador vê todos os chamados e define quem atende.”
Use **Sair**.

### 3. Técnico: atender e registrar a solução

Entre como o técnico escolhido. O chamado atribuído aparece na listagem:

1. Mude a situação para **em andamento** e salve.
2. Registre o comentário: `Cabo de rede verificado e substituído. Conexão testada com sucesso.`
3. Mude a situação para **resolvido** e salve.

Explique: “O técnico só acessa chamados atribuídos a ele.” Use **Sair**.

### 4. Solicitante: conferir a resolução

Entre novamente como solicitante. Mostre o comentário do técnico e a situação
**resolvido**. Registre: `Conexão funcionando. Atendimento confirmado.`
Explique: “O solicitante acompanha e comenta, mas não atribui técnicos ou
altera a situação.”

### 5. Demonstrar permissões e gestão de usuários

- Ainda como solicitante, abra `/usuarios`: deve apresentar acesso negado.
- Entre como administrador e mostre **Usuários**, **Cadastrar usuário** e as
  opções de ativação/desativação. Não exiba ou digite senhas diante da audiência.
- Se precisar cadastrar durante a apresentação, use somente dados fictícios e
  faça a etapa da senha de forma privada. Não é necessário cadastrar de novo
  as contas já preparadas para avaliar o fluxo.
- Opcionalmente, feche o chamado como administrador e explique que somente
  esse perfil pode reabri-lo. Não é necessário alterar contas administrativas.

## Explicação técnica curta

- **Flask/fábrica:** `create_app()` concentra a configuração e facilita usar um
  banco isolado nos testes.
- **ORM/relacionamentos:** um chamado referencia um solicitante e, opcionalmente,
  um técnico; ambos são usuários. As chaves estrangeiras são declaradas
  explicitamente para distinguir os papéis.
- **Senhas/sessões:** Werkzeug deriva hashes com salt. Flask-Login identifica
  a sessão; Flask-WTF valida CSRF nos formulários.
- **Permissões:** o servidor filtra consultas e recusa ações de outro perfil,
  mesmo que alguém altere a URL ou envie um formulário manualmente.
- **Persistência:** SQLite local facilita a execução pelo professor. No Render,
  o PostgreSQL é separado do serviço Flask e preserva dados em reinícios do web.
- **Inicialização:** foi explícita e validada. Não se apagam tabelas para iniciar
  a aplicação, e a rotina opcional de bootstrap fica desativada após o sucesso.

## Perguntas possíveis

**Por que SQLite local e PostgreSQL online?**
SQLite reduz a preparação local. PostgreSQL oferece armazenamento separado do
serviço hospedado. Os modelos SQLAlchemy são compartilhados entre os ambientes.

**O administrador pode apagar contas ou chamados?**
Não. Há ativação/desativação de técnicos e solicitantes, preservando os vínculos.
Não existe exclusão pela interface.

**Como você sabe que as permissões funcionam?**
Além da validação manual relatada, os testes verificam acessos por perfil, URLs
de chamados de outras pessoas, CSRF e revogação de sessão após desativação.

**Os testes usam o banco real?**
Não. A suíte usa SQLite em memória. A verificação adicional de comportamento
PostgreSQL foi feita em um servidor temporário, não no banco hospedado.

**O que ainda não foi implementado?**
Anexos, relatórios, categorias, envio de e-mail, histórico de auditoria separado,
edição de perfil e troca de senha por interface. São possibilidades futuras,
sem serem apresentadas como entregas desta versão.

**Onde está o histórico do projeto?**
Na branch `main` do GitHub. `docs/fases.md` relaciona os commits e as validações.

## Contingência

Se a hospedagem ou internet falhar, informe a limitação e use a execução local
já preparada. As três imagens no README são capturas reais de uma instância
local com dados fictícios e podem apoiar a explicação. Não as apresente como
prova de uma execução online que não foi realizada naquele momento.

## Reproduzir as capturas (opcional)

Esta etapa é apenas para renovar as imagens da documentação. Não é necessária
para executar ou avaliar o projeto.

Com o ambiente virtual ativo e as dependências locais instaladas:

```bash
python -m pip install playwright==1.64.1
python -m playwright install chromium
python scripts/capturar_telas.py
```

O script inicia um servidor HTTP local, usa um SQLite temporário, cria dados
fictícios com senhas aleatórias não exibidas e captura três páginas reais em
Chromium com resolução de 1440 pixels de largura. Ao terminar, encerra servidor
e navegador e remove somente seu diretório temporário. Não conecta ao
PostgreSQL hospedado, não usa contas reais e não imprime senhas.
Os PNGs ficam em `docs/images/`. As senhas não aparecem nas capturas.
A execução das capturas foi validada em Linux; Playwright pode requerer
bibliotecas de sistema dependendo do sistema operacional.
