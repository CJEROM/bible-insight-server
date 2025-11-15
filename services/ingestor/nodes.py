from bs4 import BeautifulSoup

# Will be created from books class
class Nodes:
    def __init__(self, book_xml, book_map_id):
        self.book_xml = BeautifulSoup(book_xml, "xml")
        self.book_map_id = book_map_id
        pass

    def walk_parsed_xml(self):
        pass

if __name__ == "__main__":
    pass