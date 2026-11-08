> Migração de endereço em andamento: o novo serviço ainda aguarda configuração e validação online.
> As validações anteriores se referem à instância original. Veja [migração](migracao-endereco.md).

# Relatório de entrega — 7 de novembro de 2026

## Estado funcional

- Código publicado em https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB.
- Aplicação em https://sigetec-chamados.onrender.com, serviço `sigetec-chamados`.
- Fase funcional 4, commit `bbb5549`, confirmada Live pelo Render.
- PostgreSQL hospedado e primeiro administrador inicializados; logs de criação
  foram confirmados. Contas fictícias de técnico e solicitante foram cadastradas
  pelo responsável, que relatou sucesso no roteiro completo online.
- A versão local funciona sem PostgreSQL, Docker, Render ou `.env` obrigatório.

## Entregas

| Item | Situação |
| --- | --- |
| Login/logout, sessões e hash de senha | Implementado |
| Três perfis com validação no backend | Implementado |
| Abertura, atribuição e atualização de chamados | Implementado |
| Comentários e registro de solução | Implementado |
| Cadastro de técnicos e solicitantes pelo administrador | Implementado |
| Ativação/desativação preservando os registros | Implementado |
| Inicialização explícita e segura de banco/administrador | Implementado |
| Execução local e hospedada | Disponíveis |
| Roteiro de apresentação | `docs/apresentacao.md` |
| Três capturas reais sem credenciais | README e `docs/images/` |
| Código e histórico por fases | Branch `main` |

## Evidências e seus limites

1. **Automatizado:** 69 testes pytest aprovados novamente nesta entrega, em
   SQLite em memória. Incluem CSRF, perfis, privacidade, integridade, bootstrap,
   gestão de usuários e fluxo de atendimento. Não alteram o banco online.
2. **PostgreSQL isolado:** validação adicional anterior de persistência,
   preservação de senha, rollback de DDL e duas inicializações simultâneas.
   O servidor temporário foi encerrado.
3. **Navegador real:** três screenshots em Chromium, com SQLite temporário e
   dados fictícios, gerados pelo script versionado. Mostram login, listagem e
   atendimento resolvido. As imagens foram revisadas antes da publicação.
4. **Hospedagem:** deploy Live confirmado por ferramenta do Render, além de
   respostas HTTP 200 em `/healthz` e `/login` e redirecionamento ao login para
   `/usuarios` sem sessão.
5. **Aceitação manual:** o responsável informou que os perfis e o ciclo completo
   funcionaram online. O assistente não utilizou senhas reais nem fez login
   nessas contas.

Windows/macOS não foram testados. Os comandos estão documentados, mas a
validação de instalação ocorreu em Linux com Python 3.14.7. O comportamento de
cada ambiente não deve ser apresentado como testado sem execução correspondente.

## Operação após a inicialização

A inicialização já foi concluída. Não é necessário repeti-la, recriar o banco
ou redefinir contas. As flags de bootstrap devem permanecer desativadas e seus
valores temporários vazios/removidos. Nesta entrega, `INIT_DB_ON_START` e `CREATE_ADMIN_ON_START` foram definidos
como `false`, e os valores de `BOOTSTRAP_ADMIN_NAME`, `BOOTSTRAP_ADMIN_EMAIL` e
`BOOTSTRAP_ADMIN_PASSWORD` foram esvaziados. As chaves temporárias podem
continuar presentes sem valor; o segredo temporário não foi mantido.
A atualização parcial preservou todas as outras variáveis. O redeploy
`dep-dbnm3o3m8hqs73cjp5m0` foi confirmado Live com o mesmo código funcional.
Não houve mudança de plano, conexão, chave de sessão ou contas existentes.

O banco permanece com acesso externo restrito. Não foram alterados planos,
allowlists ou dados existentes. Uma consulta SQL pelo MCP foi bloqueada por
essa política; a restrição foi preservada.

## Limites deliberados

Sem exclusão de registros, cadastro público, anexos, relatórios, categorias,
notificações por e-mail, auditoria separada, edição de perfil ou recuperação de
senha pela interface. Os comentários registram o atendimento e a solução.
`init-db` verifica nomes de tabelas/colunas e não é uma ferramenta de migração.
Evoluções de esquema precisam de planejamento e não devem apagar dados.

## Pendências externas e manutenção

- Conferir disponibilidade antes da avaliação: o inventário do Render consultado
  em 7/11/2026 informa expiração do PostgreSQL gratuito em **6/12/2026**.
  Essa validade é controlada pelo provedor; não houve alteração de plano.
- Manter os acessos do professor em canal privado; não publicar senhas no
  README, artigo, slides ou imagens.
- Conferir o commit efetivamente Live depois de cada nova fase. O serviço
  indicou Auto-Deploy ativo, mas a fase 4 precisou de publicação manual.
- Gerar exportação privada do PostgreSQL antes de mudanças futuras relevantes,
  conforme as possibilidades do plano e a política de acesso. Nenhum backup
  do banco real foi solicitado ou criado nesta entrega.

Não há funcionalidade adicional prometida como pendência obrigatória desta
versão acadêmica. O roteiro completo foi aceito pelo responsável. Requisitos
formais específicos do professor/rubrica não foram fornecidos e precisam ser
comparados com o escopo se forem exigidos posteriormente.
