const toggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('senac-theme');
if (savedTheme === 'dark') document.body.classList.add('dark');
function updateThemeLabel() {
  const dark = document.body.classList.contains('dark');
  toggle.innerHTML = dark ? '☀ <span>Modo claro</span>' : '☾ <span>Modo escuro</span>';
}
updateThemeLabel();
toggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('senac-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  updateThemeLabel();
});
document.getElementById('today').textContent = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'full' }).format(new Date());

document.getElementById('search').addEventListener('input', (event) => {
  const term = event.target.value.toLocaleLowerCase('pt-BR');
  document.querySelectorAll('#bookRows tr[data-search]').forEach(row => {
    row.style.display = row.dataset.search.includes(term) ? '' : 'none';
  });
});
function abrirModal(id) { document.getElementById(id).classList.add('show'); }
function fecharModal(id) { document.getElementById(id).classList.remove('show'); }
function editarLivro(livro) {
  const form = document.getElementById('bookForm');
  form.action = `/livros/${livro.id}/editar`;
  form.querySelector('[name="titulo"]').value = livro.titulo;
  form.querySelector('[name="autor"]').value = livro.autor;
  form.querySelector('[name="categoria"]').value = livro.categoria;
  form.querySelector('[name="isbn"]').value = livro.isbn || '';
  form.querySelector('[name="exemplares"]').value = livro.exemplares;
  document.getElementById('modalTitle').textContent = 'Editar livro';
  abrirModal('modalLivro');
}
document.getElementById('modalLivro').addEventListener('click', event => {
  if (event.target.id === 'modalLivro') fecharModal('modalLivro');
});
