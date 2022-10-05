import pygame
from enum import Enum

class GameMode(Enum):
    GM_SET = "Set a piece on the board"
    GM_DESTROY = "Destroy a enemy piece"
    GM_MOVE = "Move a piece"
    GM_VICTORY = "Victory"

class Piece:
    player = 0
    node = None
    collider = None

    def __init__(self,player_,node_):
        self.player = player_
        self.node = node_
    
    def set_node(self,node_):
        self.node = node_
    
    def delete_node(self):
        self.node = None
    
    def draw(self,surface):
        self.collider = pygame.draw.circle(surface,(255*(1-self.player),255*(1-self.player),255*(1-self.player)),(self.node.x,self.node.y),10)

class Node:
    piece = None
    x = 0
    y = 0
    connections = []
    collider = None

    def __init__(self,x_,y_):
        self.x = x_
        self.y = y_
        self.connections = []
    
    def set_piece(self,piece_):
        self.piece = piece_

    def delete_piece(self):
        self.piece = None

    def set_connections(self,*conns):
        for node in conns:
            if node!=self:
                self.connections.append(node)
                node.set_connection(self)

    def set_connection(self,conn):
        self.connections.append(conn)
    
    def get_position(self):
        return (self.x,self.y)

    def can_select_to_move(self):
        for node in self.connections:
            if node.piece is None:
                return True
        return False
    
    def can_move(self,node):
        if node in self.connections:
            return True
        return False

    def draw(self,surface):
        self.collider = pygame.draw.circle(surface,(125,125,125),(self.x,self.y),8)
        if self.piece is not None:
            self.piece.draw(surface)

class Board:
    layer = 0
    nodes = []
    lines = []
    first_node_position = (0,0)
    margin = 0
    length = 0
    next_board = None

    def __init__(self,layers,position,length_, margin_ = 50):
        self.nodes = []
        self.layer = layers
        self.first_node_position = (position[0]+margin_,position[1]+margin_)
        self.margin = margin_
        self.length = (length_ - 2*margin_)/2
        self.next_board = None if layers - 1 == 0 else Board(layers-1,(self.first_node_position),2*self.length,length_*1.5/10)
        return

    def __str__(self):
        return "This board is the layer " + str(self.layer)

    def remove_line(self,node):
        for line in self.lines:
            if node in line:
                self.lines.remove(line)

    def check_line(self,*nodes):
        for node in nodes:
            if node.piece is None:
                return False
        player = nodes[0].piece.player
        for node in nodes:
            if node.piece.player != player:
                return False

        for line in self.lines:
            if line[0] == nodes[0] and line[1] == nodes[1] and line[2] == nodes[2]:
                return False
        self.lines.append([nodes[0],nodes[1],nodes[2]])
        return True

    def check_in(self):
        in_pos = [1,3,4,6]
        for n in in_pos:
            if self.check_line(self.nodes[n],self.next_board.nodes[n],self.next_board.next_board.nodes[n]):
                return True

    def check_out(self):
        return self.check_line(self.nodes[0],self.nodes[1],self.nodes[2]) or self.check_line(self.nodes[0],self.nodes[3],self.nodes[5]) or self.check_line(self.nodes[2],self.nodes[4],self.nodes[7]) or self.check_line(self.nodes[5],self.nodes[6],self.nodes[7])

    def draw(self,surface):
        for node in self.nodes:
            for connection in node.connections:
                pygame.draw.line(surface,(100,100,100),node.get_position(),connection.get_position())
        if self.next_board is not None:
            self.next_board.draw(surface)
        for node in self.nodes:
            node.draw(surface)

    def check_can_move(self,player):
        pieces = []
        for node in self.nodes:
            if node.piece is not None:
                if node.piece.player is player:
                    pieces.append(node)
        for node in self.next_board.nodes:
            if node.piece is not None:
                if node.piece.player is player:
                    pieces.append(node)
        for node in self.next_board.next_board.nodes:
            if node.piece is not None:
                if node.piece.player is player:
                    pieces.append(node)
    
        return any(node.can_select_to_move() for node in pieces)

    @staticmethod
    def create_nodes(board):
        board.nodes.append(Node(board.first_node_position[0],board.first_node_position[1]))
        board.nodes.append(Node(board.first_node_position[0]+board.length,board.first_node_position[1]))
        board.nodes.append(Node(board.first_node_position[0]+(2*board.length),board.first_node_position[1]))
        board.nodes.append(Node(board.first_node_position[0],board.first_node_position[1]+board.length))
        board.nodes.append(Node(board.first_node_position[0]+(2*board.length),board.first_node_position[1]+board.length))
        board.nodes.append(Node(board.first_node_position[0],board.first_node_position[1]+(2*board.length)))
        board.nodes.append(Node(board.first_node_position[0]+board.length,board.first_node_position[1]+(2*board.length)))
        board.nodes.append(Node(board.first_node_position[0]+(2*board.length),board.first_node_position[1]+(2*board.length)))
        if board.next_board is not None:
            Board.create_nodes(board.next_board)

    @staticmethod
    def create_connections(board):
        nodes = board.nodes
        board.nodes[0].set_connections(nodes[1],nodes[3])
        board.nodes[1].set_connections(nodes[2])
        board.nodes[2].set_connections(nodes[4])
        board.nodes[3].set_connections(nodes[5])
        board.nodes[4].set_connections(nodes[7])
        board.nodes[5].set_connections(nodes[6])
        board.nodes[6].set_connections(nodes[7])
        if board.next_board is not None:
            board.nodes[1].set_connections(board.next_board.nodes[1])
            board.nodes[3].set_connections(board.next_board.nodes[3])
            board.nodes[4].set_connections(board.next_board.nodes[4])
            board.nodes[6].set_connections(board.next_board.nodes[6])
            Board.create_connections(board.next_board)


class Game:
    size_window = 0
    initial_pieces = 0
    pieces = [0,0]
    game_pieces = [0,0]
    bRun = True
    actual_player = 0
    game_mode = GameMode.GM_SET
    actual_piece = None

    def __init__(self, size, initial):
        self.size_window = size
        self.initial_pieces = initial
        self.pieces = [initial,initial]
        self.game_pieces = [initial,initial]
        return
    
    def check_lines(self,board):
        return board.check_out() or board.next_board.check_out() or board.next_board.next_board.check_out() or board.check_in()

    def set(self,board):
        for node in board.nodes:
            if node.collider.collidepoint(pygame.mouse.get_pos()):
                if node.piece is None:
                    node.piece = Piece(self.actual_player,node)
                    self.pieces[self.actual_player] -= 1
                    self.actual_player = 0 if self.actual_player == 1 else 1
                    if self.pieces[0] == 0 and self.pieces[1] == 0:
                        self.game_mode = GameMode.GM_MOVE
        if board.next_board is not None:
            self.set(board.next_board)

    def destroy(self,board):
        for node in board.nodes:
            if node.piece is not None:
                if node.piece.collider.collidepoint(pygame.mouse.get_pos()):
                    if node.piece.player == self.actual_player:
                        node.piece.delete_node()
                        node.delete_piece()
                        self.game_pieces[self.actual_player] -= 1
                        self.game_mode = GameMode.GM_MOVE if self.pieces == [0,0] else GameMode.GM_SET
                        if self.game_pieces[0] == 2 or self.game_pieces[1] == 2:
                            self.victory(1-self.actual_player)
        if board.next_board is not None:
            self.destroy(board.next_board)

    def move(self,board):
        for node in board.nodes:
            if node.piece is not None:
                if node.piece.collider is not None:
                    if node.piece.collider.collidepoint(pygame.mouse.get_pos()):
                        if self.actual_player == node.piece.player:
                            if node.can_select_to_move():
                                self.actual_piece = node.piece
            else:
                if self.actual_piece is not None:
                    if node.collider.collidepoint(pygame.mouse.get_pos()):
                        if not self.actual_piece.node.can_move(node):
                            return
                        board.remove_line(self.actual_piece.node)
                        self.actual_piece.node.delete_piece()
                        self.actual_piece.delete_node()
                        self.actual_piece.node = node
                        node.piece = self.actual_piece
                        self.actual_piece = None
                        self.actual_player = 0 if self.actual_player == 1 else 1
        if board.next_board is not None:
            self.move(board.next_board)


    def victory(self, winner):
        self.game_mode = GameMode.GM_VICTORY
        pygame.display.set_caption("Nine Men Morris - {} - The Winner is {}".format(str(self.game_mode.value),"White" if winner == 0 else "Black"))
        return

    def run(self):
        board = Board(3,(0,0),self.size_window)
        Board.create_nodes(board)
        Board.create_connections(board)
        pygame.init()
        screen = pygame.display.set_mode((self.size_window, self.size_window))
        while self.bRun:            
            screen.fill((150,150,150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if self.game_mode is not GameMode.GM_VICTORY:
                    turn = ("White" if self.actual_player == 0 else "Black") if self.game_mode is not GameMode.GM_DESTROY else ("Black" if self.actual_player == 0 else "White")
                    pygame.display.set_caption("Nine Men Morris - {} - Turn of {}".format(str(self.game_mode.value),turn))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.game_mode == GameMode.GM_SET:
                            self.set(board)
                        if self.game_mode == GameMode.GM_DESTROY:
                            self.destroy(board)
                        if self.game_mode == GameMode.GM_MOVE:
                            self.move(board)
                            if not board.check_can_move(self.actual_player):
                                self.victory(1-self.actual_player)
            self.game_mode = GameMode.GM_DESTROY if self.check_lines(board) else self.game_mode
            board.draw(screen)
            pygame.display.flip()

def main():
    game = Game(700,9)
    game.run()

if __name__ == "__main__":
    main()
