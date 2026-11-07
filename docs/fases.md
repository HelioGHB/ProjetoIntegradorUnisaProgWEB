# Fases e evidências de evolução do SIGETEC

O reinício simplificado foi autorizado pelo responsável. Código anterior foi
guardado temporariamente para recuperação; credenciais e bancos anteriores
foram preservados. O histórico abaixo descreve commits reais.

| Entrega | Commit | Resultado e validação |
| --- | --- | --- |
| Fase 1 — Base local | `f88dd9c` | Fábrica Flask, página inicial e CSS local; HTTP 200 |
| Fase 2 — Atendimento básico | `704bc19` | Três perfis, login, SQLite, chamados, atribuição, status e comentários; fluxo isolado verificado |
| Fase 3 — Entrega executável | `619a3db` | Instruções para execução local, testes e Render; 36 testes aprovados em instalação limpa |
| Publicação do histórico no GitHub | `400e849` | Código enviado à `main`, preservando os commits anteriores |
| Inicialização sem Shell | `bfeb1c6` | Bootstrap opcional e primeiro administrador; 51 testes e PostgreSQL temporário para transação, rollback e concorrência |
| Fase 4 — Administração de usuários | `bbb5549` | Cadastro e ativação/desativação de técnicos/solicitantes; 69 testes, sem alteração de esquema |
| Entrega de apresentação | Histórico atual da `main` | Roteiro, README consolidado, três screenshots reais e relatório de validação |

Os commits iniciais usam a autoria técnica **SIGETEC <sigetec@example.com>**,
pois não havia identidade pessoal configurada. Não foi presumida uma identidade
pessoal para publicar o trabalho. Essa autoria pode ser configurada pelo
responsável para os próximos commits, sem reescrever o histórico existente.

## Publicação e execução

- Repositório: https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB
- Histórico: https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB/commits/main/
- Serviço: `sigetec-unisa`, em https://sigetec-unisa.onrender.com.
- PostgreSQL separado do serviço web, na mesma região.

Em 6/11/2026, os commits foram publicados usando autenticação do GitHub CLI,
após falha da autenticação do VS Code. Os logs do Render confirmaram a criação
das tabelas e do administrador nessa data; uma execução posterior preservou a
senha existente.

Em 7/11/2026, o responsável concluiu o deploy manual da fase 4. O Render
confirmou o commit `bbb5549` Live, e `/healthz` e `/login` responderam HTTP 200.
A rota `/usuarios`, sem sessão, encaminhou ao login. O responsável cadastrou
as contas fictícias e relatou sucesso no ciclo completo de atendimento.
A consulta SQL direta pelo MCP foi bloqueada pela allowlist externa vazia;
a política foi preservada, sem ampliar acesso ao banco.

O Blueprint tem Auto-Deploy Off como referência para novas instalações. O
serviço existente indicou automático por commit, mas não iniciou sozinho o
build da fase 4. A causa não foi comprovada; a atualização manual resolveu a
publicação. Não se deve apresentar o campo Auto-Deploy como prova de deploy.

## Entrega de documentação e imagens

As capturas foram feitas em Chromium com o código real, SQLite temporário e
dados fictícios, sem usar contas reais ou alterar o PostgreSQL hospedado.
O script de captura fica versionado em `scripts/capturar_telas.py`.
A suíte de 69 testes foi executada novamente nesta entrega.

Como a inicialização e o login já haviam sido validados, as flags de bootstrap
foram desativadas e seus três valores temporários foram esvaziados por atualização
parcial das variáveis. `SECRET_KEY`, `DATABASE_URL`, `APP_ENV` e as demais
configurações foram preservadas. O redeploy de configuração foi confirmado
Live, sem alteração de planos ou dados. A conclusão está em `docs/entrega.md`.

## Rotina para uma próxima fase

1. Definir uma parte pequena dentro do escopo acadêmico.
2. Implementar e testar em ambiente isolado.
3. Criar commit com mudança e validação; enviar sem force push.
4. Confirmar se há deploy automático real ou executar o procedimento manual.
5. Verificar o commit Live, saúde HTTP e o comportamento entregue.

Alterações exclusivamente de documentação podem usar `[skip render]` na mensagem
do commit para evitar um rebuild sem mudança funcional. Serviços pagos,
operações destrutivas ou mudanças de escopo exigem decisão explícita.
