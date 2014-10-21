from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class SequencesView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])    
        if project is None:
            return "[]"
    
        # TODO(silverasm): in the case where there's no query_id, use the
        # sequence count table directly.
        length = int(params["length"][0])
        sequence_query = None;
        if "query_id" in params:
            query = Query.query.get(params["query_id"])
            sequence_query = db.session.query(
                Sequence.id,
                Sequence.lemmatized.label("lemmatized"),
                Sequence.has_function_words.label("has_function_words"),
                Sequence.sequence.label("sequence"),
                func.count(Sentence.id).label("sentence_count"),
                func.count(Sentence.document_id.distinct()).label("document_count")).\
                group_by(Sequence.id).\
                filter(Sentence.project_id == project.id).\
                join(SentenceInQuery,
                     SentenceInQuery.sentence_id == Sentence.id).\
                filter(SentenceInQuery.query_id == query.id).\
                filter(Sequence.all_function_words == False).\
                filter(Sequence.length == length).\
                filter(Sequence.id == SequenceInSentence.sequence_id).\
                filter(Sentence.id == SequenceInSentence.sentence_id)
        else:
            # There's no query id, we just want the most frequent sequences in
            # the whole collection.
            sequence_query = db.session.query(
                Sequence.id,
                Sequence.lemmatized.label("lemmatized"),
                Sequence.has_function_words.label("has_function_words"),
                Sequence.sequence.label("sequence"),
                SequenceCount.sentence_count.label("sentence_count"),
                SequenceCount.document_count.label("document_count")).\
            filter(SequenceCount.project_id == project.id).\
            filter(SequenceCount.sequence_id == Sequence.id).\
            filter(Sequence.length == length)

        sequence_query = sequence_query.order_by(desc("sentence_count"))
        results = []
        for sequence in sequence_query:
            results.append({
                "id": sequence.id,
                "count": sequence.sentence_count,
                "document_count": sequence.document_count,
                "sentence_count": sequence.sentence_count,
                "has_function_words": 1 if sequence.has_function_words else 0,
                "lemmatized": 1 if sequence.lemmatized else 0,
                "sequence": sequence.sequence,
                "length": length
            })

        return jsonify(results = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass


register_rest_view(
    SequencesView,
    wordseer,
    'sequences_view',
    'sequence',
    parents=["project"],
)