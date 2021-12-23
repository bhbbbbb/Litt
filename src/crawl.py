import requests
from bs4 import BeautifulSoup as BS


class Crawl:
    def __init__(self):
        self._data_dict = {}
        self._hot_page = 0
        self._href_list = []
        self._next_href = None
        self._prev_href = None
        self._cur_href = None
        return


    # https://www.ptt.cc/bbs/Gossiping/M.1640052429.A.12C.html
    BASE = "https://www.ptt.cc"
    HOT = "https://www.ptt.cc/bbs/index.html"

    def _crawl(self, url, use_cache=True):
        """crawl content from url

        Args:
            url (string): url to crawl
            use_cache (bool, optional): [description]. Defaults to True.

        Returns:
            TODO: [description]
        """
        if use_cache:
            content = self._data_dict.get(url)
            if content != None:
                return content
        req = requests.get(url, cookies={ "over18": "1" })
        if req.status_code != 200:
            raise Exception(str(req.status_code))
        content = BS(req.text, "lxml")
        if use_cache:
            self._data_dict[url] = content
        return content

    def get_next_hot_page(self, refresh=False) -> str:
        """get next page of hot boards on ptt

        Args:
            refresh (bool, optional)

        Returns:
            str: return None if there is no next page. Otherwise return board list for current
            page.
        """
        if refresh: self._hot_page = 0
        content = self._crawl(self.HOT, use_cache=(not refresh))
        all_a = content.find_all("a", class_="board")

        # 20 boards per page
        full_list = ""
        start_pos = self._hot_page * 20  

        if start_pos >= len(all_a): raise Exception("There is no next page!")

        if start_pos + 20 >= len(all_a): end_pos = len(all_a)
        else: end_pos = start_pos + 20

        href_list = []
        for idx in range(start_pos, end_pos):
            href_list.append(self.BASE + all_a[idx]["href"])
            children = all_a[idx].find_all("div")
            full_list = full_list + f"{idx - start_pos + 1:2}." + " "
            full_list = full_list + f"{children[0].text:12}" + " " # boardname
            full_list = full_list + f"{children[1].text:5}" + " " # nuser
            full_list = full_list + children[2].text + " " # class
            full_list = full_list + children[3].text # title
            full_list = full_list + "\n"

        self._hot_page = self._hot_page + 1
        self._href_list = href_list
        return full_list

    def get_prev_hot_page(self, refresh=False) -> str:
        self._hot_page = self._hot_page - 2
        if self._hot_page < 0: raise Exception("There is no previous page!")
        return self.get_next_hot_page(refresh=refresh)
    

    def _parse_board(self, url):
        """parse article list in specific board

        Args:
            url (str): url

        Returns:
            (str): full_title
        """
        content = self._crawl(url, use_cache=False)
        page_btns = content.find("div", class_="btn-group-paging")
        page_btns = page_btns.find_all("a")

        self._cur_href = url

        next = page_btns[1].get("href")
        if next != None: self._next_href = self.BASE + next
        else: self._next_href = None

        prev = page_btns[2].get("href")
        if prev != None: self._prev_href = self.BASE + prev
        else: self._prev_href = None

        articles = content.find_all("div", class_="r-ent")
        full_title = ""
        href_list = []
        idx = 0
        for article in articles:
            # title
            title = article.find("div", class_="title").a
            if title == None: continue

            full_title = full_title + f"{idx + 1:2}.  "

            # nrec
            nrec = article.find("div", class_="nrec").text
            if nrec.isdigit():
                full_title = full_title + f"{int(nrec):2} "
            elif len(nrec) == 0:
                full_title = full_title + "   "
            else: # nrec = wide char "bao" (>99)
                full_title = full_title + nrec + " "
            
            href_list.append(self.BASE + title["href"])
            full_title = full_title + title.text + "\n"
            idx = idx + 1
        self._href_list = href_list
        return full_title

    def _parse_article(self, url) -> str:
        content = self._crawl(url, use_cache=False)
        full_article = ""
        main = content.find("div", id="main-content")

        meta = main.find_all("div")

        [tem_a, tem_b] = meta[0].find_all("span") # author, <author-value>
        full_article = full_article + tem_a.text + " " + tem_b.text + "\n"

        [tem_a, tem_b] = meta[2].find_all("span") # title, <title-value>
        full_article = full_article + tem_a.text + " " + tem_b.text + "\n"

        [tem_a, tem_b] = meta[3].find_all("span") # time, <time-value>
        full_article = full_article + tem_a.text + " " + tem_b.text + "\n"

        for idx in range(4):
            meta[idx].extract()
        
        full_article = full_article + main.text
        self._prev_href = self._cur_href
        self._cur_href = url
        self._next_href = None
        return full_article

    def go_board_from_hot(self, selected_idx) -> str:
        """go to board from the hot board list

        Args:
            selected_idx (int): note that this index is start from 1
        
        Raises:
            Exception: If selected_idx is out of range.

        Returns:
            str: article list in specific board
        """
        selected_idx = selected_idx - 1
        if selected_idx >= len(self._href_list) or selected_idx < 0:
            raise Exception(f"Invalid index {selected_idx + 1}")
        
        dest = self._parse_board(self._href_list[selected_idx])
        return dest
    
    def go_board_by_board_name(self, name) -> str:
        url = self.BASE + "/bbs/" + name + "/index.html"
        print(url)
        try:
            dest = self._parse_board(url)
        except Exception as exc:
            print("183: ", exc)
            if str(exc) == "404":
                raise Exception(f"board name '{name}' does not exist") from exc
            else:
                raise exc

        return dest
        
    def go_next_page_articles_list(self):
        return self._parse_board(self._next_href)
    
    def go_prev_page_articles_list(self):
        return self._parse_board(self._prev_href)

    def go_article(self, selected_idx) -> str:
        """go to article's content

        Args:
            selected_idx (int): note that this index is start from 1

        Returns:
            str: specific parsed article
        """
        selected_idx = selected_idx - 1
        if selected_idx >= len(self._href_list) or selected_idx < 0:
            raise Exception(f"Invalid index {selected_idx + 1}")
        
        dest = self._parse_article(self._href_list[selected_idx])
        return dest
    
    def leave_article(self) -> str:
        return self._parse_board(self._prev_href)
    




if __name__ == "__main__":
    user = Crawl()