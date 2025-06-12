import React, { useRef, useEffect, useState } from 'react';
import './TableSelector.css';

const TableSelector = ({ hallType = 'test' }) => {
  const canvasRef = useRef(null);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);

  const testTables = [
    { id: 1, x: 18 * 40, y: 11 * 40, status: 'free' },
    { id: 2, x: 17 * 40, y: 11 * 40, status: 'occupied' },
    { id: 3, x: 16 * 40, y: 11 * 40, status: 'free' },
    { id: 4, x: 15 * 40, y: 11 * 40, status: 'free' },
    { id: 5, x: 14 * 40, y: 11 * 40, status: 'occupied' },
    { id: 6, x: 13 * 40, y: 11 * 40, status: 'free' },
    { id: 7, x: 12 * 40, y: 11 * 40, status: 'free' },
    { id: 8, x: 11 * 40, y: 10 * 40, status: 'occupied' },
    { id: 9, x: 10 * 40, y: 10 * 40, status: 'free' },
    { id: 10, x: 6 * 40, y: 11 * 40, status: 'free' },
    { id: 11, x: 5 * 40, y: 11 * 40, status: 'free' },
    { id: 12, x: 6 * 40, y: 9 * 40, status: 'occupied' },
    { id: 13, x: 8 * 40, y: 8 * 40, status: 'free' },
    { id: 14, x: 10 * 40, y: 8 * 40, status: 'free' },
    { id: 15, x: 11 * 40, y: 5 * 40, status: 'occupied' },
    { id: 16, x: 10 * 40, y: 7 * 40, status: 'free' },
    { id: 17, x: 11 * 40, y: 7 * 40, status: 'free' },
    { id: 18, x: 14 * 40, y: 8 * 40, status: 'occupied' },
    { id: 19, x: 15 * 40, y: 3 * 40, status: 'free' },
    { id: 20, x: 14 * 40, y: 3 * 40, status: 'free' },
    { id: 21, x: 13 * 40, y: 3 * 40, status: 'occupied' },
    { id: 22, x: 12 * 40, y: 3 * 40, status: 'free' },
    { id: 23, x: 4 * 40, y: 8 * 40, status: 'free' },
    { id: 24, x: 5 * 40, y: 8 * 40, status: 'occupied' },
    { id: 25, x: 5 * 40, y: 7 * 40, status: 'free' },
    { id: 26, x: 9 * 40, y: 10 * 40, status: 'free' },
    { id: 27, x: 8 * 40, y: 10 * 40, status: 'occupied' },
  ];

  useEffect(() => {
    if (hallType === 'test') {
      setTables(testTables);
    } else {
      fetch('/api/tables')
        .then(response => response.json())
        .then(data => {
          const formattedTables = data.map(table => ({
            id: table.id,
            x: table.x * 40,
            y: table.y * 40,
            status: table.status,
          }));
          setTables(formattedTables);
        })
        .catch(error => console.error('Error loading tables:', error));
    }
  }, [hallType]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const drawMap = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#333';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Отрисовка сетки
      ctx.strokeStyle = '#555';
      ctx.lineWidth = 1;
      for (let x = 0; x <= canvas.width; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y <= canvas.height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Отрисовка стен (примерно как на картинке)
      ctx.fillStyle = '#666';
      ctx.fillRect(40, 0, 40, 80); // Левый верхний блок
      ctx.fillRect(80, 0, 40, 40); // Лестница
      ctx.fillRect(560, 0, 40, 200); // Правый вертикальный блок
      ctx.fillRect(600, 200, 200, 40); // Правый горизонтальный блок
      ctx.fillRect(400, 480, 80, 40); // Нижний центральный блок

      tables.forEach(table => {
        const gradient = ctx.createRadialGradient(
          table.x + 20, table.y + 20, 0,
          table.x + 20, table.y + 20, 20
        );
        if (table.status === 'free') {
          gradient.addColorStop(0, '#00ff00');
          gradient.addColorStop(1, '#008000');
        } else if (selectedTable && selectedTable.id === table.id) {
          gradient.addColorStop(0, '#ffff00');
          gradient.addColorStop(1, '#cc9900');
        } else {
          gradient.addColorStop(0, '#ff0000');
          gradient.addColorStop(1, '#800000');
        }
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(table.x + 20, table.y + 20, 20, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#fff';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(table.id, table.x + 20, table.y + 20);
      });

      ctx.fillStyle = '#fff';
      ctx.font = '16px Arial';
      ctx.fillText('Схема зала кафе "Артлин"', canvas.width / 2, canvas.height - 20);
    };

    const isPointInTable = (x, y, table) => {
      const dist = Math.sqrt((x - (table.x + 20)) ** 2 + (y - (table.y + 20)) ** 2);
      return dist <= 20;
    };

    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const clickedTable = tables.find(table => isPointInTable(x, y, table));
      if (clickedTable) {
        if (clickedTable.status === 'occupied') {
          alert(`Table ${clickedTable.id} is already occupied!`);
          return;
        }
        setSelectedTable(clickedTable);
        drawMap();
        fetch('/api/reserve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tableId: clickedTable.id }),
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              setTables(tables.map(t => t.id === clickedTable.id ? { ...t, status: 'occupied' } : t));
              setSelectedTable(null);
              alert(`Table ${clickedTable.id} reserved!`);
            } else {
              alert(data.message);
            }
          })
          .catch(error => console.error('Error:', error));
      }
    });

    drawMap();
  }, [tables]);

  return (
    <div className="table-selector">
      <canvas ref={canvasRef} width={800} height={600} />
    </div>
  );
};

export default TableSelector;