from flask_wtf import FlaskForm
from wtforms import *
#from wtforms import StringField, BooleanField, TextAreaField, IntegerField, SelectField, DecimalField, SelectMultipleField, SubmitField, HiddenField, widgets
from wtforms.validators import DataRequired, Length, NumberRange
# from app.models import User
# from flask_babel import gettext
from config import SCALES, SCALES_WRITTEN, PATCHES

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(gettext('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class InstrumentGroupForm(FlaskForm):
    pass

class InstrumentForm(FlaskForm):
    instrument = SelectField('Instruments', choices=PATCHES, coerce=int, description=u'List of desired patches (0-127) to be mapped to output based on magnitude (low to high).')
    #submit_instrument = SubmitField('Add Patch')

class MusicForm(FlaskForm):
    num_days = IntegerField('Number Of Days', validators=[DataRequired()], default=7, description=u'Number of days back from current day to collect earthquake data')
    music_key = SelectField('Musical Key', validators=[DataRequired()], description=u'Key in which to generate notes (i.e. "EbMINOR")', choices=SCALES_WRITTEN, default='CHROMATIC')
    min_mag = DecimalField('Minimum Magnitude', validators=[DataRequired()], description=u'Minimum magnitude of earthquake to include in note list.', default=2.5)
    tempo = IntegerField('Tempo (BPM)', validators=[DataRequired(), NumberRange(min=60, max=240)], description=u'Tempo in beats per minute.', default=120)
    base_octave = IntegerField('Base Octave (0-10)', validators=[DataRequired(), NumberRange(min=0, max=10)], description=u'Base octave for output (0 lowest to 10 highest).', default=3)
    octave_range = IntegerField('Octave Range (1-9)', validators=[DataRequired(), NumberRange(min=1, max=9)], description=u'Octave range for output (1 to 9, depending on base octave).', default=5)
    patches = FieldList(FormField(InstrumentForm), validators=[DataRequired()], min_entries=0)
    #patches = MultiCheckboxField('Instruments', choices=PATCHES, coerce=int, description=u'List of desired patches (0-127) to be mapped to output based on magnitude (low to high).')
    latitude = HiddenField('Latitude', id="latitude", validators=[DataRequired()])
    longitude = HiddenField('Longitude', id="longitude", validators=[DataRequired()])
    #submit_music = SubmitField('Create Music')

class LoginForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class PostForm(FlaskForm):
    post = StringField('post', validators=[DataRequired()])
