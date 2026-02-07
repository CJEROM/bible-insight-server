from bs4 import BeautifulSoup, Tag, NavigableString

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ingestor.usx.book import Book
    from manager.logmanager import LogManager

# Will be created from books class
class Nodes:
    def __init__(self, this_book: "Book", log: "LogManager"):
        self.this_book          = this_book
        self.metadata           = this_book.metadata

        # Adds a database connection
        self.log                = log
        self.manager            = self.log.get_manager_handler()
        self.db                 = self.manager.get_db()

        # Initialise variables 
        self.book_soup          = self.this_book.usx
        self.book_map_id        = self.this_book.book_map_id
        self.book_style_file_id = self.metadata.styles
        self.translation_id     = self.metadata.translation_id

        self.created_nodes = {
            "chapter": {},
            "verse": {},
            "para": {},
            "note": {}
        }
        
        self.walk_parsed_xml()
            
        self.db.commit()
    
    def walk_parsed_xml(self):
        node_id_map = {}    # maps bs4 node → SQL node_id
        child_index = {}    # parent → next child index
        path_map = {}       # bs4 node → canonical path

        all_new_nodes = []

        node_id_offset = self.metadata.read.get_node_count()

        node_id_counter = 1

        node_chapter_ref = self.this_book.book_code + " 1"

        for node in self.book_soup.descendants:
            # Initialise node_id for the note we are going to create in DB
            node_id = node_id_counter + node_id_offset # since i will be 0, want to start at 1 instead + offset from database to say this new node is
            node_type = None
            
            this_node = [None] * 20 # create mutable list of length 17

            if isinstance(node, Tag):
                node_type =     node.name

                this_node[1] =  node_type # node_type, 1
                this_node[2] =  node.get("code") # code, 2
                sid =           node.get("sid")
                this_node[3] =  sid # sid, 3
                eid =           node.get("eid")
                this_node[4] =  eid # eid, 4
                this_node[5] =  node.get("vid") # vid, 5
                this_node[6] =  node.get("style") # style, 6 
                this_node[7] =  node.get("number") # number, 7
                this_node[8] =  node.get("caller") # caller, 8
                this_node[9] =  node.get("closed") # closed, 9
                this_node[10] = node.get("version") # version, 10
                strong =        node.get("strong")
                this_node[11] = strong # strong, 11
                this_node[12] = node.get("loc") # loc, 12
                this_node[17] = node.get("align") # align, 17 

            if isinstance(node, NavigableString):  
                node_type = "text"

                this_node[0] = str(node) # node_text, 0
                this_node[1] = node_type # node_type, 1

                for node_parent in node.parents:
                    if node_parent.name == "note":
                        break # if text_node inside a note node, then skip, never tokenisable
                    elif node_parent.name == "para":
                        # if inside a para node
                        parent_style = node_parent.get("style")

                        this_node[19] = self.metadata.read.is_paragraph_versetext( # is_tokenisable, 19
                            style=parent_style,
                            style_file_id=self.book_style_file_id
                        )
                        break

            # ------ Skip empty nodes
            if all(x is None for x in this_node) and node_type != "table":
                continue

            # ------ Parent & child index tracking
            node_id_map[id(node)] = node_id # add to node_map

            # With mapped id, find parent and get associated node_id
            parent_obj = node.parent
            parent_node_id = None
            index_in_parent = None

            # if has a parent (only xml and usx will not)
            if parent_obj:
                # get node_id map for parsed xml
                parent_node_id = node_id_map.get(id(parent_obj))

                # also increment and set count for child index under that parent
                if id(parent_obj) not in child_index:
                    child_index[id(parent_obj)] = 0
                index_in_parent = child_index[id(parent_obj)]
                child_index[id(parent_obj)] += 1
            else:
                index_in_parent = None

            # ------ Build Canonical Path
            parent_path = path_map.get(id(parent_obj), "") # if not exists, gives empty string

            new_path = f"/{node_type}:{index_in_parent}" 
            canonical_path = parent_path + new_path
            path_map[id(node)] = canonical_path

            # Update the rest of the node parts that required more processing
            this_node[13] = parent_node_id          # parent_node_id, 13
            this_node[14] = index_in_parent         # index_in_parent, 14
            this_node[15] = self.book_map_id        # book_map_id, 15
            this_node[16] = canonical_path          # canonical_path, 16 
            this_node[18] = self.translation_id     # translation_id, 18

            # Prepare for next node, and add for bulk insert
            all_new_nodes.append(tuple(this_node))
            node_id_counter += 1

            self.log.log_to_file(f"Created New Node: {this_node}", f"NODE:{node_type}", "TRACE")

            # Add to dictionary to show start and end nodes for chapters or verse
            if node_type in ["chapter", "verse"]:
                if sid != None:
                    self.created_nodes[node_type][sid] = {}
                    self.created_nodes[node_type][sid]["sid"] = node_id
                    if node_type == "chapter":
                        node_chapter_ref = sid
                elif eid != None:
                    self.created_nodes[node_type][eid]["eid"] = node_id
            # Add to dictionary to show node_id for para or note
            elif node_type in ["para", "note"]:
                # Check if need to inialise for chapter
                if self.created_nodes[node_type] == {}:
                    self.created_nodes[node_type][node_chapter_ref] = []
                elif self.created_nodes[node_type].get(node_chapter_ref) == None:
                    self.created_nodes[node_type][node_chapter_ref] = []

                self.created_nodes[node_type][node_chapter_ref].append(node_id)

        # Now bulk insert all of the nodes into the database (in batches / chunks)
        self.metadata.write.persist_nodes(all_new_nodes)

    def get_chapters(self):
        nodes = self.created_nodes["chapter"]
        self.log.log_to_file(f"Requested Chapter Nodes: {nodes}", f"NODE", "DEBUG")
        return nodes
    
    def get_paras(self):
        nodes = self.created_nodes["para"]
        self.log.log_to_file(f"Requested Para Nodes: {nodes}", f"NODE", "DEBUG")
        return nodes
    
    def get_verses(self):
        nodes = self.created_nodes["verse"]
        self.log.log_to_file(f"Requested Verse Nodes: {nodes}", f"NODE", "DEBUG")
        return nodes
    
    def get_notes(self):
        nodes = self.created_nodes["note"]
        self.log.log_to_file(f"Requested Note Nodes: {nodes}", f"NODE", "DEBUG")
        return nodes

# if __name__ == "__main__":
#     test_book_xml = None
#     # test_book_path = Path(__file__).parents[2] / "downloads" / "1CH - WMBBE.usx"
#     # test_book_path = Path(__file__).parents[2] / "downloads" / "PSA - WMBBE.usx"
#     test_book_path = Path(__file__).parents[2] / "downloads" / "3JN - FBV.usx"
#     with open(test_book_path, "r", encoding="utf-8") as f:
#         test_book_xml = f.read()

#     db_config = EnvManager().get_postgres_config()

#     # Adds a database connection
#     conn = psycopg2.connect(
#         host=db_config["host"],
#         port=db_config["port"],
#         dbname=db_config["database"],
#         user=db_config["username"],
#         password=db_config["password"]
#     )

#     new_nodes = Nodes(None, conn, test_book_xml)
#     print(new_nodes.get_chapters()["3JN"])