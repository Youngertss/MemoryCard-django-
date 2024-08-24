import sys
sys.path.append('../')
from users.models import *
sys.path.remove('../')

def random_bot(request):
    bot = CustomUsers.objects.filter(is_bot=True).order_by("?").first()
    if not bot:
        bot = {"slug":"no_one_bot_is_alive"}
    return {'random_bot': bot}