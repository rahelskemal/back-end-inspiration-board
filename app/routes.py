from flask import Blueprint, request, jsonify, abort, make_response
from app import db
from app.models.card import Card
from app.models.board import Board

# example_bp = Blueprint('example_bp', __name__)

cards_bp = Blueprint("cards",__name__, url_prefix="/cards")


def validate_id(cls, id):
    try: 
        id = int(id)
    except:
        abort(make_response ({"message":f"{cls.__name__} {id} invalid"}, 400))

    obj = cls.query.get(id)

    if not obj:
        abort(make_response({"message":f"{cls.__name__} {id} not found"}, 404))

    return obj

@cards_bp.route("/<card_id>", methods=["GET"])
def get_one_card(card_id):
    card = validate_id(Card, card_id)

    return {
        "message": card.message
    }

#have a call to update board
@cards_bp.route("/<card_id>",methods=["DELETE"])
def delete_card(card_id):
    card=validate_id(Card,card_id)
    db.session.delete(card)
    db.session.commit()
    return make_response({"details":f'Card {card_id} "{card.message}" successfully deleted'})




@cards_bp.route("/<card_id>",methods=["PUT"])
def update_card(card_id):
    request_body=request.get_json()
    card=validate_id(Card,card_id)
    card.likescount=request_body["likes"]
    db.session.commit()
    return make_response({"details":f'Card{card_id} "{card.message} "  successfully updated'})

boards_bp = Blueprint("boards",__name__, url_prefix="/boards")


@boards_bp.route("/<board_id>/cards", methods=["GET"])
def get_cards_for_boards(board_id):
    board = validate_id(Board, board_id)

    response_body = []
    for card in board.cards:
        response_body.append(card.card_dict())

    return {
        "id": board.id,
        "title": board.title,
        "author": board.author,
        "cards": response_body
    }

@boards_bp.route("", methods=["POST"])
def create_board():
    request_body=request.get_json()
    new_board = Board(title= request_body["title"],author=request_body["author"])

    db.session.add(new_board)
    db.session.commit()

    return {
        "id": new_board.id,
        "title": new_board.title,
        "author": new_board.author,    
    }, 201


@boards_bp.route("/<board_id>/cards", methods=["POST"])
def post_card_id_to_board(board_id):
    board = validate_id(Board, board_id)

    request_body = request.get_json()


    if "message" not in request_body: 
        return make_response({"details": "Invalid data"
    }, 400)


    new_card = Card(
        message=request_body["message"],
        board = board
    ) 

    db.session.add(new_card)
    db.session.commit()


    return {
        "id": new_card.id,
        "message": new_card.message
    }, 201



@boards_bp.route("", methods=["GET"])
def get_all_boards():
    board_list = []

    boards= Board.query.all()

    for board in boards:
        board_list.append(board.board_dict())
    
    return jsonify(board_list)

@boards_bp.route("/<board_id>", methods=["GET"])
def get_one_board(board_id):
    board = validate_id(Board, board_id)

    return board.board_dict(), 200
