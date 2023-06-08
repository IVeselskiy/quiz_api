
from marshmallow import post_load, validates
from flasgger import Schema, fields, ValidationError

from models import Questions, get_question_by_id


class QuestionsSchema(Schema):
    id = fields.Int(dump_only=True)
    question_id = fields.Int(required=True)
    question_text = fields.Str(required=True)
    answer = fields.Str(required=True)
    created_at = fields.DateTime(required=True)

    @validates('question_id')
    def validate_question(self, question_id, **kwargs) -> None:
        if get_question_by_id(question_id) is not None:
            raise ValidationError('Этот вопрос уже есть в базе данных.')

    @post_load
    def create_question(self, data: dict, **kwargs) -> Questions:
        return Questions(**data)


class RequestsSchema(Schema):
    id = fields.Int(dump_only=True)
    questions_num = fields.Int(required=True, default=1)

    @validates('questions_num')
    def validate_question(self, questions_num: int, **kwargs) -> None:
        if questions_num <= 0 or questions_num >= 10:
            raise ValidationError('Число должно быть от 1 до 10.')
