from transitions.extensions import GraphMachine
from transitions.core import MachineError
from crawl import Crawl
from utils import send_text_message



class TocMachine(GraphMachine):
    def __init__(self):
        self.user = Crawl()
        self.machine = GraphMachine(
            model=self, 
            states=["home", "hot_boards", "board", "article"],
            transitions=[
                {
                    "trigger": "board_name",
                    "source": ["home", "hot_boards"],
                    "dest": "board",
                    "before": "go_board_by_board_name"
                },
                {
                    "trigger": "hot",
                    "source": "home",
                    "dest": "hot_boards",
                    "before": "go_hot_boards"
                },
                {
                    "trigger": "next",
                    "source": "hot_boards",
                    "dest": "hot_boards",
                    "before": "go_next_hot_page"
                },
                {
                    "trigger": "prev",
                    "source": "hot_boards",
                    "dest": "hot_boards",
                    "before": "go_prev_hot_page"
                },
                {
                    "trigger": "index",
                    "source": "hot_boards",
                    "dest": "board",
                    "before": "go_board_by_index_from_hot",
                },
                {
                    "trigger": "prev",
                    "source": "board",
                    "dest": "board",
                    "before": "go_prev_page_articles_list"
                },
                {
                    "trigger": "next",
                    "source": "board",
                    "dest": "board",
                    "before": "go_next_page_articles_list",
                },
                {
                    "trigger": "index",
                    "source": "board",
                    "dest": "article",
                    "before": "go_article",
                },
                {
                    "trigger": "back",
                    "source": "article",
                    "dest": "board",
                    "before": "leave_article"
                },
                {
                    "trigger": "back",
                    "source": ["board", "hot_boards"],
                    "dest": "home",
                },
                {
                    "trigger": "exit",
                    "source": ["board", "hot_boards"],
                    "dest": "home",
                },
                {
                    "trigger": "home",
                    "source": "*",
                    "dest": "home",
                },
            ],
            initial="home",
            auto_transitions=False,
        )

    def reply_message(self, event, msg):
        reply_token = event.reply_token
        send_text_message(reply_token, msg)
        return

    def on_enter_home(self, event):
        MSG = """Welcome to Litt
enter 'hot' to get the hot boards list
enter go <board name> to get in the specific board
        """
        self.reply_message(event, MSG)
        return
    
    def go_hot_boards(self, event):
        res = self.user.get_next_hot_page(refresh=True)
        self.reply_message(event, res)
        return
    
    def go_next_hot_page(self, event):
        res = self.user.get_next_hot_page()
        self.reply_message(event, res)
        return
    
    def go_prev_hot_page(self, event):
        res = self.user.get_prev_hot_page()
        self.reply_message(event, res)
        return
    
    def go_board_by_index_from_hot(self, event):
        res = self.user.go_board_from_hot(int(event.message.text))
        self.reply_message(event, res)
        return
    
    def go_next_page_articles_list(self, event):
        res = self.user.go_next_page_articles_list()
        self.reply_message(event, res)
        return
    
    def go_prev_page_articles_list(self, event):
        res = self.user.go_prev_page_articles_list()
        self.reply_message(event, res)
        return
    
    def go_article(self, event):
        res = self.user.go_article(int(event.message.text))
        self.reply_message(event, res)
        return

    def leave_article(self, event):
        res = self.user.leave_article()
        self.reply_message(event, res)
        return

    def go_board_by_board_name(self, event):
        tem = event.message.text.split()
        if tem[0] == "go":
            res = self.user.go_board_by_board_name(tem[1])
        else:
            raise Exception(f"There is no command {tem[0]}")
        self.reply_message(event, res)
        return
    


    def parse_event(self, event):
        text = event.message.text
        try:
            res = self.trigger(text, event)
        except MachineError as exc:
            self.reply_message(event, f"command '{text}' is unavailable here.")
        except AttributeError as exc:
            print(exc) ##
            if text.isdigit():
                try:
                    self.index(event)
                except Exception as fexc:
                    self.reply_message(event, str(fexc))
            elif self.state == "home" or self.state == "hot_boards":
                try:
                    self.board_name(event)
                except Exception as fexc:
                    self.reply_message(event, str(fexc))
                    raise fexc
        except Exception as exc:
            self.reply_message(event, str(exc))

        print(f"current state: {self.state}")
        return

