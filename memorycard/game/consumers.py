import json
import random

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


from .models import *

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECT", self.scope['user'].slug)
        self.game_name = str(self.scope["url_route"]["kwargs"]["user_slug1"]) + "_" + str(self.scope["url_route"]["kwargs"]["user_slug2"])
        self.game_group_name = f"lobby_{self.game_name}"
        self.winner = ''
        
        info = await self.start_info_game()
        info['curr_user'] = self.scope['user'].slug
        # print(self.scope)

        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        
        await self.accept()
        # await self.user_in(self.scope['user'].slug)
        
        await self.send(text_data=json.dumps(info))



    @database_sync_to_async
    def start_info_game(self):
        try:
            curr_game = Games.objects.get(game_slug = self.game_name)
        except:
            curr_game = None
        
        if curr_game:
            cards = list(
            curr_game.cards.all().values(
                'rank', 'color', 'flipped', 'guessed', 'order'
                )
            )
            if not curr_game.first_user.photo:
                url1 = "https://static.vecteezy.com/system/resources/previews/002/275/847/original/male-avatar-profile-icon-of-smiling-caucasian-man-vector.jpg"
            else:
                url1 = curr_game.first_user.photo.url
            
            if not curr_game.second_user.photo:
                url2 = "https://static.vecteezy.com/system/resources/previews/002/275/847/original/male-avatar-profile-icon-of-smiling-caucasian-man-vector.jpg"
            else:
                url2 = curr_game.second_user.photo.url
            print(url1, "\n\n", url2)
            context = {
                'first_user': curr_game.first_user.slug,
                'score_first_user': curr_game.score_first_user,
                'first_avatar_url': url1,
                
                'second_user': curr_game.second_user.slug,
                'score_second_user': curr_game.score_second_user,
                'second_avatar_url': url2,
                
                'is_turn_first_user': curr_game.is_turn_first_user,  # Установите начальное значение
                'cards': cards,  # Получите все карточки для этой игры
            }
            print(context)
            return context
        else:
            context = {
                'action':"end_game",
                'winner': self.winner, 
            }
            print("Conext",context)
            return context
            
    
    async def new_member_message(self, event):
        pass
    async def chat_update_message(self, event):
        pass
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json["action"]
        
        if action == "change_turn":
            answer = await self.change_turn()
            
            await self.channel_layer.group_send(
                self.game_group_name, {"type": "send_turn", "action":action ,"is_turn_first_user": answer}
            )
        elif action == "was_flipped":
            card_index, username = text_data_json["order"], text_data_json["username"]
            updated_card = await self.flip_this_card(card_index, username)
            if updated_card:
                await self.channel_layer.group_send(
                    self.game_group_name, {"type": "send_updated_card", "action":action ,"updated_card": updated_card}
                )
            
        elif action == "was_guessed":
            card1_order, card2_order, user = text_data_json["card1_order"], text_data_json["card2_order"], text_data_json["user"]  #dicts: rank, color, order
            updated_cards_guessed = await self.card_was_guessed(card1_order, card2_order, user)
            if updated_cards_guessed:
                await self.channel_layer.group_send(
                    self.game_group_name, {"type": "send_guessed_card", "action":action ,"updated_cards_guessed": updated_cards_guessed}
                )
                
        elif action == "end_game": 
            winner, loser = text_data_json["winner"], text_data_json["loser"]
            self.winner = winner
            await self.end_game(winner, loser)
            await self.channel_layer.group_send(
                    self.game_group_name, {"type": "send_end_game", "action":action ,"winner": self.winner}
                )
    
        else:
            text = text_data_json["text"]
            
            await self.channel_layer.group_send(
                self.game_group_name, {"type": "send_message", "action":action ,"text": text}
            )
            
    @database_sync_to_async
    def end_game(self, winner, loser):
        winner = CustomUsers.objects.get(slug = winner)

        winner.wins += 1
        winner.games += 1
        winner.save()
        
        loser = CustomUsers.objects.get(slug = loser)
        loser.games += 1
        loser.save()
        
        curr_game = Games.objects.get(game_slug = self.game_name)
        for i in range(1,17):#пока что так
            card = Card.objects.get(game = curr_game, order = i)
            card.delete()
        print("Карты удалены наверн")
        try:
            curr_game.delete()
            print(":) ГЕЙМ Удалил")
        except:
            print("Не удалось удалить игру")
        
        
    @database_sync_to_async
    def card_was_guessed(self, card1_order, card2_order, user):
        curr_game = Games.objects.get(game_slug = self.game_name)
        
        if curr_game.first_user.slug == user:
            curr_game.score_first_user += 1
        elif curr_game.second_user.slug == user:
            curr_game.score_second_user += 1
        curr_game.save()
        
        card1 = Card.objects.get(game=curr_game.id, order=card1_order)
        card2 = Card.objects.get(game=curr_game.id, order=card2_order)
        if card1.rank == card2.rank and card1.color == card2.color:
            card1.guessed = True
            card1.save()
            
            card2.guessed = True
            card2.save()
            cards_info = [
                {
                    "card1":{'order':card1.order},
                    "card2":{'order':card2.order},
                    'score_first_user': curr_game.score_first_user,
                    'score_second_user': curr_game.score_second_user,
                }
                ]

            print("Эти карточки были УГАДАНЫ; ихний order: ", cards_info)
            return cards_info
        else:
            print("Ты шо это разные карты")
            cards_info = [
                {
                    "card1":{'order':card1.order},
                    "card2":{'order':card2.order},
                    'score_first_user': curr_game.score_first_user,
                    'score_second_user': curr_game.score_second_user,
                }
                ]

            print("Эти карточки РАЗНЫЕ, я их НЕ УДАЛИЛ; ихний order: ", cards_info)
            return None
    
    @database_sync_to_async
    def flip_this_card(self, order, username):
        curr_game = Games.objects.get(game_slug = self.game_name)
        print(".............", order,"\n", username,"\n", curr_game.is_turn_first_user,"\n", curr_game.first_user.slug)
        if username == curr_game.first_user.slug and curr_game.is_turn_first_user or username == curr_game.second_user.slug and not curr_game.is_turn_first_user:
            current_card = Card.objects.get(game=curr_game.id, order=order)
            current_card.flipped = not current_card.flipped
            current_card.save()
            

            card_info = [{"rank":current_card.rank}, {"color":current_card.color}, {'flipped':current_card.flipped},
            {"guessed":current_card.guessed}, {'order':current_card.order}]
            
            print("Эта карточка перевернулась, и теперь выглядит так: ",card_info)
            return card_info
        else:
            return False

    
    @database_sync_to_async
    def change_turn(self):
        curr_game = Games.objects.get(game_slug = self.game_name)
        curr_game.is_turn_first_user = not curr_game.is_turn_first_user
        curr_game.save()
        print("Теперь ход:", curr_game.is_turn_first_user)
        return curr_game.is_turn_first_user
    
    async def send_end_game(self, event):
        action = event["action"]
        winner = event["winner"]
        await self.send(text_data=json.dumps({'action': action, "winner": winner}))
        
    async def send_guessed_card(self, event):
        action = event["action"]
        updated_cards_guessed = event["updated_cards_guessed"]
        await self.send(text_data=json.dumps({'action': action, "updated_cards_guessed": updated_cards_guessed}))
        
    async def send_updated_card(self, event):
        action = event["action"]
        updated_card = event["updated_card"]
        await self.send(text_data=json.dumps({'action': action, "updated_card": updated_card}))  
    
    async def send_turn(self, event):
        action = event["action"]
        is_turn_first_user = event["is_turn_first_user"]
        await self.send(text_data=json.dumps({'action': action, "is_turn_first_user": is_turn_first_user}))
    
    async def send_message(self, event):
        action = event["action"]
        text = event["text"]
        await self.send(text_data=json.dumps({'action': action, "text": text}))
    
    @sync_to_async
    def user_in (self, user_slug):
        print('user in')
        curr_game = Games.objects.get(game_slug = self.game_name)
        user1_slug, user2_slug = self.game_name.split("_")
        
        if user_slug == user1_slug:
            if not curr_game.first_user:
                print(1, 'user in')
                this_user = CustomUsers.objects.get(slug=user1_slug)
                curr_game.first_user = this_user
            
        elif user_slug == user2_slug:
            if not curr_game.second_user:
                print(2, 'user in')
                this_user = CustomUsers.objects.get(slug=user2_slug)
                curr_game.second_user = this_user
    
    @sync_to_async
    def user_out (self, user_slug):
        print('user out')
        curr_game = Games.objects.get(game_slug = self.game_name)
        if user_slug == curr_game.first_user.slug:
            print('1 user out')
            curr_game.first_user = None
            return True
        elif user_slug == curr_game.second_user.slug:
            print('2 user out')
            curr_game.second_user = None
            return True
        if not curr_game.first_user and not curr_game.second_user:
            Card.objects.filter(game=curr_game.id).delete()
            print("JHO DELETESES")
            curr_game.delete()
            return True
            

    
    async def disconnect(self, close_code):
        print("DISCONNECT", self.scope['user'].slug)
        # print(self.user_out(self.scope['user'].slug))

        
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

#############################################################################################################################

class GameConsumerWithbot(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECT", self.scope['user'].slug)
        self.bots_slug = str(self.scope["url_route"]["kwargs"]["user_slug2"])
        self.game_name = str(self.scope["url_route"]["kwargs"]["user_slug1"]) + "_" + self.bots_slug
        self.winner = '_'
        
        info = await self.start_info_game()
        info['curr_user'] = self.scope['user'].slug
        
        
        self.bots_info = await self.get_bots_info() #contains 16 names(rank+color) of cards, index 0 = 1-st order (so index 15=16-th order)
        self.bots_ideas = [] #contains names(rank+color) of cards, that already exist in bots_info in 2 instance
        
        if len(self.bots_info) == 0:
            self.bots_info = [0]*16
        # print(self.scope)

        # await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        
        await self.accept()
        # await self.user_in(self.scope['user'].slug)
        
        await self.send(text_data=json.dumps(info))

    @database_sync_to_async
    def get_bots_info(self):
        try:
            curr_game = Games.objects.get(game_slug = self.game_name)
            bt_info = curr_game.bots_info
            print(bt_info)
            return bt_info
        except:
            curr_game = None

    @database_sync_to_async
    def start_info_game(self):
        try:
            curr_game = Games.objects.get(game_slug = self.game_name)
        except:
            curr_game = None
        
        if curr_game:
            #get list with card's info
            cards = list(
            curr_game.cards.all().values(
                'rank', 'color', 'flipped', 'guessed', 'order'
                )
            )
            
            #urls to photo
            if not curr_game.first_user.photo:
                url1 = "https://static.vecteezy.com/system/resources/previews/002/275/847/original/male-avatar-profile-icon-of-smiling-caucasian-man-vector.jpg"
            else:
                url1 = curr_game.first_user.photo.url

            url2 = "https://forum.evanotend.com/uploads/gallery/category_48/gallery_15345_48_91607.jpg"

            print(url1, "\n\n", url2)
            
            context = {
                'first_user': curr_game.first_user.slug,
                'score_first_user': curr_game.score_first_user,
                'first_avatar_url': url1,
                
                'second_user': curr_game.second_user.slug,
                'score_second_user': curr_game.score_second_user,
                'second_avatar_url': url2,
                
                'is_turn_first_user': curr_game.is_turn_first_user, 
                'cards': cards,  
            }
            print(context)
        else: #it means that game is already end
            context = {
                'action':"end_game",
                'winner': self.winner, 
            }
            print("Conext",context)

        return context

        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json["action"]
        
        if action == "change_turn":
            data_after_bots_actions = await self.bots_turn()
            
            await self.send_turn({"action":action , "data_after_bots_actions": data_after_bots_actions})

        elif action == "was_flipped":
            card_index, username = text_data_json["order"], text_data_json["username"]
            updated_card = await self.flip_this_card(card_index, username)
            if updated_card:
                await self.send_updated_card({"action":action ,"updated_card": updated_card})
            
        elif action == "was_guessed":
            card1_order, card2_order, user = text_data_json["card1_order"], text_data_json["card2_order"], text_data_json["user"]  #dicts: rank, color, order
            updated_cards_guessed = await self.card_was_guessed(card1_order, card2_order, user)
            if updated_cards_guessed:
                await self.send_guessed_card({"action":action ,"updated_cards_guessed": updated_cards_guessed})
            
        elif action == "end_game": 
            winner, loser = text_data_json["winner"], text_data_json["loser"]
            self.winner = winner
            await self.end_game(winner, loser)
            await self.send_end_game({"action":action ,"winner": self.winner})
    
        else:
            text = text_data_json["text"]
            
            await self.send_message({"action":action ,"text": text})

            
    @database_sync_to_async
    def end_game(self, winner, loser):
        self.winner = winner
        
        curr_game = Games.objects.get(game_slug = self.game_name)
        for i in range(1,17): #пока что так
            card = Card.objects.get(game = curr_game, order = i)
            card.delete()
        print("Карты удалены наверн")
        try:
            curr_game.delete()
            print(":) ГЕЙМ Удалил")
        except:
            print("Не удалось удалить игру")
        
        
    @database_sync_to_async
    def card_was_guessed(self, card1_order, card2_order, user):
        curr_game = Games.objects.get(game_slug = self.game_name)
        
        if curr_game.first_user.slug == user:
            curr_game.score_first_user += 1
        elif curr_game.second_user.slug == user:
            curr_game.score_second_user += 1
        curr_game.save()
        
        card1 = Card.objects.get(game=curr_game.id, order=card1_order)
        card2 = Card.objects.get(game=curr_game.id, order=card2_order)
        if card1.rank == card2.rank and card1.color == card2.color:
            card1.guessed = True
            card1.save()
            
            card2.guessed = True
            card2.save()
            cards_info = [
                {
                    "card1":{'order':card1.order},
                    "card2":{'order':card2.order},
                    'score_first_user': curr_game.score_first_user,
                    'score_second_user': curr_game.score_second_user,
                }
                ]
            #it means that these cards were guessed and bot should't use them
            self.bots_info[card1.order-1] = -1
            if str(card1.rank)+card1.color in self.bots_ideas:
                self.bots_ideas.remove(str(card1.rank)+card1.color)
            self.bots_info[card2.order-1] = -1
            
            print("Эти карточки были УГАДАНЫ; ихний order: ", cards_info)
            return cards_info
        else:
            print("Ты шо это разные карты")
            cards_info = [
                {
                    "card1":{'order':card1.order},
                    "card2":{'order':card2.order},
                    'score_first_user': curr_game.score_first_user,
                    'score_second_user': curr_game.score_second_user,
                }
                ]

            print("Эти карточки РАЗНЫЕ, я их НЕ УДАЛИЛ; ихний order: ", cards_info)
            return None
    
    @database_sync_to_async
    def flip_this_card(self, order, username):
        curr_game = Games.objects.get(game_slug = self.game_name)
        print(".............", order,"\n", username,"\n", curr_game.is_turn_first_user,"\n", curr_game.first_user.slug)
        if username == curr_game.first_user.slug and curr_game.is_turn_first_user or username == curr_game.second_user.slug and not curr_game.is_turn_first_user:
            current_card = Card.objects.get(game=curr_game.id, order=order)
            current_card.flipped = not current_card.flipped
            current_card.save()
            if current_card.flipped and self.bots_info[order-1] == 0:
                added = str(current_card.rank)+current_card.color
                if added in self.bots_info: #at the next turn we will flip it first
                    self.bots_ideas.append(added)
                self.bots_info[order-1] = added
            
            card_info = [{"rank":current_card.rank}, {"color":current_card.color}, {'flipped':current_card.flipped},
            {"guessed":current_card.guessed}, {'order':current_card.order}]
            
            print("Эта карточка перевернулась, и теперь выглядит так: ",card_info)
            return card_info
        else: #it is not your turn!
            return False

    
    @database_sync_to_async #script of bot's decisions, returns 2 lists: flipped and guessed cards
    def bots_turn(self):
        curr_game = Games.objects.get(game_slug = self.game_name)
        
        #these lists contains ORDERS from db field, not indexes!
        cards_flipped = []
        cards_guessed = []

        #moves, that bases on list of "bots_ideas"
        for idea in range(len(self.bots_ideas)):
            for card in range(len(self.bots_info)):
                if self.bots_ideas[idea] == self.bots_info[card]:
                    cards_flipped.append(card+1) #+1 because we need order, not index
                    cards_guessed.append(card+1)
                    self.bots_info[card] = -1
        print("Pre moves from bot, result:",cards_flipped, cards_guessed)
        self.bots_ideas.clear()
        
        #moves with random and memory
        list_to_choice = [i for i, x in enumerate(self.bots_info) if x==0] #it contains indexes of place with zeros from bots_info
        moves = 2
        last_card_name = ''
        end_game = False
        while moves!=0:
            if list_to_choice == []:
                end_game=True
                break
            moves-=1
            card_index = random.choice(list_to_choice)
            cards_flipped.append(card_index)
            list_to_choice.remove(card_index)
            
            card = Card.objects.get(game=curr_game, order=card_index+1)
            card_name = str(card.rank)+card.color
            if card_name in self.bots_info:
                if moves==1:
                    second_card_index = self.bots_info.index(card_name)
                    cards_flipped.append(second_card_index)
                    
                    self.bots_info[second_card_index] = -1
                    self.bots_info[card_index] = -1
                    cards_guessed.append(card_index+1) #+1 because we need order, not index
                    cards_guessed.append(second_card_index+1)
                    moves = 2
                elif card_name==last_card_name:
                    second_card_index = cards_flipped[-1]-1
                    
                    self.bots_info[second_card_index] = -1
                    self.bots_info[card_index] = -1
                    cards_guessed.append(card_index+1) #+1 because we need order, not index
                    cards_guessed.append(second_card_index+1)
                    moves = 2
                else:
                    self.bots_ideas.append(card_name)
                    
            else:
                self.bots_info[card_index] = card_name
            last_card_name = card_name
        
        print("Script moves from bot, result:",cards_flipped, cards_guessed)
        #save changes regarding guessed cards
        for order in cards_guessed:
            card = Card.objects.get(game=curr_game, order=order)
            card.guessed = True
            card.save()
        
        curr_game.score_second_user += int(len(cards_guessed)/2)
        curr_game.save()
        #result
        data_after_bots_actions = {
            "cards_flipped":cards_flipped,
            "cards_guessed":cards_guessed,
            'score_second_user': curr_game.score_second_user,
            "is_turn_first_user": True,
            "end_game":end_game
        }
        return data_after_bots_actions
    
    async def send_end_game(self, event):
        action = event["action"]
        winner = event["winner"]
        await self.send(text_data=json.dumps({'action': action, "winner": winner}))
        
    async def send_guessed_card(self, event):
        action = event["action"]
        updated_cards_guessed = event["updated_cards_guessed"]
        await self.send(text_data=json.dumps({'action': action, "updated_cards_guessed": updated_cards_guessed}))
        
    async def send_updated_card(self, event):
        action = event["action"]
        updated_card = event["updated_card"]
        await self.send(text_data=json.dumps({'action': action, "updated_card": updated_card}))  
    
    async def send_turn(self, event):
        action = event["action"]
        is_turn_first_user = event["is_turn_first_user"]
        await self.send(text_data=json.dumps({'action': action, "is_turn_first_user": is_turn_first_user}))
    
    async def send_message(self, event):
        action = event["action"]
        text = event["text"]
        await self.send(text_data=json.dumps({'action': action, "text": text}))

    @database_sync_to_async
    def save_bots_info(self):
        try:
            curr_game = Games.objects.get(game_slug = self.game_name)
            curr_game.bots_info = self.bots_info
            curr_game.save()
            print("bot's info succesfully saved")
        except:
            pass
    
    async def disconnect(self, close_code):
        await self.save_bots_info()
        print("DISCONNECT", self.scope['user'].slug)
        
        # print(self.user_out(self.scope['user'].slug))

        
        # await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

#############################################################################################################################

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_name = self.scope["url_route"]["kwargs"]["lobby_name"]
        self.lobby_group_name = f"lobby_{self.lobby_name}"
        self.user1, self.user2 = self.lobby_name.split('_')

        # Join room group
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)

        await self.accept()

        user = self.scope['user']
        username = user.username
    
        curr_lobby= await self.get_curr_lobby()
        if username.lower() == self.user1:
            curr_lobby.is_user1_in = True
        elif username.lower() == self.user2:
            curr_lobby.is_user2_in = True
        await self.save_curr_lobby_async(curr_lobby)

        
        curr_lobby = await self.get_curr_lobby()
        await self.send(text_data=json.dumps({"action": "chat_update", "text": curr_lobby.message_history}))
        print("UNL")
        
        await self.channel_layer.group_send(
            self.lobby_group_name, {"type": "new_member_message", "action":"new_member" ,"username": username}
        )

        if curr_lobby.is_user1_in and curr_lobby.is_user2_in:
            users_slugs = await self.get_users()
            
            await self.channel_layer.group_send(
                self.lobby_group_name, {"type": "get_started", "action":"start", "user1":users_slugs[0], "user2":users_slugs[1]}
            )

    @database_sync_to_async
    def get_users(self):
        curr_lobby = Lobby.objects.get(lobby_name=self.lobby_name)
        user1 = curr_lobby.user1
        user2 = curr_lobby.user2
        return (user1.slug, user2.slug)
    
    
    @sync_to_async
    def get_curr_lobby(self):
        try:
            curr_lobby = Lobby.objects.get(lobby_name=self.lobby_name)
        except:
            return None
        return curr_lobby
       
    @sync_to_async
    def save_curr_lobby_async(self, lobby):
        lobby.save()
        
    @database_sync_to_async
    def disconnect_db(self):
        try:
            lobby = Lobby.objects.get(lobby_name=self.lobby_name)
        except:
            return None
        user = self.scope['user']
        username = user.slug
        
        if username == self.user1:
            lobby = Lobby.objects.get(lobby_name=self.lobby_name)
            lobby.is_user1_in = False
            lobby.save()
            print("ПЕВРЫЙ = False")
        elif username == self.user2:
            lobby = Lobby.objects.get(lobby_name=self.lobby_name)
            lobby.is_user2_in = False
            lobby.save()
            print("ВТОРОЙ = False")
        if not lobby.is_user1_in and not lobby.is_user2_in:
            try:
                lobby.delete()
                print("LOBBY DELETE SUCC")
            except:
                print("Can't delete lobby in DB")
            
    async def new_member_message(self, event):
        username = event["username"]
        action = event["action"]

        if action == "new_member":
            message = f"{username} присоединился"
        elif action == "left_member":
            message = f"{username} покинул лобби"

        curr_lobby = await self.get_curr_lobby()
        curr_lobby.message_history += message + "\n"
        await self.save_curr_lobby_async(curr_lobby)

        await self.channel_layer.group_send(
            self.lobby_group_name, {"type": "chat_update_message", "text": curr_lobby.message_history, "action": "chat_update"}
        )
        
    async def chat_update_message(self, event):
        text = event["text"]
        action = event["action"]
        await self.send(text_data=json.dumps({"text": text, 'action': action}))
    
    async def get_started(self, event):
        action = event["action"]
        user1 = event["user1"]
        user2 = event["user2"]
        print("GO TO GAME!")
        await self.disconnect_db()
        await self.send(text_data=json.dumps({'action': action, 'user1':user1, 'user2':user2}))
    
    async def disconnect(self, close_code):
        username = self.scope["user"].username
        if await self.get_curr_lobby():
            await self.channel_layer.group_send(
                self.lobby_group_name, {"type": "new_member_message", "action": "left_member", "username": username}
            )
        
        await self.disconnect_db()


        # Leave room group
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)
    
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     action = text_data_json["action"]

    #     if action == "chat_update":
    #         text = text_data_json["text"]
            
    #         curr_lobby = await self.get_curr_lobby()
    #         curr_lobby.message_history += text
    #         return_text = curr_lobby.message_history
            
    #         await self.channel_layer.group_send(
    #             self.lobby_group_name, {"type": "chat_update_message", "text": return_text, 'action': action}
    #         )

    # Receive message from lobby group