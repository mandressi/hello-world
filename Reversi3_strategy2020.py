# Reversi.py - (c) 2001 Brent Burley
# Permission granted for any use.  No warranty.  Enough said.
# Changed by D. R. R. in 2007
from tkinter import *
import random, re
'''
国際ルールに基づいて、プレイする。
オセロのゲームは石をはさんで返す。
最後の時、石の多いのプレイヤーが勝つ。
左上はa1、右上はh1、左下はa8、右下はh8と表記される。
列は[a,b,c,d,e,f,g,h]、は行[1,2,3,4,5,6,7,8]となる。
行列の要素はそれぞれの行と列の組み合わせです。
最初は二つの黒石(d5,e4)と白石(d4,c5)が間中に設置
黒石のプレイヤーが先手です。
黒石の可能な手はmoves=[c4,d3,e6,f5]
ハイライトされている四角の薄い緑色は可能な手です。
'''

# Constants
#プレイするボードの各ますの大きさ
GridSize = 50 # size in pixels of each square on playing board
#各遊ぶ石のピクセル中のサイズ
PieceSize = GridSize - 8 # size in pixels of each playing piece
#キャンバスの端からのボードのピクセル中のオフセット
Offset = 2 # offset in pixels of board from edge of canvas
#ボードの色はmedium green
BoardColor = '#008000' # color of board - medium green
#ハイライトされている四角の色はlight green
HiliteColor = '#00a000' # color of highlighted square - light green
dark_grey =  '#292929'
#プレイヤーの色はblackとwhite
PlayerColors = ('', '#000000', '#ffffff') # rgb values for black, white
#プレイヤーの表示される名前
PlayerNames = ('', '黒(くろ)', '白(しろ)') # Names of players as displayed to the user
#(dx、dy)としての8つのコンパス方位
Compass = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
	  # eight compass directions as (dx, dy)
#動くのに1秒待つ
MoveDelay = 1000 # pause 1000 msec (1 sec) between moves

class BoardState:
    '''Holds one state of the board.
       getPlayer() and getPieces() return information about the state.
       getMoves() computes legal moves that can be made from this state.
    '''
    def __init__(self, boardstate=None):
        "Creates a new board state.  If a board state is supplied, it is copied"
        if boardstate:
            #存在するボード状態をコピーする
            # copy an existing board state
            self._pieces = boardstate._pieces.copy()
            self._open = boardstate._open.copy()
            self._player = boardstate._player
            self._passed = boardstate._passed
        else:
            #新しいボードステートを作製
            #ノート:xは0から7まで、yも0から7まで動く
            #リストの中の「_pieces」はボードの上の石;_pieces[x,y]=プレイヤーの番号:1か2
            #これは開始状態である-ボードの中心の各プレーヤーにつき2個
            # create a new board state
            # Note: x goes from 0 to 7, y goes from 0 to 7
            # _pieces is a list of pieces on the board; _pieces[x,y] = player no: 1 or 2
            # this is the opening state - 2 pieces for each player in center of board
            self._pieces = {(3,3):2,(3,4):1,(4,3):1,(4,4):2}
            #「_open」は使用されているスペースの空きスペースです。
            #正しい動きのための探索スペースを狭めるために使用される
            #「_open[x,y] = 1」はそのスペースが空いていることを意味する。
            # _open is a list of open spaces next to occupied spaces
            # it is used to narrow the search space for legal moves
            # _open[x,y] = 1 means space is open
            self._open = {(2,2):1,(2,3):1,(2,4):1,(2,5):1,
                          (3,2):1,                (3,5):1,
                          (4,2):1,                (4,5):1,
                          (5,2):1,(5,3):1,(5,4):1,(5,5):1}
            # 常に黒からスタート
            self._player = 1 # black always starts first
            #Pythonの表では黒はmoves=[(2,3),(3,2),(4,5),(5,4)]の中か一つを選ぶ
            # 最後のプレイヤーが通過したかどうかを示す（ゲーム終了を決定する）
            self._passed = 0 # indicates if last player passed (for determing game over)
    def getPlayer(self):
        "Returns player whose turn it is"
        return self._player
    def getPieces(self):
        "Returns current pieces on board as dictionary: pieces[x,y] = player"
        return self._pieces
    def getMoves(self):
        '''Returns a list of valid next moves and board states.
           Each item is (x,y,newBoardState). x,y in range 0-7.
           If the only legal move is a pass, there will be one entry with x=y=None.
           If there is no legal move (game over), the list will be empty.
        '''
        result = []
        # 正しい動きのための空いている個所を検査する。        
        # examine open spaces for legal moves
        for x,y in self._open.keys():
            boardState = self._placePiece(x, y)
            if boardState: result.append((x,y,boardState))
        if not result:
            # 動ける場所が何も見つからなかったら、ゲーム終了
            # no moves found, game might be over
            if self._passed:
                # 最後のプレイヤーが既にパスした場合、ゲーム終了
                # last player already passed, indicate game over
                return ()
            # ボードステートをコピーして、通過するための状態をセットして、プレイヤーを交替させる
            # copy board state, set state to passed, and change players
            boardState = BoardState(self)
            boardState._passed = 1
            boardState._changePlayers()
            result.append((None, None, boardState))
        return result
        # 開かれたスペースリストからの新しい石を除く
        # remove new piece from open space list
        del newboard._open[x,y]
        # 部分を囲む新しい空地を加える
        # add new open spaces surrounding piece
    def _placePiece(self, x, y):
        #与えられた位置に1個置こうとする。正常な場合新しいBoardStateを返す。
        # Tries to place a piece at given location.  Returns new BoardState if legal.
        newboard = None
        player = self._player
        #石を弾くためにすべての方向をチェックする。
        # check every direction for pieces to flip
        for dx,dy in Compass:
            #(tx, ty)はテストする位置
            tx = x + dx; ty = y + dy # (tx, ty) is the testing location
            #この方向の弾ける石の数をカウントする
            # count number of flippable pieces in this direction
            flipcount = 0
            while 1:
                c = self._pieces.get((tx, ty))
                #空きsquareが見つかったら、探すのをやめる
                if c is None: flipcount = 0; break # found a blank square, stop looking
                #自分のもう1つの石が見つかったら、探すのをやめる
                if c == player: break # found another one of our pieces, stop looking
                flipcount = flipcount + 1
                #進歩テストポインタ
                tx = tx + dx; ty = ty + dy # advance test pointer
            if flipcount:
                #最後のテスト位置に向かって後ろに歩き、石を弾きます。
                # we found some pieces to flip, make a new board state
                if not newboard:
                    newboard = self._getNewBoard(x, y)
                    newboard._passed = 0
                for i in range(flipcount):
                    #最後のテスト位置に向かって後ろに歩き、石を弾きます。
                    # walk backwards for last test position and flip pieces
                    tx = tx - dx; ty = ty - dy
                    newboard._pieces[tx,ty] = player
        return newboard
    def _getNewBoard(self, x, y):
        #現在のものから新しいボードを建造し、部分と空地を更新します。
        #現在のボード状態をコピーする。
        # Builds a new board from current one and updates pieces and open spaces
        # copy current board state
        newboard = BoardState(self)
        #新しい石を追加する
        # add new piece
        newboard._pieces[x,y] = self._player
        # オープンスペース・リストから新しい部分を取り除く
        # remove new piece from open space list
        del newboard._open[x,y]
        # 部分を囲む新しい空地を加える        
        # add new open spaces surrounding piece
        for dx,dy in Compass:
            tx = x + dx; ty = y + dy
            if not newboard._pieces.get((tx, ty)):
                #スペースが空いていれば、それをオープンリストに加える（もし、それが端になければ!）
                # space is open, add it to open list (unless it's off the edge!)
                if tx >= 0 and tx <= 7 and ty >= 0 and ty <= 7:
                    newboard._open[tx, ty] = 1
        #別のプレーヤーの番にする
        # make it the other player's turn
        newboard._changePlayers()
        return newboard
    def _changePlayers(self):
        #別のプレイヤーの番に変える
        # Changes to the other player's turn
        if self._player == 1: self._player = 2
        else:                 self._player = 1


class Board:
    "Holds the Tk GUI and the current board state"
    class Square: # マスのクラス
        "一つマスに含むデータの定義(Holds data related to a square of the board)"
        def __init__(self, x, y): # 初期化　Squareのコンストラクタ
            self.x, self.y = x, y # location of square (in range 0-7) #盤の位置(0から7)
            self.player = 0 # number of player occupying square #プレイヤーの番号
            self.squareId = 0 # canvas id of rectangle
            self.pieceId = 0 # canvas id of circle

    def __init__(self, strategies=()): # 初期化 Boardのコンストラクタ 
        '''Initialize the interactive game board.  An optional list of
           computer opponent strategies can be supplied which will be
           displayed in a menu to the user.
        '''
        # create a Tk frame to hold the gui # Tkフレーム作成
        self._frame = Frame()
        # set the window title # 全体のウインドウタイトルを設定する
        self._frame.master.wm_title('オセロ(Reversi)')
        # build the board on a Tk drawing canvas # 図面キャンバスの作成
        size1 = 8*GridSize +20
        self._canvas = Canvas(self._frame, width=size1, height=size1)
        t = (0, 0, size1, size1)
        self._canvas.create_rectangle(t, fill=dark_grey)
        canvas_id = self._canvas.create_text(10, size1 - 18, anchor="nw",fill='#FFFFFF')
        self._canvas.itemconfig(canvas_id, text="   a       b        c         d         e         f         g        h")
        y1=1
        for y in range(37,size1,GridSize):
            self._canvas.create_text(size1- 12, y-12, anchor="nw",fill='#FFFFFF', text=str(y1))
            y1 += 1
        #old settings
        #size = 8*GridSize # make room for 8x8 squares
        #self._canvas = Canvas(self._frame, width=size, height=size)
        self._canvas.pack()
        # add button for starting game # ボタンを追加する
        self._menuFrame = Frame(self._frame)
        self._menuFrame.pack(expand=Y, fill=X)
        self._newGameButton = Button(self._menuFrame, text='最初から', command=self._newGame)
        self._newGameButton.pack(side=LEFT, padx=5)
        Label(self._menuFrame).pack(side=LEFT, expand=Y, fill=X)
        #プレイヤーの戦略を選ぶためのメニューを追加する
        # add menus for choosing player strategies
        self._strategies = {} # strategies, indexed by name
        optionMenuArgs = [self._menuFrame, 0, '人(ひと)']
        for s in strategies:
            name = s.getName()
            optionMenuArgs.append(name)
            self._strategies[name] = s
        #ダミーのエントリー、したがって、戦略インデックスはプレーヤー番号と一致
        self._strategyVars = [0] # dummy entry so strategy indexes match player numbers
        #各プレイヤーのためにメニューを作る
        # make an menu for each player
        for n in (1,2):
            label = Label(self._menuFrame, anchor=E, text='%s:' % PlayerNames[n])
            label.pack(side=LEFT, padx=10)
            var = StringVar(); var.set('人(ひと)')
            var.trace('w', self._strategyMenuCallback)
            self._strategyVars.append(var)
            optionMenuArgs[1] = var
            #menu = apply(OptionMenu, optionMenuArgs)
            print (optionMenuArgs)
            menu = OptionMenu(optionMenuArgs[0],optionMenuArgs[1],
                              optionMenuArgs[2],optionMenuArgs[3],
                              optionMenuArgs[4],optionMenuArgs[5],
                              optionMenuArgs[6])
            menu.pack(side=LEFT)
        # add a label for showing the status # ステータスを表示するためのラベルを追加する
        self._status = Label(self._frame, relief=SUNKEN, anchor=W)
        self._status.pack(expand=Y, fill=X)
        # map the frame in the main Tk window #Tkウインドウの中のフレーム
        self._frame.pack()

        # track the board state #ボード状態を追う
        self._squares = {} # Squares indexed by (x,y)
        #有効な動きのリスト
        self._enabledSpaces = () # list of valid moves as returned by BoardState.getmoves()
        for x in range(8):
            for y in range(8):
                square = self._squares[x,y] = Board.Square(x,y)
                x0 = x * GridSize + Offset
                y0 = y * GridSize + Offset
                square.squareId = self._canvas.create_rectangle(x0, y0,
                                                                x0+GridSize,
                                                                y0+GridSize,
                                                                fill=BoardColor)

        #「_afterId」は現在の'after'のprocを追うため、必要ならばキャンセルすることができる
        # _afterId tracks the current 'after' proc so it can be cancelled if needed
        self._afterId = 0

        # ready to go - start a new game! #ゲーム最初から！
        self._newGame()

    def play(self):
        'メインプログラムの呼び出しメソッド, Play the game! (this is the only public method)'
        self._frame.mainloop()

    def _postStatus(self, text):
        # updates the status line text #状態ラインテキストをアップデートする
        self._status['text'] = text

    def _strategyMenuCallback(self, *args):
        #プレーヤー戦略のうちの1つが変更される場合、これが呼ばれる
        #「_updateBoard」は同時にすべてを保つだろう
        # this is called when one of the player strategies is changed.
        # _updateBoard will keep everything in sync
        self._updateBoard()

    def _newGame(self):
        # 存在する石を削除する
        # delete existing pieces
        for s in self._squares.values():
            if s.pieceId:
                self._canvas.delete(s.pieceId)
                s.pieceId = 0
        # 新しいボード状態を作って表示する
        # create a new board state and display it
        self._state = BoardState()
        self._updateBoard()

    def _updateBoard(self):
        # 必要ならば'after' procをキャンセルする
        # cancel 'after' proc, if any
        if self._afterId:
            self._frame.after_cancel(self._afterId)
            self._afterId = 0
        # 可能にされたスペースをリセットする
        # reset any enabled spaces
        self._disableSpaces()
        # 現状と一致する最新版キャンバス・ディスプレイ
        # update canvas display to match current state
        for pos, player in self._state.getPieces().items():
            square = self._squares[pos]
            if square.pieceId:
                if square.player != player:
                    self._canvas.itemconfigure(square.pieceId,
                                               fill=PlayerColors[player])
            else:
                x,y = pos
                x0 = x * GridSize + Offset + 4
                y0 = y * GridSize + Offset + 4
                square.pieceId = self._canvas.create_oval(x0,
                                                          y0,
                                                          x0 + PieceSize, y0 + PieceSize,
                                                          fill=PlayerColors[player])
        # 次の動き(人間かaiのいずれか)の準備をする
        # prepare for next move, either human or ai
        player = self._state.getPlayer()
        moves = self._state.getMoves()
        # ゲーム終了のためのチェックをする
        # check for game over
        if not moves:
            self._gameOver()
            return
        # パスのためのチェックをする
        # check for a pass
        if len(moves) == 1 and moves[0][0] == None:
            # must pass - do it now # パスしなければいけない、今やる
            self._state = moves[0][2]
            moves = self._state.getMoves()
            if not moves:
                self._gameOver()
                return
            # パスしたというステータス・メッセージ
            # prepend status message with passed message
            passedText = PlayerNames[player] + ' パスです - '
            # update player
            player = self._state.getPlayer()
        else:
            # player can't pass # プレイヤーがパスできない場合は
            passedText = ''

        # get strategy (if not human) # 戦略を得る（人でない場合）
        ai = self._strategies.get(self._strategyVars[player].get())
        if ai:
            # ai: AIを実行する
            # ai: we have to schedule the ai to run
            self._postStatus(passedText + "%s (%s) をかんがえる" % \
                             (ai.getName(), PlayerNames[player]))
            self._afterId = self._frame.after_idle(self._processAi, ai, moves)
        else:
            # 人: ただ正しい動きを可能にして、クリックを待つ
            # human: just enable legal moves and wait for a click
            count = [0,0,0] # first entry is a dummy
            for _player in self._state.getPieces().values():
                count[_player] = count[_player] + 1
            self._postStatus(passedText + PlayerNames[player] + "の手番（てばん）,  %s: %d  -  %s: %d" % \
                             (PlayerNames[1], count[1], PlayerNames[2], count[2]))
            self._enabledSpaces = self._state.getMoves()
            self._enableSpaces()

    def _processAi(self, ai, moves):
        # 次の動きを決定するために戦略を呼ぶ
        # calls the strategy to determine next move
        if len(moves) == 1:
            # たった1つの選択肢、両方の呼び出しの戦略をしない
            # only one choice, don't both calling strategy
            self._state = moves[0][2]
        else:
            # call strategy # 戦略を呼ぶ
            x,y,boardstate = ai.getNextMove(self._state.getPlayer(), moves)
            self._state = boardstate
        self._afterId = self._frame.after(MoveDelay, self._updateBoard)

    def _enableSpaces(self):
        # make spaces active where a legal move is possible (only used for human players)
        for x,y,bs in self._enabledSpaces:
            if x == -1: break
            id = self._squares[x,y].squareId
            self._canvas.tag_bind(id, '<ButtonPress>',
                                  lambda e, s=self, x=x, y=y,
                                  bs=bs: s._selectSpace(bs))
            self._canvas.tag_bind(id, '<Enter>',
                                  lambda e, c=self._canvas, id=id: \
                                  c.itemconfigure(id, fill=HiliteColor))
            self._canvas.tag_bind(id, '<Leave>',
                                  lambda e, c=self._canvas, id=id: \
                                  c.itemconfigure(id, fill=BoardColor))

    def _disableSpaces(self):
        # すべての可能にされたスペース用イベント処理部を削除する
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
        # 人が石を置くスペースをクリックしたときに呼ばれる
        # this is called when a human clicks on a space to place a piece
        # 新しいボード状態はあらかじめ計算されました、それを単に使用する
        self._state = bs # the new board state was pre-computed, just use it
        self._updateBoard()

    def _gameOver(self):
        # ゲーム終了。石を総計して、勝利者を宣言する
        # the game is over.  Count up the pieces and declare the winner.
        count = [0,0,0] # first entry is a dummy #最初の要素はダミー
        for player in self._state.getPieces().values():
            count[player] = count[player] + 1
        self._postStatus('おわり,  %s: %d  -  %s: %d' % \
                         (PlayerNames[1], count[1], PlayerNames[2], count[2]))

class Strategy:
    # これは、戦略を実践するための基底クラスです。
    # This is a base class for implementing strategies
    def getName(self):
        "Returns the name of the strategy for displaying to the user."
        try:
            # return name if we have one # 戦略名を返す
            return self._name
        except AttributeError: # self._name定義されなかった場合
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

#
# 次のクラスはStrategyのクラスを継承している
#
class Random(Strategy): # 動きをランダムに取る
    def __init__(self):
        self._name='ランダム'
    def getNextMove(self, player, moves):
        # just pick a move randomly
        move = moves[random.randint(0, len(moves)-1)]
        return move

class InvGreedy(Strategy): # 動きを欲張る
    def __init__(self):
        self._name='逆欲張り'
    def getNextMove(self, player, moves):
        # check every move and pick the one with the least pieces belonging to player
        bestMove = None
        bestCount = minimum = 40
        for move in moves:
            x,y,bs = move
            pieces = bs.getPieces()
            count = 0
            for piece in pieces.values():
                if piece == player: count = count + 1
            if count < bestCount:
                bestCount = count
                bestMove = move
        return bestMove

class CornerFirst(Strategy):
    """ 隅（すみ）の場所を優先し、できればX(b2,g2,b7,f7)を打たない"""
    def __init__(self):
        self._name='隅(すみ)かランダム'
    def getNextMove(self, player, moves):
        # check every move and pick the one at the corner first otherwise random
        bestMove = None
        for move in moves:
            x,y,bs = move
            print ("x=",x,"y=",y)
            if (x==0 and y==0):
                bestMove = move
            elif (x==0 and y==7):
                bestMove = move
            elif (x==7 and y==0):
                bestMove = move
            elif (x==7 and y==7):
                bestMove = move
        if bestMove==None:
            # not b2,g2,b7,f7 (not X)
            trial =0
            while len(moves)>1 and trial <=10:
                bestMove = moves[random.randint(0, len(moves)-1)]
                x,y,bs=bestMove
                trial +=1
                test = (x==1 and y==1) or (x==1 and y==6)
                test = test or (x==6 and y==1) or (x==6 and y==1)
                if  test :
                    pass
                elif trial > 10:
                    break
                else:
                    break
            if len(moves)==1:
                bestMove = moves[0]
                
        return bestMove

class CornerFirstGreedy(Strategy):
    def __init__(self):
        self._name='隅か逆欲張り'
    def getNextMove(self, player, moves):
        # check every move and pick the one at the corner first otherwise random
        bestMove = None
        for move in moves:
            x,y,bs = move
            print ("x=",x,"y=",y)
            if (x==0 and y==0):
                bestMove = move
            elif (x==0 and y==7):
                bestMove = move
            elif (x==7 and y==0):
                bestMove = move
            elif (x==7 and y==7):
                bestMove = move
        if bestMove==None:
                    bestCount = 40
                    for move in moves:
                        x,y,bs = move
                        pieces = bs.getPieces()
                        count = 0
                        for piece in pieces.values():
                            if piece == player: count = count + 1
                        if count < bestCount:
                            bestCount = count
                            bestMove = move
        return bestMove

################# メインプログラム：boardボードのインスタスを作成 ####
if __name__ == '__main__':
    # create a new game board with the desired strategies
    # 戦略のリストstrategiesはBoardの引数
    strategies = (Random(),InvGreedy(),CornerFirst(),CornerFirstGreedy())
    board = Board(strategies)
    board.play() # 実際フレームの処理を開始する
