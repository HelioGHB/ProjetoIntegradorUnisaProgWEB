# Migração para endereço sem identificação institucional

Novo serviço: `sigetec-chamados`, plano Free, região Virginia.
URL atribuída: https://sigetec-chamados.onrender.com.
Estado: criado; aguarda configuração privada e validação. Atribuir uma URL não significa que a aplicação está pronta.

1. No [ambiente do serviço antigo](https://dashboard.render.com/web/srv-dbn2dotbedkc73a2i1d0/env), copie somente os valores de `DATABASE_URL` e `SECRET_KEY`.
2. No [ambiente do novo serviço](https://dashboard.render.com/web/srv-dbo8549srm7s73b7o350/env), adicione essas duas variáveis com os mesmos valores. Não compartilhe os valores no chat, Git ou documentação.
3. Escolha **Save, rebuild, and deploy**. O primeiro deploy sem essas variáveis pode falhar; não é necessário criar banco nem administrador novamente.
4. Após o deploy ficar Live, conferir `/healthz`, `/login` e login com uma conta existente. O domínio permitido usa automaticamente o novo hostname do Render.
5. Somente depois da validação, desativar o serviço antigo pelo painel para retirar o endereço anterior do ar. Não excluir o PostgreSQL `sigetec-db`.

O novo serviço executa diretamente Gunicorn, sem inicialização de tabelas ou administrador. `INIT_DB_ON_START` e `CREATE_ADMIN_ON_START` estão definidos como `false`.
Os dados continuam no mesmo PostgreSQL. Auto-deploy está desativado; alterações futuras precisam de deploy manual.
