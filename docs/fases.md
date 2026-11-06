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
| 3 — Entrega | Testes automatizados, instalação reproduzível, guia do professor e configuração Render | 36 testes aprovados em instalação limpa e fluxo HTTP real validado |

## Publicação e deploy

O remoto configurado é:
https://github.com/HelioGHB/ProjetoIntegradorUnisaProgWEB.git

O envio da fase 1 foi tentado, mas a autenticação GitHub do VS Code estava
indisponível. Não houve push bem-sucedido nessa tentativa. Os commits locais
mantêm a separação das fases e podem ser enviados juntos quando a autenticação
estiver funcionando:

```bash
git push -u origin main
```

Não use force push. Se o remoto tiver recebido mudanças, compare o histórico
antes de enviar. O histórico de commits estará visível no GitHub após o push;
publicar código no GitHub não cria automaticamente uma aplicação acessível.

O deploy requer um serviço Render conectado e PostgreSQL hospedado configurado.
Ainda não houve deploy. Não é possível registrar retrospectivamente um deploy
para fases que não foram publicadas. Depois da primeira publicação, a rotina
para cada nova fase será:

1. Implementar uma parte pequena e testá-la.
2. Criar commit com fase, mudança e validação.
3. Enviar ao GitHub, preservando o histórico.
4. Executar deploy manual no Render e testar pelo navegador.
5. Registrar URL e resultado real da implantação.

O envio do código foi autorizado pelo responsável, mas depende da autenticação.
A criação de recursos pagos depende de escolha explícita de plano e custos.
