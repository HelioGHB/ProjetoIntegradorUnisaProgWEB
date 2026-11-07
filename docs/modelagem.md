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

`init-db` ou `preparar-demo` criam a estrutura explicitamente. `criar-admin`
cria somente o primeiro administrador, sem redefinir um já existente.
Iniciar a fábrica Flask não cria tabelas nem contas. Na hospedagem, o Start
Command pode executar `inicializar-deploy` antes do servidor, mas somente
quando suas flags forem habilitadas. Elas ficam desativadas após o sucesso. O comando não é uma ferramenta de migração:
se encontrar outra estrutura, recusa o destino e preserva os dados existentes.
Alterações futuras devem usar migrações específicas, sem apagar banco do professor.


## Administração de usuários

O administrador cadastra técnicos e solicitantes. As senhas iniciais exigem
12 a 128 caracteres e confirmação; e-mails são validados e convertidos para
minúsculas antes de verificar unicidade. A restrição UNIQUE protege contra
conflitos simultâneos de cadastro. Não há cadastro público ou criação de
administradores pelo formulário.

Ativar/desativar uma conta altera apenas `ativo`, mantendo as referências de
chamados e comentários. Um usuário desativado é recusado no login e deixa de
ser carregado na próxima requisição de uma sessão aberta. A interface protege
contas administrativas contra bloqueio e não oferece exclusão de registros.
