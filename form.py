from wtforms import (Form, TextField, validators, SubmitField,
DecimalField, IntegerField)

class ReusableForm(Form):
    # start string
    start_string = TextField("Start text:", default = 'SCULLY: Mulder, ', validators = [validators.InputRequired()])
    # temperature
    temperature = DecimalField('Prediction temperature:', default = 0.7,
                             validators = [validators.InputRequired(),
                                         validators.NumberRange(min = 0.1, max = 1.0,
                                         message ='Temperature must be between 0.1 and 1')])
    # character length
    char_length = IntegerField('Character length:',
                         default = 1000, validators = [validators.InputRequired(),
                                                 validators.NumberRange(min = 500, max = 3000,
                                                 message = 'Number of characters must be between 500 and 3000 (for performance reasons)')])
    # submit
    submit = SubmitField("GENERATE")
