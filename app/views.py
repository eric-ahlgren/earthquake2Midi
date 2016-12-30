from flask import render_template, flash, redirect, session, url_for, request, g
#from flask_login import login_user, logout_user, current_user, login_required
#from app import app, db, lm, oid, babel
from app import app
from forms import MusicForm, InstrumentForm
#from models import User, Post
from datetime import datetime
import earthquake2Midi
from flask_cors import cross_origin
#from config import POSTS_PER_PAGE, LANGUAGES
#from .emails import follower_notification
#from flask_babel import gettext
#from guess_language import guessLanguage
#from flask import jsonify
#from .translate import microsoft_translate

@app.route('/translate', methods=['POST'])
#@login_required
def translate():
    return jsonify({ 
        'text': microsoft_translate(
            request.form['text'], 
            request.form['sourceLang'], 
            request.form['destLang']) })

#@babel.localeselector
def get_locale():
    return 'es' #request.accept_languages.best_match(LANGUAGES.keys())

@app.route('/edit', methods=['GET', 'POST'])
#@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

# @app.before_request
# def before_request():
#     g.user = current_user
#     if g.user.is_authenticated:
#         g.user.last_seen = datetime.utcnow()
#         db.session.add(g.user)
#         db.session.commit()
#     g.locale = get_locale()

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# @app.route('/index/<int:page>', methods=['GET', 'POST'])
# @login_required
# def index(page=1):
#     form = PostForm()
#     if form.validate_on_submit():
#     	language = guessLanguage(form.post.data)
#         if language == 'UNKNOWN' or len(language) > 5:
#             language = ''
#         post = Post(body=form.post.data, 
#                     timestamp=datetime.utcnow(), 
#                     author=g.user, 
#                     language=language)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post is now live!')
#         return redirect(url_for('index'))
#     posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
#     return render_template('index.html',
#                            title='Home',
#                            form=form,
#                            posts=posts)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    instrument_form = InstrumentForm()
    form = MusicForm()
    #print "MUSIC FORM SUBMIT: "+str(form.submit_music.data)
    #instrument_form.submit_instrument.data = True
    #print "INSTRUMENT FORM SUBMIT: "+str(instrument_form.submit_instrument.data)
    print "ERRORS BEFORE VALIDATE: "+str(form.errors)
    if form.validate_on_submit():
        num_days = form.num_days.data
        music_key = form.music_key.data
        min_mag = form.min_mag.data
        tempo = form.tempo.data
        base_octave = form.base_octave.data
        octave_range = form.octave_range.data
        patches = []
        for elem in form.patches.data:
            patches.append(elem['instrument'])
        print "PATCHES: "+str(patches)
        latitude = form.latitude.data
        longitude = form.longitude.data
        location = (float(latitude), float(longitude))
        for i in request.form:
            print i
        #submit = form.submit_music
        #print "SUBMT MUSIC: "+str(submit.data)
        #if submit.data:
        if 'submit-music' in request.form:
            earthquake2Midi.generateMidi(num_days, min_mag, location, tempo, base_octave, octave_range, music_key, patches)
            flash('Your song is being generated')
            flash(patches)
            print(patches)
            #import pdb; pdb.set_trace()
            print "ERRORS AFTER VALIDATE: "+str(form.errors)
            return redirect(url_for('quakemusic'))
    print str(form.errors)
    return render_template('index_bs.html',
                           title='Home',
                           form=form)

@app.route('/quakemusic', methods=['GET', 'POST'])
def quakemusic():
    return render_template('quakemusic.html')


@app.route('/login', methods=['GET', 'POST'])
#@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
#@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

#@oid.after_login
def after_login(resp):
    flash(resp.email)
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/follow/<nickname>')
#@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
#@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))
