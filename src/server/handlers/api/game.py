import logging
from tornado.web import RequestHandler
from tornado.escape import json_decode, json_encode
from src.db import (
    DBSession, Session, Game, Round,
    SetUpPhase, CluePhase, VotePhase, RevealPhase
)
from src.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class GameAPIHandler(RequestHandler):
    async def get(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.error("Cannot create game without session.")
            self.send_error(status_code=400)
            return

        game_name = self.get_argument('gameName', None)
        db_session = DBSession()
        existing_game = db_session.query(Game).filter(Game.name == game_name).first()
        if existing_game is None:
            logger.error("Could not find game with name %s", game_name)
            self.send_error(status_code=404)
            return

        db_session.query(Session).filter(Session.id == int(session_id)).update({'game_id': existing_game.id})
        db_session.commit()
        db_session.close()
        return {'success': True}

    async def post(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.error("Cannot create game without session.")
            self.send_error(status_code=400)
            return

        try:
            json_data = json_decode(self.request.body)
            game_name = json_data['gameName']
        except (ValueError, KeyError):
            logger.error("Did not receive game name.")
            self.send_error(status_code=400)
            return

        db_session = DBSession()
        self._init_game(session_id=int(session_id), game_name=game_name, db_session=db_session)
        self.set_status(status_code=200)
        self.write(json_encode({'success': True}))
        db_session.close()

    def _init_game(
            self,
            session_id: int,
            game_name: str,
            db_session: 'DBSession'
    ):
        new_game = Game(
            name=game_name
        )
        db_session.add(new_game)
        db_session.commit()
        logger.info("Committed game!")

        new_round = Round(
            game_id=new_game.id,
        )
        db_session.add(new_round)
        db_session.commit()
        logger.info("Committed round!")

        db_session.add(SetUpPhase(round_id=new_round.id))
        db_session.add(CluePhase(round_id=new_round.id))
        db_session.add(VotePhase(round_id=new_round.id))
        db_session.add(RevealPhase(round_id=new_round.id))
        db_session.commit()
        logger.info("Committed phases!")

        session = db_session.query(Session).filter_by(id=session_id).first()
        session.game_id = new_game.id
        db_session.add(session)
        db_session.commit()
        logger.info(f"Added game_id: {new_game.id} to session with id: {session.id}")
