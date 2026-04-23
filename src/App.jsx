import { useState } from 'react';

function Square({value, onSquareClick, index, visualValidMoves}) {
  return (
    <button 
      className="square" onClick={onSquareClick} 
      style={{backgroundColor: visualValidMoves && visualValidMoves.includes(index) ? 'lightgreen' : 'white'}}
    >
      {value}
    </button>
  );
}

export default function Board() {
  const [xIsNext, setXIsNext] = useState(true);
  const [squares, setSquares] = useState(Array(9).fill(null));

  const [xCount, setXCount] = useState(0);
  const [oCount, setOCount] = useState(0);
  const [selectSquare, setSelectedSquare] = useState(null);
  const [visualValidMoves, setVisualValidMoves] = useState([]);

  function handleClick(i) {
    const placementDone = xCount === 3 && xCount === oCount;

    // Movement phase
    if (placementDone) {
      // Select a square
      if (xIsNext && squares[i] === 'X') {
        console.log('X selected at', i);
        setSelectedSquare(i);
        setVisualValidMoves(adjacentSquares(i));
        return;
      } else if (!xIsNext && squares[i] === 'O') {
        console.log('O selected at', i);
        setSelectedSquare(i);
        setVisualValidMoves(adjacentSquares(i));
        return;
      }

      // Select square to move piece to
      const validMoves = adjacentSquares(selectSquare);
      if (selectSquare !== null) {
        if (validMoves.includes(i)) {
          console.log('Moving piece from', selectSquare, 'to', i);
          const nextSquares = squares.slice();
          nextSquares[i] = xIsNext ? 'X' : 'O';

          nextSquares[selectSquare] = null;
          setSquares(nextSquares);
          setSelectedSquare(null);
          setVisualValidMoves([]); 
          setXIsNext(!xIsNext);
          return;
        } else {
          console.log('Invalid move');
          return;
        }
      }
      return;
    }

    // Placement phase
    if (calculateWinner(squares) || squares[i]) {
      return;
    }

    const nextSquares = squares.slice();

    if (xIsNext) {
      nextSquares[i] = 'X';
      setXCount(xCount + 1);
    } else {
      nextSquares[i] = 'O';
      setOCount(oCount + 1);
    }
    setSquares(nextSquares);
    setXIsNext(!xIsNext);
  }

  function adjacentSquares(i) {
    const adjacentSqaures = [
      [1, 3, 4],
      [0, 2, 3, 4, 5], 
      [1, 4, 5],
      [0, 1, 4, 6, 7],
      [0, 1, 2, 3, 5, 6, 7, 8],
      [1, 2, 4, 7, 8],
      [3, 4, 7],
      [3, 4, 5, 6, 8],
      [4, 5, 7]
    ];

    return adjacentSqaures[i].filter(index => squares[index] === null);
  }
  
  // Determine Winner Status
  const winner = calculateWinner(squares);
  let status;
  if (winner) {
    status = 'Winner: ' + winner;
  } else {
    status = 'Next player: ' + (xIsNext ? 'X' : 'O');
  }

  return (
    <>
      <div className="status">{status}</div>
      <div className="board-row">
        <Square 
          value={squares[0]} 
          onSquareClick={() => handleClick(0)} 
          visualValidMoves={visualValidMoves} 
          index={0}
        />
        <Square 
          value={squares[1]} 
          onSquareClick={() => handleClick(1)} 
          visualValidMoves={visualValidMoves} 
          index={1}
        />
        <Square 
          value={squares[2]} 
          onSquareClick={() => handleClick(2)} 
          visualValidMoves={visualValidMoves} 
          index={2}
        />
       </div>
      <div className="board-row">
        <Square 
          value={squares[3]} 
          onSquareClick={() => handleClick(3)} 
          visualValidMoves={visualValidMoves} 
          index={3}
        />
        <Square 
          value={squares[4]} 
          onSquareClick={() => handleClick(4)} 
          visualValidMoves={visualValidMoves} 
          index={4}
        />
        <Square 
          value={squares[5]} 
          onSquareClick={() => handleClick(5)} 
          visualValidMoves={visualValidMoves} 
          index={5}
        />
      </div>
      <div className="board-row">
        <Square 
          value={squares[6]} 
          onSquareClick={() => handleClick(6)} 
          visualValidMoves={visualValidMoves} 
          index={6}
        />
        <Square 
          value={squares[7]} 
          onSquareClick={() => handleClick(7)} 
          visualValidMoves={visualValidMoves} 
          index={7}
        />
        <Square 
          value={squares[8]} 
          onSquareClick={() => handleClick(8)} 
          visualValidMoves={visualValidMoves}  
          index={8}
        />
      </div>
    </>
  );
}

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}
