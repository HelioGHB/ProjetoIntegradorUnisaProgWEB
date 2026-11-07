# Fases do desenvolvimento

O reinício foi autorizado pelo responsável pelo projeto. O código anterior foi
retirado da aplicação e guardado temporariamente fora do repositório para
recuperação. Credenciais, ambiente virtual e bancos existentes foram preservados.

Cada fase abaixo corresponde a um commit real, sem reconstruir um histórico
fictício. Como não havia identidade Git configurada, os commits usam a autoria
técnica **SIGETEC <sigetec@example.com>**, e não uma identidade pessoal presumida.
O responsável poderá configurar sua autoria para os próximos commits.

| Fase | Entrega | Verificação |
| --- | --- | --- |
| 1 — Base (`f88dd9c`) | Fábrica Flask, página inicial, CSS local e instruções de instalação | Página inicial HTTP 200 |
| 2 — Atendimento básico (`704bc19`) | Login, três perfis, chamados, atribuição, status e comentários | Login e abertura de chamado em SQLite em memória |
| 3 — Entrega (`619a3db`) | Testes automatizados, instalação reproduzível, guia do professor e configuração Render | 36 testes aprovados em instalação limpa e fluxo HTTP real validado |

## Publicação e deploy

O remoto configurado é:
https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB.git

Em 6 de novembro de 2026, os três commits foram publicados com sucesso na
branch `main`, usando a autenticação do GitHub CLI. As tentativas anteriores
pela sessão do VS Code falharam; a nova publicação preservou os três commits
separados e não utilizou force push.

O histórico está disponível em:
https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB/commits/main/

A consulta ao GitHub após o envio não encontrou deployments ou status de
integração Render associados ao commit publicado. Publicar código no GitHub
não cria automaticamente uma aplicação acessível pelo navegador.

O deploy requer um serviço Render conectado e PostgreSQL hospedado configurado.
O responsável informou posteriormente o serviço **sigetec-unisa** como Live,
em https://sigetec-unisa.onrender.com. A consulta anterior ao GitHub representa
apenas o momento anterior a essa implantação. Não houve inicialização remota
do PostgreSQL durante a preparação do novo procedimento sem Shell.
Para cada nova fase, a rotina será:

1. Implementar uma parte pequena e testá-la.
2. Criar commit com fase, mudança e validação.
3. Enviar ao GitHub, preservando o histórico.
4. Executar deploy manual no Render e testar pelo navegador.
5. Registrar URL e resultado real da implantação.

O envio do código foi autorizado. O serviço já está publicado, segundo o
responsável; a execução da inicialização e a confirmação de acesso ao PostgreSQL
hospedado continuam pendentes.
A criação de recursos pagos depende de escolha explícita de plano e custos.


## Inicialização segura do PostgreSQL hospedado

Foi preparada uma etapa opcional no Start Command, sem Shell ou mudança de
plano, para criar tabelas e o primeiro administrador por variáveis privadas.
As flags ficam desativadas por padrão e devem ser desligadas após o sucesso.
Também foi acrescentado `criar-admin` para uso interativo com acesso seguro ao
banco remoto. Veja `docs/inicializacao-render.md` para executar e verificar.

Validação desta atualização: 51 testes pytest aprovados e verificação adicional
em PostgreSQL temporário, incluindo preservação de senha, rollback de DDL e
duas inicializações simultâneas sem duplicar o administrador. Nenhum banco
hospedado foi acessado e nenhum plano foi alterado.


## Fase 4 — Administração de usuários

Cadastro de técnicos e solicitantes pelo administrador em `/usuarios`, com
confirmação de senha e recusa de e-mail duplicado. A listagem permite ativar e
desativar contas sem excluir chamados ou comentários. Contas administrativas
não podem ser bloqueadas nem criadas por esse formulário. As regras são
verificadas no servidor e os formulários mantêm proteção CSRF.

Não houve alteração de tabelas ou necessidade de migração nesta fase.
Na retomada de 7/11/2026, o Render confirmou deploy Live do commit `bfeb1c6`.
Os logs registraram tabelas e administrador criados em 6/11, com uma execução
posterior preservando a senha. A consulta SQL direta pelo MCP foi bloqueada
pela política de acesso externo do banco; essa política não foi modificada.
O serviço real tem deploy automático por commit habilitado, diferentemente
do padrão Off descrito no Blueprint para novas instalações.

Validação da fase 4 em 7/11/2026: 69 testes pytest aprovados. Não houve acesso
a credenciais, alteração de plano, ampliação da allowlist ou mudança de esquema.
A verificação do deploy é registrada após a publicação, separadamente dos testes.
