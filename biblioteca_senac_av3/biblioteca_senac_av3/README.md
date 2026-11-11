# Biblioteca Senac — Projeto Integrador AV3

Sistema web simples para gerenciamento de acervo e empréstimos, desenvolvido com **Python + Flask + SQLite**.

## Requisitos atendidos
- Banco SQLite (`banco.db`) com duas tabelas relacionadas: `livros` e `emprestimos`.
- CRUD de livros: cadastrar, listar, editar e remover.
- Gestão de empréstimos: registrar, listar, devolver e excluir registros.
- API JSON: `GET /api/livros` e `GET /api/emprestimos`.
- Interface responsiva com pesquisa e modo claro/escuro.
- Arquivo `render.yaml` e `Procfile` para publicação no Render.

## Executar no computador
1. Instale Python 3.10 ou superior.
2. Abra esta pasta no Visual Studio Code.
3. No terminal integrado, execute uma vez:
   ```bash
   py -m pip install -r requirements.txt
   ```
4. Clique em **Run Python File** com `app.py` aberto, ou execute:
   ```bash
   py app.py
   ```
5. Abra `http://127.0.0.1:5000`.

O banco `banco.db` é criado automaticamente na primeira execução, já com dados de exemplo. O arquivo também acompanha o projeto para a entrega.

## API
- `GET /api/livros` — catálogo, exemplares, emprestados e disponíveis.
- `GET /api/emprestimos` — registros de empréstimos.

Abra as rotas no navegador para visualizar o JSON.

## Publicar no Render
1. Crie um repositório no GitHub e envie todos os arquivos deste projeto.
2. No Render, escolha **New + → Web Service** e conecte o repositório.
3. O Render identifica o `render.yaml`. Se pedir os comandos manualmente:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Clique em **Deploy** e aguarde a URL pública.

**Atenção:** o plano gratuito do Render pode usar armazenamento efêmero. Para uma demonstração escolar, os dados de exemplo podem ser recriados no deploy; para manter alterações permanentemente em produção, configure um disco persistente ou banco de dados gerenciado.

## Arquivos
- `app.py`: rotas, regras de negócio, banco e API.
- `banco.db`: banco SQLite de exemplo.
- `templates/index.html`: estrutura da interface.
- `static/style.css`: visual e responsividade.
- `static/app.js`: busca, modal e tema.
- `relatorio_tecnico.md`: DER e dicionário de dados.
