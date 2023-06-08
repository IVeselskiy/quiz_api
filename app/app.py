from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import Swagger, APISpec, swag_from
from flask import Flask, request, Response
from flask_restful import Api, Resource
from marshmallow import ValidationError

import logging
import requests

from models import init_db, get_all_questions, add_question, delete_all_questions, get_previous_question, add_requests
from schemas import QuestionsSchema, RequestsSchema


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel('DEBUG')


app = Flask(__name__)
api = Api(app)


spec = APISpec(
    title='QuestionsList',
    version='1.0.0',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)


URL: str = 'https://jservice.io/api/random'


@app.before_request
def before_request():
    """Этот эндпойнт создает таблицу questions в базе данных."""
    init_db()


class QuestionsList(Resource):

    @swag_from('./docs/get_questions.yml')
    def get(self) -> tuple[list[dict], int]:
        """Этот эндпойнт возвращает все вопросы из базы данных."""

        schema = QuestionsSchema()
        db_is_not_empty = get_all_questions()
        if db_is_not_empty:
            return schema.dump(db_is_not_empty, many=True), 200
        return [{'message': 'В базе данных нет ни одного вопроса.'}], 200

    @swag_from('./docs/post_questions.yml')
    def post(self) -> tuple[Response, int] or Response:
        """Этот эндпойнт добавляет указанное количество вопросов в базу данных и возвращает предыдущий вопрос."""

        previous_question = get_previous_question()

        data = request.json
        schema = RequestsSchema()
        try:
            questions_num = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        number = questions_num['questions_num']
        logger.info(f"Запрошено вопросов - {number}.")
        add_requests(number)

        logger.info(f"Выполнение запроса.")

        num = 0
        logger.debug(f"{num}")
        while num < number:
            logger.debug(f'Запрос номер {1 + num}.')
            result = requests.get(URL).json()

            logger.debug(f'Получен ответ {result}')
            question_id: int = int(result[0]['id'])
            question_text: str = result[0]['question']
            answer: str = result[0]['answer']
            created_at: str = result[0]['created_at']

            new_question = {
                'question_id': question_id,
                'question_text': question_text,
                'answer': answer,
                'created_at': created_at,
            }
            logger.debug(f'Новый вопрос {new_question}.')

            schema = QuestionsSchema()
            try:
                data = schema.load(new_question)
                num += 1
                logger.debug(f'Вопрос №{num} - {data}')
            except ValidationError as exc:
                return exc.messages, 400

            add_question(data)

        logger.debug(f'Конец цикла while. Добавлено {num} вопросов.')
        if previous_question:
            schema = QuestionsSchema()
            return schema.dump(previous_question, many=False), 201
        return [{}], 201

    @swag_from('./docs/delete_questions.yml')
    def delete(self) -> tuple[list[dict], int]:
        """Этот эндпойнт удаляет все данные из таблицы Questions."""
        delete_all_questions()
        return [{'message': 'Все вопросы удалены из базы данных.'}], 200


template = spec.to_flasgger(
    app,
    definitions=[QuestionsSchema, RequestsSchema],
)

swagger = Swagger(app, template=template)

api.add_resource(QuestionsList, '/api/questions')


if __name__ == '__main__':
    logger.info('Старт работы программы Quiz.')
    app.run(debug=True)
