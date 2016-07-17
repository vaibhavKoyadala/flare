from models import Joker

class JokerMiddleware(object):
    def process_request(self, request):
        session = request.session
        joker_id = session.get('joker_id', default=None)
        try:
            joker=Joker.objects.get(pk=joker_id)
        except Joker.DoesNotExist:
            joker=None

        request.joker = joker
