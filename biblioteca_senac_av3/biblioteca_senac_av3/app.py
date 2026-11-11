from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "banco.db"

app = Flask(__name__)
app.secret_key = "biblioteca-senac-av3-chave-local"

def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def inicializar_banco():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT NOT NULL DEFAULT 'Geral',
            isbn TEXT UNIQUE,
            exemplares INTEGER NOT NULL DEFAULT 1 CHECK(exemplares >= 0)
        );

        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            aluno TEXT NOT NULL,
            data_emprestimo TEXT NOT NULL,
            data_devolucao TEXT,
            status TEXT NOT NULL DEFAULT 'Emprestado'
                CHECK(status IN ('Emprestado', 'Devolvido')),
            FOREIGN KEY (livro_id) REFERENCES livros(id) ON DELETE RESTRICT
        );
        """)
        total = con.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
        if total == 0:
            con.executemany(
                "INSERT INTO livros (titulo, autor, categoria, isbn, exemplares) VALUES (?, ?, ?, ?, ?)",
                [
                    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", "Literatura", "9788522031445", 5),
                    ("Dom Casmurro", "Machado de Assis", "Literatura brasileira", "9788594318245", 3),
                    ("A lógica do consumo", "Martin Lindstrom", "Administração", "978853522ಕ್ತಿ", 2),
                    ("Python para Iniciantes", "Luiz Eduardo", "Tecnologia", "9786500000001", 4),
                ]
            )
            # Corrige ISBN de exemplo para manter unicidade e formato simples.
            con.execute("UPDATE livros SET isbn = '9788535220002' WHERE titulo = 'A lógica do consumo'")
            con.execute("""
                INSERT INTO emprestimos (livro_id, aluno, data_emprestimo, data_devolucao, status)
                VALUES (1, 'Mariana Costa', ?, NULL, 'Emprestado')
            """, (date.today().isoformat(),))

def obter_livros():
    with conectar() as con:
        return con.execute("""
            SELECT l.*,
                   l.exemplares - COUNT(CASE WHEN e.status = 'Emprestado' THEN 1 END) AS disponiveis,
                   COUNT(CASE WHEN e.status = 'Emprestado' THEN 1 END) AS emprestados
            FROM livros l
            LEFT JOIN emprestimos e ON e.livro_id = l.id
            GROUP BY l.id
            ORDER BY l.titulo COLLATE NOCASE
        """).fetchall()

@app.route("/")
def index():
    livros = obter_livros()
    with conectar() as con:
        emprestimos = con.execute("""
            SELECT e.*, l.titulo AS livro_titulo
            FROM emprestimos e JOIN livros l ON l.id = e.livro_id
            ORDER BY e.id DESC
        """).fetchall()
        total_livros = con.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
        total_emprestados = con.execute("SELECT COUNT(*) FROM emprestimos WHERE status='Emprestado'").fetchone()[0]
    return render_template("index.html", livros=livros, emprestimos=emprestimos,
                           total_livros=total_livros, total_emprestados=total_emprestados)

@app.route("/livros/adicionar", methods=["POST"])
def adicionar_livro():
    dados = (request.form["titulo"].strip(), request.form["autor"].strip(),
             request.form.get("categoria", "Geral").strip(),
             request.form.get("isbn", "").strip() or None,
             max(0, int(request.form.get("exemplares", 1))))
    try:
        with conectar() as con:
            con.execute("INSERT INTO livros (titulo, autor, categoria, isbn, exemplares) VALUES (?, ?, ?, ?, ?)", dados)
        flash("Livro cadastrado com sucesso!", "success")
    except sqlite3.IntegrityError:
        flash("Não foi possível cadastrar. Verifique se o ISBN já existe.", "error")
    return redirect(url_for("index"))

@app.route("/livros/<int:livro_id>/editar", methods=["POST"])
def editar_livro(livro_id):
    try:
        with conectar() as con:
            ativos = con.execute("SELECT COUNT(*) FROM emprestimos WHERE livro_id=? AND status='Emprestado'", (livro_id,)).fetchone()[0]
            exemplares = max(int(request.form["exemplares"]), ativos)
            con.execute("""UPDATE livros SET titulo=?, autor=?, categoria=?, isbn=?, exemplares=? WHERE id=?""",
                        (request.form["titulo"].strip(), request.form["autor"].strip(),
                         request.form.get("categoria", "Geral").strip(),
                         request.form.get("isbn", "").strip() or None, exemplares, livro_id))
        flash("Livro atualizado!", "success")
    except (sqlite3.IntegrityError, ValueError):
        flash("Erro ao atualizar. Confira os dados e o ISBN.", "error")
    return redirect(url_for("index"))

@app.route("/livros/<int:livro_id>/remover", methods=["POST"])
def remover_livro(livro_id):
    with conectar() as con:
        possui_historico = con.execute("SELECT COUNT(*) FROM emprestimos WHERE livro_id=?", (livro_id,)).fetchone()[0]
        if possui_historico:
            flash("Este livro possui histórico de empréstimos e não pode ser removido.", "error")
        else:
            con.execute("DELETE FROM livros WHERE id=?", (livro_id,))
            flash("Livro removido.", "success")
    return redirect(url_for("index"))

@app.route("/emprestimos/adicionar", methods=["POST"])
def adicionar_emprestimo():
    livro_id = int(request.form["livro_id"])
    aluno = request.form["aluno"].strip()
    with conectar() as con:
        livro = con.execute("""
            SELECT l.exemplares - COUNT(CASE WHEN e.status='Emprestado' THEN 1 END) AS disponiveis
            FROM livros l LEFT JOIN emprestimos e ON e.livro_id=l.id
            WHERE l.id=? GROUP BY l.id
        """, (livro_id,)).fetchone()
        if not livro or livro["disponiveis"] <= 0:
            flash("Não há exemplares disponíveis para este livro.", "error")
        elif aluno:
            con.execute("""INSERT INTO emprestimos (livro_id, aluno, data_emprestimo, status)
                           VALUES (?, ?, ?, 'Emprestado')""",
                        (livro_id, aluno, date.today().isoformat()))
            flash("Empréstimo registrado!", "success")
    return redirect(url_for("index"))

@app.route("/emprestimos/<int:emprestimo_id>/devolver", methods=["POST"])
def devolver_emprestimo(emprestimo_id):
    with conectar() as con:
        con.execute("""UPDATE emprestimos SET status='Devolvido', data_devolucao=?
                       WHERE id=? AND status='Emprestado'""", (date.today().isoformat(), emprestimo_id))
    flash("Devolução registrada.", "success")
    return redirect(url_for("index"))

@app.route("/emprestimos/<int:emprestimo_id>/remover", methods=["POST"])
def remover_emprestimo(emprestimo_id):
    with conectar() as con:
        con.execute("DELETE FROM emprestimos WHERE id=?", (emprestimo_id,))
    flash("Registro de empréstimo removido.", "success")
    return redirect(url_for("index"))

@app.route("/api/livros", methods=["GET"])
def api_livros():
    """Rota de API: retorna o catálogo em JSON."""
    return jsonify([dict(livro) for livro in obter_livros()])

@app.route("/api/emprestimos", methods=["GET"])
def api_emprestimos():
    with conectar() as con:
        rows = con.execute("""
            SELECT e.id, e.livro_id, l.titulo AS livro, e.aluno,
                   e.data_emprestimo, e.data_devolucao, e.status
            FROM emprestimos e JOIN livros l ON l.id=e.livro_id
            ORDER BY e.id DESC
        """).fetchall()
    return jsonify([dict(row) for row in rows])

inicializar_banco()

if __name__ == "__main__":
    app.run(debug=True)
