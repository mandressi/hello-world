'''
Tic Tac Toe game program
Use classes to build the board, board state, strategies
Use the Tkinter for the GUI
Last revised 2019/12/24 by D.R.R.
'''

from tkinter import *  # tkinter : version 3.*
import random, re


#a_list = [1,2,3,4,5,6,7,8,9]




# Constants
GridSize = 200 # size in pixels of each square on playing board
PieceSize = GridSize - 8 # size in pixels of each playing piece
Offset = 2 # offset in pixels of board from edge of canvas
BoardColor = '#D3D3D3'#'#2B2BFF' #color of board - medium blue
HiliteColor = '#ffD3D3' #5555FF' #color of highlighted square - light blue
PlayerColors = ('', '#000000', '#ffffff')#('', '#000000', '#ffffff') # rgb values for black, white
PlayerNames = ('', 'Black', 'White') # Names of players as displayed to the user
Compass = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
	  # eight compass directions as (dx, dy)
MoveDelay = 1000 # pause 1000 msec (1 sec) between moves
# Equivalent to enum in C: for symbolic notation
class Player:
    black = 1
    white = 2


class BoardState:
    '''Holds one state of the board.
       getPlayer() and getPieces() return information about the state.
       getMoves() computes legal moves that can be made from this state.
    '''
    def __init__(self, boardstate=None):
        "Creates a new board state.  If a board state is supplied, it is copied"
        if boardstate:
            # copy an existing board state
            self._pieces = boardstate._pieces.copy()
            self._open = boardstate._open.copy()
            self._player = boardstate._player
            self._passed = boardstate._passed
        else:
            # create a new board state
            # Note: x goes from 0 to 2, y goes from 0 to 2
            # _pieces is a list of pieces on the board; _pieces[x,y] = player no: 1 or 2
            # this is the opening state of the board
            self._pieces = {}
            # _open is a list of open spaces next to occupied spaces
            # it is used to narrow the search space for legal moves
            # _open[x,y] = 1 means space is open
            self._open = {(0,0):1,(0,1):1,(0,2):1,
                                   (1,0):1,(1,1):1,(1,2):1,
                                   (2,0):1,(2,1):1,(2,2):1}
            self._player = random.choice([Player.black,Player.white]) #  choose randomly player at start
            self._passed = 0 # indicates if last player passed (for determing game over)
    def getPlayer(self):
        "Returns player whose turn it is"
        return self._player
    def getPieces(self):
        "Returns current pieces on board as dictionary: pieces[x,y] = player"
        return self._pieces
    def getMoves(self):
        '''Returns a list of valid next moves and board states.
           Each item is (x,y,newBoardState). x,y in range 0-2.
           If there is no legal move (game over), the list will be empty.
        '''
        result = []
        # examine open spaces for legal moves
        for x,y in self._open.keys():
            boardState = self._placePiece(x, y)
            if boardState: result.append((x,y,boardState))
        #print "result after examining legal move:",result
        return result
        # remove new piece from open space list
        del newboard._open[x,y] # <--- when is this line executed ??????
        # add new open spaces surrounding piece
    def _placePiece(self, x, y):
        # Place a piece at given location.  Returns new BoardState.
        newboard = self._getNewBoard(x, y)
        player = self._player
        # check each square if open               
        newboard._pieces[x,y]=player
        return newboard
    def _getNewBoard(self, x, y):
        # Builds a new board from current one and updates pieces and open spaces
        # copy current board state
        newboard = BoardState(self)
        # add new piece
        newboard._pieces[x,y] = self._player
        # remove new piece from open space list
        del newboard._open[x,y]
        # add new open spaces surrounding piece
        for dx,dy in Compass:
            tx = x + dx; ty = y + dy
            if not newboard._pieces.get((tx, ty)):
                # space is open, add it to open list (unless it's off the edge!)
                if tx >= 0 and tx <= 2 and ty >= 0 and ty <= 2:
                    newboard._open[tx, ty] = 1
        # make it the other player's turn
        newboard._changePlayers()
        return newboard
    def _changePlayers(self):
        # Changes to the other player's turn
        if self._player == Player.black: self._player = Player.white
        else:                 self._player = Player.black

    
    def isWinner(self,pieces):
        x=pieces
        result=False
        for i in range(3):
            try:
                if (x[i,0]==x[i,1] and x[i,1]==x[i,2]):
                    result=True
            except:
                pass
        for j in range(3):
            try:
                if (x[0,j]==x[1,j] and x[1,j]==x[2,j]):
                    result=True
            except:
                pass
        try:
            if (x[0,0]==x[1,1] and x[1,1]==x[2,2]):
                result=True
        except:
            pass
        try:
            if (x[0,2]==x[1,1] and x[1,1]==x[2,0]):
                result=True
        except:
            pass
        print ("test winning:", result)
        return result


class Board:
    "Holds the Tk GUI and the current board state"
    class Square:
        "Holds data related to a square of the board"
        def __init__(self, x, y):
            self.x, self.y = x, y # location of square (in range 0-2)
            self.player = 0 # number of player occupying square
            self.squareId = 0 # canvas id of rectangle
            self.pieceId = 0 # canvas id of circle

    def __init__(self, strategies=()):
        '''Initialize the interactive game board.  An optional list of
           computer opponent strategies can be supplied which will be
           displayed in a menu to the user.
        '''
        # create a Tk frame to hold the gui
        self._frame = Frame()
        # set the window title
        self._frame.master.wm_title('Tic Tac Toe')
        # build the board on a Tk drawing canvas
        size = 3*GridSize # make room for 3x3 squares
        self._canvas = Canvas(self._frame, width=size, height=size)
        self._canvas.pack()
        # add button for starting game
        self._menuFrame = Frame(self._frame)
        self._menuFrame.pack(expand=Y, fill=X)
        self._newGameButton = Button(self._menuFrame, text='New Game', command=self._newGame)
        self._newGameButton.pack(side=LEFT, padx=5)
        Label(self._menuFrame).pack(side=LEFT, expand=Y, fill=X)
        # add menus for choosing player strategies
        self._strategies = {} # strategies, indexed by name
        optionMenuArgs = [self._menuFrame, 0, 'Human']
        for s in strategies:
            name = s.getName()
            optionMenuArgs.append(name)
            self._strategies[name] = s
        self._strategyVars = [0] # dummy entry so strategy indexes match player numbers
        # make a menu for each player
        for n in (1,2):
            label = Label(self._menuFrame, anchor=E, text='%s:' % PlayerNames[n])
            label.pack(side=LEFT, padx=10)
            var = StringVar(); var.set('Human')
            var.trace('w', self._strategyMenuCallback)
            self._strategyVars.append(var)
            optionMenuArgs[1] = var
            #menu = apply(OptionMenu, optionMenuArgs)
            print (optionMenuArgs)
            menu = OptionMenu(optionMenuArgs[0],optionMenuArgs[1],optionMenuArgs[2],optionMenuArgs[3],
                              optionMenuArgs[4],optionMenuArgs[5])#,optionMenuArgs[6]
            menu.pack(side=LEFT)
        # add a label for showing the status
        self._status = Label(self._frame, relief=SUNKEN, anchor=W)
        self._status.pack(expand=Y, fill=X)
        # map the frame in the main Tk window
        self._frame.pack()

        # track the board state
        self._squares = {} # Squares indexed by (x,y)
        self._enabledSpaces = () # list of valid moves as returned by BoardState.getmoves()
        for x in range(3):
            for y in range(3):
                square = self._squares[x,y] = Board.Square(x,y)
                x0 = x * GridSize + Offset
                y0 = y * GridSize + Offset
                square.squareId = self._canvas.create_rectangle(x0, y0,
                                                                x0+GridSize, y0+GridSize,
                                                                fill=BoardColor)

        # _afterId tracks the current 'after' proc so it can be cancelled if needed
        self._afterId = 0

        # ready to go - start a new game!
        self._newGame()

    def play(self):
        'Play the game! (this is the only public method)'
        self._frame.mainloop()

    def _postStatus(self, text):
        # updates the status line text
        self._status['text'] = text

    def _strategyMenuCallback(self, *args):
        # this is called when one of the player strategies is changed.
        # _updateBoard will keep everything in sync
        self._updateBoard()

    def _newGame(self):
        # delete existing pieces
        for s in self._squares.values():
            if s.pieceId:
                self._canvas.delete(s.pieceId)
                s.pieceId = 0
        # create a new board state and display it
        self._state = BoardState()
        self._updateBoard()

    def _updateBoard(self):
        # cancel 'after' proc, if any
        if self._afterId:
            self._frame.after_cancel(self._afterId)
            self._afterId = 0
        # reset any enabled spaces
        self._disableSpaces()
        
        # update canvas display to match current state
        for pos, player in self._state.getPieces().items():
            square = self._squares[pos]
            if square.pieceId:
                if square.player != player:
                    self._canvas.itemconfigure(square.pieceId, fill=PlayerColors[player])
            else:
                x,y = pos
                x0 = x * GridSize + Offset #
                y0 = y * GridSize + Offset #
                square.pieceId = self._canvas.create_oval(x0, y0,
                                                          x0 + PieceSize, y0 + PieceSize,
                                                          fill=PlayerColors[player])

        # prepare for next move, either human or ai
        player = self._state.getPlayer()
        moves = self._state.getMoves()
        # check for game over
        print ("----------------")
        #player = self._state.getPlayer()
        print ("pieces: ", self._state._pieces)
        print ("open: ", self._state._open)
        print ("Player:",PlayerNames[player])
        if self._state.isWinner(self._state._pieces):
            prev_player = 0
            if player == Player.black:
                prev_player = Player.white
            else:
                prev_player = Player.black
            end_text=PlayerNames[prev_player] + " won."
            self._gameOver(end_text)
            return
               
        print ("Check for moves ...")                
        if not moves:
            end_text="It's a tie."
            self._gameOver(end_text)
            return
        passedText = " * "
   
        # get strategy (if not human)
        ai = self._strategies.get(self._strategyVars[player].get())
        if ai:
            # ai: we have to schedule the ai to run
            self._postStatus(passedText + "%s (%s) is thinking" % \
                             (ai.getName(), PlayerNames[player]))
            self._afterId = self._frame.after_idle(self._processAi, ai, moves)
        else:
            # human: just enable legal moves and wait for a click
            print (PlayerNames[player] + "'s turn")
            self._postStatus(PlayerNames[player] + "'s turn")
            self._enabledSpaces = self._state.getMoves()
            #print "self._enabledSpaces=",self._enabledSpaces
            #input("Enter key")
            self._enableSpaces()

    def _processAi(self, ai, moves):
        # calls the strategy to determine next move
        if len(moves) == 1:
            # only one choice, don't both calling strategy
            self._state = moves[0][2]
        else:
            # call strategy
            x,y,boardstate = ai.getNextMove(self._state.getPlayer(), moves)
            self._state = boardstate
        self._afterId = self._frame.after(MoveDelay, self._updateBoard)



    def _enableSpaces(self):
        # make spaces active where a legal move is possible (only used for human players)
        for x,y,bs in self._enabledSpaces:
            if x == -1: break
            id = self._squares[x,y].squareId
            self._canvas.tag_bind(id, '<ButtonPress>',
                                  lambda e, s=self, x=x, y=y, bs=bs: s._selectSpace(bs))
            self._canvas.tag_bind(id, '<Enter>',
                                  lambda e, c=self._canvas, id=id: \
                                  c.itemconfigure(id, fill=HiliteColor))
            self._canvas.tag_bind(id, '<Leave>',
                                  lambda e, c=self._canvas, id=id: \
                                  c.itemconfigure(id, fill=BoardColor))

    def _disableSpaces(self):
        # remove event handlers for all enabled spaces
        for x,y,bs in self._enabledSpaces:
            if x == -1: break
            id = self._squares[x,y].squareId
            self._canvas.tag_unbind(id, '<ButtonPress>')
            self._canvas.tag_unbind(id, '<Enter>')
            self._canvas.tag_unbind(id, '<Leave>')
            self._canvas.itemconfigure(id, fill=BoardColor)
        self._enabledSpaces = ()

    def _selectSpace(self, bs):
        # this is called when a human clicks on a space to place a piece
        self._state = bs # the new board state was pre-computed, just use it
        self._updateBoard()
        
    def _gameOver(self,text=""):
        # the game is over.
        print ("Game Over." + text)
        self._postStatus('Game Over. '+text)

class Strategy:
    # This is a base class for implementing strategies
    def getName(self):
        "Returns the name of the strategy for displaying to the user."
        try:
            # return name if we have one
            return self._name
        except AttributeError:
            # determine name from class name
            classname = str(self.__class__) # get class name as 'module.class'
            m = re.search(r'\.(.+)$', classname) # strip module name from classname
            if m: self._name = m.group(1)
            else: self._name = 'AI'
            return self._name
    def getNextMove(self, player, moves):
        '''Determines next move from list of available moves.
           Derived classes must implement this.

           player is the current player.  moves is a list of valid
           moves where each item is (x,y,boardState).
           This routine must return one of the moves from moves.

           Note: if there is only one valid move (or no move in the case of a pass),
           this routine will not be called and the move will be made automatically.
        '''
        raise (Exception, "Invalid Strategy class, getNextMove not implemented")

class Random(Strategy):
    def __init__(self):
        self._name='ランダム'
    def getNextMove(self, player, moves):
        # just pick a move randomly
        print ("moves:", moves)
        move = moves[random.randint(0, len(moves)-1)]
        return move

class Ai1(Strategy):
    def __init__(self):
        self._name = 'ミニマックス法'
        self._squares = {}
        self._copySquares = {}
        self._winningCombos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],#horizontal win
        [0, 3, 6], [1, 4, 7], [2, 5, 8],#vertical win
        [0, 4, 8], [2, 4, 6])           #diagonal win
        # black is 'x', white is 'o'
    def createBoard(self) :
        for i in range(9) :
            # *** use a single character, ... easier to print
            self._squares[i] = "."
        print(self._squares)
    def showBoard(self) :
        # *** add empty line here, instead of in minimax
        print ()
        print(self._squares[0], self._squares[1], self._squares[2])
        print(self._squares[3], self._squares[4], self._squares[5])
        print(self._squares[6], self._squares[7], self._squares[8])
    def convert_BoardState_to_AI_state(self,boardstate):
        #[x,y]:player to position:player
        self.createBoard()
        current_pieces = boardstate.getPieces()
        num_pieces = len(list(current_pieces))
        #print("current_pieces:",current_pieces)
        i=0
        for each in current_pieces:
            i += 1
            #print("each:",each)
            y,x = each
            player=current_pieces[each]
            if player == Player.white: ai_player="o"
            else: ai_player="x"
            if x==0 and y ==0:
                self._squares[0]=ai_player
            elif x==0 and y==1:
                self._squares[1]=ai_player
            elif x==0 and y==2:
                self._squares[2]=ai_player
            elif x==1 and y==0:
                self._squares[3]=ai_player
            elif x==1 and y==1:
                self._squares[4]=ai_player
            elif x==1 and y==2:
                self._squares[5]=ai_player
            elif x==2 and y==0:
                self._squares[6]=ai_player
            elif x==2 and y==1:
                self._squares[7]=ai_player
            elif x==2 and y==2:
                self._squares[8]=ai_player
            if i >=num_pieces-1:
                break
        self.showBoard()
    def convert_AI_move_to_game_move(self,move,ai_player):
        #position to [x,y]:player
        #current_pieces = boardstate.getPieces()
        if ai_player == "o": player = Player.white
        else: player=Player.black
        for i in range(0,9):
            if move == 0:
                return (0,0),player
            elif move == 1:
                return (1,0),player
            elif move == 2:
                return (2,0),player
            elif move ==3:
                return (0,1),player
            elif move == 4:
                return (1,1),player
            elif move == 5:
                return (2,1),player
            elif move ==6:
                return (0,2),player
            elif move == 7:
                return (1,2),player
            elif move == 8:
                return (2,2),player
    def getAvailableMoves(self) :
        self._availableMoves = []
        for i in range(9) :
            # *** see above
            if self._squares[i] == "." :
                self._availableMoves.append(i)
        return self._availableMoves
    def makeMove(self, position, a_player) :
        self._squares[position] = a_player
        #self.showBoard()
    def complete(self) :
        # *** see above
        if "." not in self._squares.values() :
            return True
        if self.getWinner() != None :
            return True
        return False
    def getWinner(self) :
        for player in ("x", "o") :
            for combos in self._winningCombos :
                if self._squares[combos[0]] == player and self._squares[combos[1]] == player and self._squares[combos[2]] == player :
                    return player
        # *** see above
        if "." not in self._squares.values() :
            return "tie"
        return None
    def getEnemyPlayer(self, player) :
        if player == "x" :
            return "o"
        return "x"
    
    def getNextMove(self, player, moves):
        boardState = moves[0][2] # this is the state in the strategy only
        # convert the boardstate to AI_state
        current_pieces = boardState.getPieces()
        print("Pieces : ", current_pieces)
        bestMove = None
        print("AI Player:",PlayerNames[player])
        print("Number of posssible moves:",len(moves))
        # black is 'x', white is 'o'
        self.convert_BoardState_to_AI_state(boardState)
        if player == Player.white: ai_player="o"
        else: ai_player="x"
        val, AI_bestMove = self.minimax(ai_player)
        # convert AI bestMove to  Game bestMove
        # AI_bestMove is a number between [0..7]
        (x_ai,y_ai),a_player=self.convert_AI_move_to_game_move(AI_bestMove,ai_player)
        for move in moves:
            x,y,bs = move
            if x == x_ai and y == y_ai:
                bestMove = move
                break
        return bestMove
    def minimax(self, player, depth = 0) :
        if player == "o": 
            best = -10
        else:
            best = 10
        if self.complete() :
            if self.getWinner() == "x" :
                return -10 + depth, None
            elif self.getWinner() == "tie" :
                return 0, None
            elif self.getWinner() == "o" :
                # *** value should be closer to zero for greater depth!
                # *** expect tuple return value
                return 10 - depth, None
        for move in self.getAvailableMoves() :
            # *** don't increase depth in each iteration, instead pass depth+1 to
            #    the recursive call
            self.makeMove(move, player)
            # *** expect tuple return value
            val, _ = self.minimax(self.getEnemyPlayer(player), depth+1)
            #print(val)
            # *** undo last move
            self.makeMove(move, ".")
            if player == "o" :
                if val > best :
                    # *** Also keep track of the actual move
                    best, bestMove = val, move
            else :
                if val < best :
                    # *** Also keep track of the actual move
                    best, bestMove = val, move
        # *** Also keep track of the actual move
        return best, bestMove



class MyStrat2(Strategy):
    def __init__(self):
        self._name='負けない戦略'
    def getNextMove(self, player, moves):
        # just pick a move randomly
        bestMove = None
        print("AI Player:",PlayerNames[player])
        print("Number of posssible moves:",len(moves))
        if player == Player.white: opponent_player = Player.black
        else: opponent_player = Player.white
        print("Opponent Player:",PlayerNames[opponent_player])
        #place on the  middle or corner for the first or second move if available
        if len(moves)>6:
            for move in moves:
                x,y,bs=move
                if (x==0 and y==0):
                    bestMove = move
                elif (x==0 and y==2):
                    bestMove = move
                elif (x==2 and y==0):
                    bestMove = move
                elif (x==2 and y==2):
                    bestMove = move
                if (x==1 and y==1):
                    bestMove=move
                    break
        #check my move if winning move, then take that move
        if len(moves)<=6:
            for move in moves:
                x,y,bs=move
                my_pieces = {e: bs._pieces[e] for e in bs._pieces if bs._pieces[e]==player}
                my_pieces[x,y]=player 
                print ("ai pieces:",my_pieces)
                if bs.isWinner(my_pieces):
                    bestMove=move
                    break
        #check opponent move if winning move, then take that move
        if len(moves)<=6 and bestMove==None:
            for move in moves:
                x,y,bs=move
                opponent_pieces = {e: bs._pieces[e] for e in bs._pieces if bs._pieces[e]==opponent_player}
                opponent_pieces[x,y]=opponent_player 
                print ("Opponent pieces:",opponent_pieces)
                if bs.isWinner(opponent_pieces):
                    bestMove=move
                    break
        # check corner 
        if bestMove==None:
            for move in moves:
                x,y,bs = move
                if (x==0 and y==0):
                    bestMove = move
                elif (x==0 and y==2):
                    bestMove = move
                elif (x==2 and y==0):
                    bestMove = move
                elif (x==2 and y==2):
                    bestMove = move
        # otherwise take a random move
        if bestMove==None:
                bestMove = moves[random.randint(0, len(moves)-1)]
        return bestMove
    
    
if __name__ == '__main__':
    # create a new game board with the desired strategies
    strategies = (Random(),Ai1(),MyStrat2())#CornerFirst(),
    board = Board(strategies)
    board.play()
        
