sys.path.append('../')
from users.models import *
sys.path.remove('../')

def random_bot(request):
    bot = CustomUsers.objects.filter(is_bot=True).order_by("?").first()
    return {'random_bot': bot}