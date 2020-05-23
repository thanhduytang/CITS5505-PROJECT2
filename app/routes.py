from flask import render_template, flash, redirect, url_for, request, abort, json, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Score, QA
from werkzeug.urls import url_parse
from sqlalchemy.sql.expression import func

@app.route('/')
@app.route('/index')
@login_required

def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):

            flash('Invalid username or password')

            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':

            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title = "Sign in", form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered account.!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/editquestion', methods=['GET', 'POST'])
@login_required
def editquestion():
    if not current_user.is_admin:
        flash("You are not allowed to access this page. Administrator only !!!")
        return redirect(url_for('index'))
    
    questions = QA.query.all()
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        flash("You have successfully created a question")
        if QA.query.get(edit_form.question_num.data) is not None:
            db.session.delete(QA.query.get(edit_form.question_num.data))
            db.session.commit()
        newquestion = QA(id      = edit_form.question_num.data,
                         question= edit_form.question.data,
                         option1 = edit_form.option1.data,
                         option2 = edit_form.option2.data,
                         option3 = edit_form.option3.data,
                         option4 = edit_form.option4.data,
                         answer  = edit_form.answer.data)
        db.session.add(newquestion)
        db.session.commit()
        return render_template('edit.html', form=edit_form, questions=questions)
    return render_template('edit.html', form=edit_form, questions=questions)


@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    lists=[]
    len_QA = len(QA.query.all())
    for i in range(1, len_QA + 1, 1):
        q_id = QA.query.get(i)
        quest = {
                'question': q_id.question,
                'option1': q_id.option1,
                'option2': q_id.option2,
                'option3': q_id.option3,
                'option4': q_id.option4,
                'answer' : q_id.answer}
        lists.append(quest)  
    return render_template('quiz.html', lists = lists)

@app.route('/getscore', methods=['POST'])
@login_required
def get_score():
    score = None
    if request.method == "POST":
        score = request.form['score']
        newscore = Score(score = score, user_id = current_user.id)
        db.session.add(newscore)
        db.session.commit()
        score = Score.query.filter_by(user_id=current_user.id).first().score
        if score > 100 and score <= 120:
            Olevel = "Sufficient"
        elif score <= 100 & score >= 80:
            Olevel = "Medium"
        else:
            Olevel = "Insufficient"
        
        olevel = Score(olevel = Olevel, user_id = current_user.id)
        db.session.add(olevel)
        db.session.commit()
    return render_template('result.html')
@app.route('/result', methods=['GET','POST'])
@login_required
def result():
    score = Score.query.filter_by(user_id = current_user.id).first().score
    olevel = Score.query.filter_by(user_id = current_user.id).first().olevel
    return render_template('result.html', score = score)

    
