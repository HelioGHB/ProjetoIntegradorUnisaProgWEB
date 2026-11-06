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
Ainda não houve deploy. Não é possível registrar retrospectivamente um deploy
para fases que não foram publicadas. Depois da primeira publicação, a rotina
para cada nova fase será:

1. Implementar uma parte pequena e testá-la.
2. Criar commit com fase, mudança e validação.
3. Enviar ao GitHub, preservando o histórico.
4. Executar deploy manual no Render e testar pelo navegador.
5. Registrar URL e resultado real da implantação.

O envio do código foi autorizado e concluído. A implantação permanece pendente
de conexão ao Render e configuração de um banco novo de demonstração.
A criação de recursos pagos depende de escolha explícita de plano e custos.
