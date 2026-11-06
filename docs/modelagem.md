# Modelo simplificado

A versão acadêmica usa três tabelas, definidas em `sigetec/models.py`:

| Tabela | Campos e responsabilidade |
| --- | --- |
| usuarios | id, nome, email único, senha_hash, perfil e ativo. Representa solicitante, técnico ou administrador. |
| chamados | id, titulo, descricao, prioridade, status, solicitante_id, tecnico_id opcional, criado_em e atualizado_em. Representa uma solicitação de suporte. |
| comentarios | id, chamado_id, usuario_id, conteudo e criado_em. Registra conversa e solução do chamado. |

`solicitante_id` e `tecnico_id` apontam para usuários diferentes no mesmo modelo;
os relacionamentos declaram explicitamente a chave estrangeira correspondente.
Cada comentário pertence a um chamado e a um usuário. As chaves estrangeiras
impedem registros órfãos, inclusive no SQLite, onde são habilitadas explicitamente.
Não há exclusão automática em cascata nem telas de exclusão.

Restrições CHECK validam perfis, prioridades, situações e textos obrigatórios.
Os formulários validam tamanho e conteúdo antes de persistir. A senha é derivada
com hash e salt pelo Werkzeug, nunca armazenada em texto puro. As datas são
criadas em UTC; a interface identifica UTC na apresentação.

Para simplificar, categorias e histórico separado foram retirados desta versão.
Não há relatórios, anexos ou envio de e-mail. Comentários permitem registrar a
solução; a tela do chamado apresenta seu estado atual.

## Permissões

As permissões são verificadas nas rotas Python e nos filtros SQLAlchemy, além
da adaptação da interface. Conhecer o ID de outro chamado não dá acesso a ele.
Solicitantes veem seus próprios chamados; técnicos veem os atribuídos a eles;
administradores veem todos. O cliente não define solicitante_id ao abrir um
chamado: o servidor utiliza o usuário da sessão.

## Inicialização

`init-db` ou `preparar-demo` criam a estrutura explicitamente. Iniciar o Flask
não cria tabelas nem contas. O comando não é uma ferramenta de migração:
se encontrar outra estrutura, recusa o destino e preserva os dados existentes.
Alterações futuras devem usar migrações específicas, sem apagar banco do professor.
