from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ANAbanana911.@localhost/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Usuario(db.Model):
 __tablename__="usuario"
 id_usuario = db.Column(db.Integer, primary_key=True)
 nome = db.Column(db.String(256), nullable=False)
 email = db.Column(db.String(256), unique=True, nullable=False)
 senha = db.Column(db.String(256), nullable=False)
 data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

 anuncios = db.relationship("Anuncio", backref="usuario", lazy=True)
 perguntas = db.relationship("Pergunta", backref="autor_pergunta", lazy=True)
 compras = db.relationship("Compra", backref="comprador", lazy=True)
 favoritos = db.relationship("Favorito", backref="usuario_favorito", lazy=True)

class Categoria(db.Model):
 __tablename__="categoria"
 id_categoria = db.Column(db.Integer, primary_key=True)
 nome = db.Column(db.String(256), nullable=False, unique=True)

 anuncios = db.relationship("Anuncio", backref="categoria", lazy=True)

class Anuncio(db.Model):
  __tablename__="anuncio"
  id_anuncio= db.Column(db.Integer, primary_key=True)
  titulo = db.Column(db.String(256), nullable=False)
  descricao = db.Column(db.Text, nullable=False)
  preco = db.Column(db.Float, nullable=False)
  data_publicacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

  id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
  id_categoria = db.Column(db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False)

  perguntas = db.relationship("Pergunta", backref="anuncio", lazy=True)
  compras = db.relationship("Compra", backref="anuncio_compra", lazy=True)
  favoritos = db.relationship("Favorito", backref="anuncio_favorito", lazy=True)

class Pergunta(db.Model):
 __tablename__="pergunta"
 id_pergunta = db.Column(db.Integer, primary_key=True)
 texto = db.Column(db.Text, nullable=False)
 data_pergunta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

 id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
 id_anuncio = db.Column(db.Integer, db.ForeignKey("anuncio.id_anuncio"), nullable=False)

 resposta = db.relationship("Resposta", backref="pergunta", uselist=False)

class Resposta(db.Model):
 __tablename__ = "resposta"
 id_resposta = db.Column(db.Integer, primary_key=True)
 texto = db.Column(db.Text, nullable=False)
 data_resposta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

 id_pergunta = db.Column(db.Integer, db.ForeignKey("pergunta.id_pergunta"), unique=True, nullable=False)


class Compra(db.Model):
 __tablename__ = "compra"
 id_compra = db.Column(db.Integer, primary_key=True)
 id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)  # quem comprou
 id_anuncio = db.Column(db.Integer, db.ForeignKey("anuncio.id_anuncio"), nullable=False)
 data_compra = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
 quantidade = db.Column(db.Integer, nullable=False, default=1)


class Favorito(db.Model):
 __tablename__ = "favorito"
 id_favorito = db.Column(db.Integer, primary_key=True)
 id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
 id_anuncio = db.Column(db.Integer, db.ForeignKey("anuncio.id_anuncio"), nullable=False)
 data_favorito = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@app.route("/")
def index():
 return render_template('index.html')

@app.route("/cad/usuario")
def usuario_list():
 usuarios = Usuario.query.order_by(Usuario.id_usuario.desc()).all()
 edit_id = request.args.get("edit_id", type=int)
 confirm_delete_id = request.args.get("confirm_delete_id", type=int)
 usuario_editar = Usuario.query.get(edit_id) if edit_id else None
 usuario_deletar = Usuario.query.get(confirm_delete_id) if confirm_delete_id else None
 return render_template("usuario.html",
                        usuarios=usuarios,
                        usuario_editar=usuario_editar,
                        usuario_deletar=usuario_deletar,
                        titulo="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def usuario_criar():
 nome = request.form.get("user", "").strip()
 email = request.form.get("email", "").strip()
 senha = request.form.get("passwd", "").strip()
 end = request.form.get("end", "").strip()

 if not (nome and email and senha):
     flash("Preencha nome, email e senha.")
     return redirect(url_for("usuario_list"))
 db.session.add(Usuario(nome=nome, email=email, senha=senha, end=end))
 db.session.commit()
 flash("Usuário cadastrado!")
 return redirect(url_for("usuario_list"))

@app.route("/usuario/editar/<int:id_usuario>", methods=["POST"])
def usuario_editar(id_usuario):
 u = Usuario.query.get_or_404(id_usuario)
 u.nome = request.form.get("nome", u.nome)
 u.email = request.form.get("email", u.email)
 u.senha = request.form.get("senha", u.senha)
 db.session.commit()
 flash("Usuário atualizado!")
 return redirect(url_for("usuario_list"))

@app.route("/usuario/deletar/<int:id_usuario>", methods=["POST"])
def usuario_deletar(id_usuario):
 u = Usuario.query.get_or_404(id_usuario)
 db.session.delete(u)
 db.session.commit()
 flash("Usuário excluído.")
 return redirect(url_for("usuario_list"))

@app.route("/config/categoria")
def categoria_list():
 categorias = Categoria.query.order_by(Categoria.id_categoria.desc()).all()
 edit_id = request.args.get("edit_id", type=int)
 confirm_delete_id = request.args.get("confirm_delete_id", type=int)
 categoria_editar = Categoria.query.get(edit_id) if edit_id else None
 categoria_deletar = Categoria.query.get(confirm_delete_id) if confirm_delete_id else None
 return render_template("categoria.html",
                        categorias=categorias,
                        categoria_editar=categoria_editar,
                        categoria_deletar=categoria_deletar,
                        titulo="Categoria")

@app.route("/categoria/criar", methods=["POST"])
def categoria_criar():
 nome = request.form.get("nome", "").strip()
 if not nome:
     flash("Informe o nome da categoria.")
     return redirect(url_for("categoria_list"))
 db.session.add(Categoria(nome=nome))
 db.session.commit()
 flash("Categoria cadastrada!")
 return redirect(url_for("categoria_list"))

@app.route("/categoria/editar/<int:id_categoria>", methods=["POST"])
def categoria_editar(id_categoria):
 c = Categoria.query.get_or_404(id_categoria)
 c.nome = request.form.get("nome", c.nome)
 db.session.commit()
 flash("Categoria atualizada!")
 return redirect(url_for("categoria_list"))

@app.route("/categoria/deletar/<int:id_categoria>", methods=["POST"])
def categoria_deletar(id_categoria):
 c = Categoria.query.get_or_404(id_categoria)
 db.session.delete(c)
 db.session.commit()
 flash("Categoria excluída.")
 return redirect(url_for("categoria_list"))

@app.route("/cad/anuncio")
def anuncio_list():
 anuncios = (Anuncio.query
             .order_by(Anuncio.id_anuncio.desc())
             .all())
 categorias = Categoria.query.order_by(Categoria.nome).all()
 usuarios = Usuario.query.order_by(Usuario.nome).all()

 compras = Compra.query.order_by(Compra.id_compra.desc()).all()
 favoritos = Favorito.query.order_by(Favorito.id_favorito.desc()).all()

 edit_id = request.args.get("edit_id", type=int)
 confirm_delete_id = request.args.get("confirm_delete_id", type=int)
 anuncio_editar = Anuncio.query.get(edit_id) if edit_id else None
 anuncio_deletar = Anuncio.query.get(confirm_delete_id) if confirm_delete_id else None

 edit_compra_id = request.args.get("edit_compra_id", type=int)
 compra_editar = Compra.query.get(edit_compra_id) if edit_compra_id else None

 edit_fav_id = request.args.get("edit_fav_id", type=int)
 favorito_editar = Favorito.query.get(edit_fav_id) if edit_fav_id else None

 del_compra_id = request.args.get("confirm_delete_compra_id", type=int)
 compra_deletar = Compra.query.get(del_compra_id) if del_compra_id else None

 del_fav_id = request.args.get("confirm_delete_fav_id", type=int)
 favorito_deletar = Favorito.query.get(del_fav_id) if del_fav_id else None

 return render_template("anuncio.html",
                       anuncios=anuncios,
                       categorias=categorias,
                       usuarios=usuarios,
                       anuncio_editar=anuncio_editar,
                       anuncio_deletar=anuncio_deletar,
                       compras=compras,
                       compra_editar=compra_editar,
                       compra_deletar=compra_deletar,
                       favoritos=favoritos,
                       favorito_editar=favorito_editar,
                       favorito_deletar=favorito_deletar,
                       titulo="Anúncio")

@app.route("/anuncio/criar", methods=["POST"])
def anuncio_criar():
 titulo = request.form.get("titulo", "").strip()
 descricao = request.form.get("descricao", "").strip()
 preco = request.form.get("preco", type=float)
 id_usuario = request.form.get("id_usuario", type=int)
 id_categoria = request.form.get("id_categoria", type=int)

 if not (titulo and descricao and preco is not None and id_usuario and id_categoria):
     flash("Preencha todos os campos do anúncio.")
     return redirect(url_for("anuncio_list"))

 db.session.add(Anuncio(titulo=titulo, descricao=descricao, preco=preco,
                        id_usuario=id_usuario, id_categoria=id_categoria))
 db.session.commit()
 flash("Anúncio cadastrado!")
 return redirect(url_for("anuncio_list"))

@app.route("/anuncio/editar/<int:id_anuncio>", methods=["POST"])
def anuncio_editar(id_anuncio):
 a = Anuncio.query.get_or_404(id_anuncio)
 a.titulo = request.form.get("titulo", a.titulo)
 a.descricao = request.form.get("descricao", a.descricao)
 a.preco = request.form.get("preco", type=float) or a.preco
 a.id_usuario = request.form.get("id_usuario", type=int) or a.id_usuario
 a.id_categoria = request.form.get("id_categoria", type=int) or a.id_categoria
 db.session.commit()
 flash("Anúncio atualizado!")
 return redirect(url_for("anuncio_list"))

@app.route("/anuncio/deletar/<int:id_anuncio>", methods=["POST"])
def anuncio_deletar(id_anuncio):
 a = Anuncio.query.get_or_404(id_anuncio)
 db.session.delete(a)
 db.session.commit()
 flash("Anúncio excluído.")
 return redirect(url_for("anuncio_list"))

@app.route("/anuncios/pergunta")
def pergunta_list():
 perguntas = (Pergunta.query
              .order_by(Pergunta.id_pergunta.desc())
              .all())
 anuncios = Anuncio.query.order_by(Anuncio.titulo).all()
 usuarios = Usuario.query.order_by(Usuario.nome).all()
 respostas = Resposta.query.order_by(Resposta.id_resposta.desc()).all()

 edit_id = request.args.get("edit_id", type=int)
 pergunta_editar = Pergunta.query.get(edit_id) if edit_id else None
 del_id = request.args.get("confirm_delete_id", type=int)
 pergunta_deletar = Pergunta.query.get(del_id) if del_id else None

 edit_resp_id = request.args.get("edit_resposta_id", type=int)
 resposta_editar = Resposta.query.get(edit_resp_id) if edit_resp_id else None
 del_resp_id = request.args.get("confirm_delete_resposta_id", type=int)
 resposta_deletar = Resposta.query.get(del_resp_id) if del_resp_id else None

 return render_template("pergunta.html",
                           perguntas=perguntas,
                           anuncios=anuncios,
                           usuarios=usuarios,
                           respostas=respostas,
                           pergunta_editar=pergunta_editar,
                           pergunta_deletar=pergunta_deletar,
                           resposta_editar=resposta_editar,
                           resposta_deletar=resposta_deletar,
                           titulo="Perguntas & Respostas")

@app.route("/pergunta/criar", methods=["POST"])
def pergunta_criar():
 texto = request.form.get("texto", "").strip()
 id_usuario = request.form.get("id_usuario", type=int)
 id_anuncio = request.form.get("id_anuncio", type=int)
 if not (texto and id_usuario and id_anuncio):
     flash("Preencha texto, usuário e anúncio da pergunta.")
     return redirect(url_for("pergunta_list"))
 db.session.add(Pergunta(texto=texto, id_usuario=id_usuario, id_anuncio=id_anuncio))
 db.session.commit()
 flash("Pergunta criada!")
 return redirect(url_for("pergunta_list"))

@app.route("/pergunta/editar/<int:id_pergunta>", methods=["POST"])
def pergunta_editar(id_pergunta):
 p = Pergunta.query.get_or_404(id_pergunta)
 p.texto = request.form.get("texto", p.texto)
 p.id_usuario = request.form.get("id_usuario", type=int) or p.id_usuario
 p.id_anuncio = request.form.get("id_anuncio", type=int) or p.id_anuncio
 db.session.commit()
 flash("Pergunta atualizada!")
 return redirect(url_for("pergunta_list"))

@app.route("/pergunta/deletar/<int:id_pergunta>", methods=["POST"])
def pergunta_deletar(id_pergunta):
 p = Pergunta.query.get_or_404(id_pergunta)
 db.session.delete(p)
 db.session.commit()
 flash("Pergunta excluída.")
 return redirect(url_for("pergunta_list"))

@app.route("/resposta/criar", methods=["POST"])
def resposta_criar():
 texto = request.form.get("texto", "").strip()
 id_pergunta = request.form.get("id_pergunta", type=int)
 if not (texto and id_pergunta):
     flash("Preencha texto e a pergunta relacionada.")
     return redirect(url_for("pergunta_list"))
 if Resposta.query.filter_by(id_pergunta=id_pergunta).first():
  flash("Esta pergunta já possui uma resposta.")
  return redirect(url_for("pergunta_list"))
 db.session.add(Resposta(texto=texto, id_pergunta=id_pergunta))
 db.session.commit()
 flash("Resposta criada")
 return redirect(url_for("pergunta_list"))

@app.route("/resposta/editar/<int:id_resposta>", methods=["POST"])
def resposta_editar(id_resposta):
 r = Resposta.query.get_or_404(id_resposta)
 r.texto = request.form.get("texto", r.texto)
 db.session.commit()
 flash("Resposta atualizada!")
 return redirect(url_for("pergunta_list")) 

@app.route("/resposta/deletar/<int:id_resposta>", methods=["POST"])
def resposta_deletar(id_resposta):
 r = Resposta.query.get_or_404(id_resposta)
 db.session.delete(r)
 db.session.commit()
 flash("Resposta excluída.")
 return redirect(url_for("pergunta_list"))

@app.route("/compra/criar", methods=["POST"])
def compra_criar():
 id_usuario = request.form.get("id_usuario", type=int)
 id_anuncio = request.form.get("id_anuncio", type=int)
 quantidade = request.form.get("quantidade", type=int) or 1
 if not (id_usuario and id_anuncio and quantidade > 0):
     flash("Informe usuário, anúncio e quantidade válida para compra.")
     return redirect(url_for("anuncio_list"))
 db.session.add(Compra(id_usuario=id_usuario, id_anuncio=id_anuncio, quantidade=quantidade))
 db.session.commit()
 flash("Compra registrada!")
 return redirect(url_for("anuncio_list"))

@app.route("/compra/editar/<int:id_compra>", methods=["POST"])
def compra_editar(id_compra):
 c = Compra.query.get_or_404(id_compra)
 c.id_usuario = request.form.get("id_usuario", type=int) or c.id_usuario
 c.id_anuncio = request.form.get("id_anuncio", type=int) or c.id_anuncio
 q = request.form.get("quantidade", type=int)
 c.quantidade = q if q and q > 0 else c.quantidade
 db.session.commit()
 flash("Compra atualizada!")
 return redirect(url_for("anuncio_list"))

@app.route("/compra/deletar/<int:id_compra>", methods=["POST"])
def compra_deletar(id_compra):
 c = Compra.query.get_or_404(id_compra)
 db.session.delete(c)
 db.session.commit()
 flash("Compra excluída.")
 return redirect(url_for("anuncio_list"))

@app.route("/favorito/criar", methods=["POST"])
def favorito_criar():
 id_usuario = request.form.get("id_usuario", type=int)
 id_anuncio = request.form.get("id_anuncio", type=int)
 if not (id_usuario and id_anuncio):
     flash("Informe usuário e anúncio para favoritar.")
     return redirect(url_for("anuncio_list"))
 db.session.add(Favorito(id_usuario=id_usuario, id_anuncio=id_anuncio))
 db.session.commit()
 flash("Favorito adicionado!")
 return redirect(url_for("anuncio_list"))

@app.route("/favorito/editar/<int:id_favorito>", methods=["POST"])
def favorito_editar(id_favorito):
 f = Favorito.query.get_or_404(id_favorito)
 f.id_usuario = request.form.get("id_usuario", type=int) or f.id_usuario
 f.id_anuncio = request.form.get("id_anuncio", type=int) or f.id_anuncio
 db.session.commit()
 flash("Favorito atualizado!")
 return redirect(url_for("anuncio_list"))

@app.route("/favorito/deletar/<int:id_favorito>", methods=["POST"])
def favorito_deletar(id_favorito):
 f = Favorito.query.get_or_404(id_favorito)
 db.session.delete(f)
 db.session.commit()
 flash("Favorito excluído.")
 return redirect(url_for("anuncio_list"))

@app.route("/relatorios/vendas")
def rel_vendas():
 """ Relatório de vendas por vendedor (dono do anúncio).
     Filtre por ?usuario_id= (id do vendedor) se quiser. """
 usuario_id = request.args.get("usuario_id", type=int)

 query = db.session.query(
        Usuario.nome.label("vendedor"),
        Anuncio.titulo.label("anuncio"),
        db.func.sum(Compra.quantidade).label("qtd_vendida"),
        db.func.sum(Compra.quantidade * Anuncio.preco).label("total")
    ).join(Anuncio, Anuncio.id_usuario == Usuario.id_usuario) \
     .join(Compra, Compra.id_anuncio == Anuncio.id_anuncio)
 
 if usuario_id:
  query = query.filter(Usuario.id_usuario == usuario_id)

 query = query.group_by(Usuario.nome, Anuncio.titulo) \
              .order_by(Usuario.nome, Anuncio.titulo)
 
 linhas = query.all()
 usuarios = Usuario.query.order_by(Usuario.nome).all()
 return render_template("relVendas.html", linhas=linhas, usuarios=usuarios, usuario_id=usuario_id)

@app.route("/relatorios/compras")
def rel_compras():
    """ Relatório de compras por comprador.
        Filtre por ?usuario_id= (id do comprador) se quiser. """
    usuario_id = request.args.get("usuario_id", type=int)

    query = db.session.query(
        Usuario.nome.label("comprador"),
        Anuncio.titulo.label("anuncio"),
        db.func.sum(Compra.quantidade).label("qtd"),
        db.func.sum(Compra.quantidade * Anuncio.preco).label("total")
    ).join(Compra, Compra.id_usuario == Usuario.id_usuario) \
     .join(Anuncio, Anuncio.id_anuncio == Compra.id_anuncio)

    if usuario_id:
        query = query.filter(Usuario.id_usuario == usuario_id)

    query = query.group_by(Usuario.nome, Anuncio.titulo) \
                 .order_by(Usuario.nome, Anuncio.titulo)

    linhas = query.all()
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("relCompras.html", linhas=linhas, usuarios=usuarios, usuario_id=usuario_id)

@app.route("/relatorios/compras")
def rel_compras_view():
    """Relatório de compras por comprador."""
    usuario_id = request.args.get("usuario_id", type=int)

    query = db.session.query(
        Usuario.nome.label("comprador"),
        Anuncio.nome.label("anuncio"),
        db.func.sum(Compra.quantidade).label("qtd"),
        db.func.sum(Compra.quantidade * Anuncio.preco).label("total")
    ).join(Compra, Compra.id_usuario == Usuario.id) \
     .join(Anuncio, Anuncio.id == Compra.id_anuncio)
    
    if usuario_id:
        query = query.filter(Usuario.id == usuario_id)

    query = query.group_by(Usuario.nome, Anuncio.nome) \
                 .order_by(Usuario.nome, Anuncio.nome)

    linhas = query.all()
    usuarios = Usuario.query.order_by(Usuario.nome).all()

    return render_template(
        "relCompras.html",
        linhas=linhas,
        usuarios=usuarios,
        usuario_id=usuario_id
    )

if __name__ =="__main__":
  with app.app_context():
    db.create_all()
  app.run(debug=True)