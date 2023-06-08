import logging

from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect, desc
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel('INFO')


engine = create_engine('postgresql+psycopg2://admin:admin@quiz_db:5432/quiz_db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Questions(Base):
    """Модель для хранения вопросов и ответов для викторины."""
    __tablename__ = 'questions'

    id: int = Column(Integer, primary_key=True)
    question_id: int = Column(Integer, unique=True, nullable=True)
    question_text: str = Column(String(250), nullable=True)
    answer: str = Column(String(250), nullable=True)
    created_at: DateTime = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'id: {self.id}, ' \
               f'question_id: {self.question_id}, ' \
               f'question_text: {self.question_text},' \
               f'answer: {self.answer},' \
               f'created_at: {self.created_at}'

    def to_json(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Requests(Base):
    """Модель для хранения вопросов и ответов для викторины."""
    __tablename__ = 'requests'

    id: int = Column(Integer, primary_key=True)
    questions_num: int = Column(Integer, nullable=True)

    def __repr__(self):
        return f'id: {self.id}, ' \
               f'questions_num {self.question_id}'

    def to_json(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def init_db() -> None:
    ins = inspect(engine)
    questions_table_exist = ins.dialect.has_table(engine.connect(), 'questions')
    requests_table_exist = ins.dialect.has_table(engine.connect(), 'requests')

    if not questions_table_exist:
        Base.metadata.create_all(bind=engine)
        logger.info(f'Таблица "questions" успешно создана.')

    if not requests_table_exist:
        Base.metadata.create_all(bind=engine)
        logger.info(f'Таблица "requests" успешно создана.')


def get_all_questions() -> list:
    return session.query(Questions).all()


def get_previous_question():
    previous_questions = session.query(Questions).order_by(desc(Questions.id)).first()
    if previous_questions:
        return previous_questions


def get_question_by_id(question_id: int) -> None or dict:
    question_in_db = session.query(Questions).filter(Questions.question_id == question_id).one_or_none()
    return question_in_db


def add_question(question: Questions) -> None:
    logger.debug(f'Добавление вопроса {question}')
    new_question = Questions(
        question_id=question.question_id,
        question_text=question.question_text,
        answer=question.answer,
        created_at=question.created_at,
        )

    session.add(new_question)
    session.commit()
    logger.info(f'Вопрос id: {question.question_id} добавлен в базу данных.')


def delete_all_questions() -> None:
    session.query(Questions).delete()
    session.commit()
    logger.info('Все вопросы удалены из базы данных.')


def get_all_requests() -> list:
    return session.query(Requests).all()


def add_requests(questions_num: int) -> None:
    new_request = Requests(
        questions_num=questions_num
        )

    session.add(new_request)
    session.commit()
    logger.info(f'Новый запрос добавлен в базу данных.')


def delete_all_requests() -> None:
    session.query(Requests).delete()
    session.commit()
    logger.info('Все запросы удалены из базы данных.')
