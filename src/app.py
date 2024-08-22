from flask import Flask, render_template, request, redirect, url_for, session
from db.db import Service, Periodo

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

service = Service()
periodo = Periodo()

def auth_guard():
  if 'role' not in session:
    return False
  return True

def admin_guard():
  if 'role' in session:
    if session['role'] == 'ADMIN':
      return True

  return False

def periodo_guard():
  if periodo.is_open:
    return True

  return False

def remove_session():
  session.pop('role', None)
  session.pop('cpf_aluno', None)


@app.get("/logout")
def logout():
  remove_session()
  return app.redirect(app.url_for('index'))

@app.route("/periodo-fechado")
def periodo_fechado():
  if (periodo_guard()):
    if (auth_guard()):
      return app.redirect(app.url_for('aluno_menu'))
    return app.redirect(app.url_for('index'))
  
  return render_template('not-found/periodo-fechado.html')

@app.route("/", methods=['GET', 'POST'])
def index():
  if (auth_guard()):
    return app.redirect(app.url_for('aluno_menu'))

  if (request.method == 'POST'):
    remove_session()
    cpf = request.form.get('cpf')
    if service.logar_aluno(cpf):
      session['cpf_aluno'] = request.form['cpf']
      session['role'] = 'ALUNO'

      if (not periodo_guard()):
        return app.redirect(app.url_for('periodo_fechado'))
      
      return app.redirect(app.url_for('aluno_menu'))

  return render_template('aluno/login.html')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
  if (not admin_guard() and auth_guard()):
    return app.redirect(app.url_for('index'))

  if (request.method == 'POST'):
    remove_session()
    login = request.form.get('login')
    senha = request.form.get('password')
    if service.logar_admin(login, senha):
      session['role'] = 'ADMIN'
      return app.redirect(app.url_for('admin_menu'))
    else:
      return app.redirect(app.url_for('admin'))
  elif (auth_guard()):
    return app.redirect(app.url_for('admin_menu'))

  return render_template('admin/login.html')


@app.get("/admin/menu")
def admin_menu():
  if not (admin_guard()):
    return app.redirect(app.url_for('index'))
  
  total_alunos, total_max_alunos = service.total_alunos()
  return render_template('admin/menu.html', total_alunos=total_alunos, total_max_alunos=total_max_alunos)

@app.post("/admin/criar-aluno")
def criar_aluno():
    cpf = request.form.get('cpf')
    if service.criar_aluno(cpf):
        return redirect(url_for('admin_menu'))
    else:
        return redirect(url_for('admin_menu'))

@app.post("/admin/abrir-periodo")
def abrir_periodo():
    periodo.abrir(service)
    return render_template('admin/menu.html')

@app.route("/aluno_menu", methods=['GET', 'POST'])
def aluno_menu():
  if not (auth_guard()):
    return app.redirect(app.url_for('index'))
  
  if (not periodo_guard()):
    remove_session()
    return app.redirect(app.url_for('index'))
  
  # if (request.method == 'POST'):
      # cpf = session['cpf_aluno']
      # periodo.turmas[turma].inscrever_aluno(cpf, service)

    return render_template('aluno/menu.html')

@app.post("/aluno/matricular/<turma>")
def matricular(turma):
    cpf = session['cpf_aluno']
    periodo.turmas[turma].inscrever_aluno(cpf, service)

    return render_template('aluno/menu.html')


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)