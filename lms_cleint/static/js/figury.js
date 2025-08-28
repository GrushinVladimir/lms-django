
// Статические 3D фигуры в правом нижнем углу
document.addEventListener('DOMContentLoaded', function() {
    const bgContainer = document.querySelector('.w-bg');
    if (!bgContainer) return;
    
    // Создаем canvas поверх фонового изображения
    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = '-1';
    canvas.width = bgContainer.offsetWidth;
    canvas.height = bgContainer.offsetHeight;
    bgContainer.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    const colors = ['#4a8a7d', '#63b8a9', '#8fd1c4'];
    
    // Создаем 3D фигуры
    const shapes = [];
    const shapeCount = 9;
    
    // Параметры для расположения в правом нижнем углу
    const cornerPadding = 10; // Отступ от краев
    const clusterWidth = 800; // Ширина области кластера
    const clusterHeight = 300; // Высота области кластера
    const minDistance = 240; // Минимальное расстояние между фигурами
    
    // Инициализация фигур в правом нижнем углу
    for (let i = 0; i < shapeCount; i++) {
        let x, y;
        let attempts = 0;
        let validPosition = false;
        
        // Пытаемся найти позицию, которая не пересекается с другими фигурами
        while (!validPosition && attempts < 100) {
            // Позиционируем в правом нижнем углу
            x = canvas.width - cornerPadding - Math.random() * clusterWidth;
            y = canvas.height - cornerPadding - Math.random() * clusterHeight;
            
            // Проверяем расстояние до других фигур
            validPosition = true;
            for (let j = 0; j < shapes.length; j++) {
                const otherShape = shapes[j];
                const distance = Math.sqrt(Math.pow(x - otherShape.x, 2) + Math.pow(y - otherShape.y, 2));
                if (distance < minDistance) {
                    validPosition = false;
                    break;
                }
            }
            attempts++;
        }
        
        shapes.push({
            x: x,
            y: y,
            z: Math.random() * 100,
            size: 50 + Math.random() * 50,
            color: colors[Math.floor(Math.random() * colors.length)],
            rotationX: Math.random() * 360,
            rotationY: Math.random() * 360,
            rotationZ: Math.random() * 360,
            type: Math.floor(Math.random() * 4)
        });
    }
    
    // Рисуем фигуры один раз (без анимации)
    function renderShapes() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Сортируем фигуры по z-координате для правильного отображения
        shapes.sort((a, b) => b.z - a.z);
        
        shapes.forEach(shape => {
            // Рисуем 3D фигуру
            ctx.save();
            ctx.translate(shape.x, shape.y);
            
            // Перспектива
            const scale = 1 + shape.z / 200;
            ctx.scale(scale, scale);
            
            // Поворот
            ctx.rotate(shape.rotationX * Math.PI / 180);
            ctx.rotate(shape.rotationY * Math.PI / 180);
            ctx.rotate(shape.rotationZ * Math.PI / 180);
            
            ctx.fillStyle = shape.color;
            ctx.strokeStyle = '#76bdad';
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.3;
            
            switch(shape.type) {
                case 0: 
                    drawCube(ctx, shape.size);
                    break;
                case 1: 
                   drawCube(ctx, shape.size/2);
                    break;
                case 2:
                    drawPyramid(ctx, shape.size);
                    break;
                case 3: 
                    drawPyramid(ctx, shape.size/2);
                    break;
            }
            
            ctx.restore();
        });
    }
    
    // Полная реализация куба
    function drawCube(ctx, size) {
        const half = size / 2;
        
        // Передняя грань
        ctx.beginPath();
        ctx.moveTo(-half, -half);
        ctx.lineTo(half, -half);
        ctx.lineTo(half, half);
        ctx.lineTo(-half, half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Задняя грань
        ctx.beginPath();
        ctx.moveTo(-half, -half);
        ctx.lineTo(-half - half*0.3, -half - half*0.3);
        ctx.lineTo(half - half*0.3, -half - half*0.3);
        ctx.lineTo(half, -half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Верхняя грань
        ctx.beginPath();
        ctx.moveTo(-half, -half);
        ctx.lineTo(-half - half*0.3, -half - half*0.3);
        ctx.lineTo(-half - half*0.3, half - half*0.3);
        ctx.lineTo(-half, half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Правая боковая грань
        ctx.beginPath();
        ctx.moveTo(half, -half);
        ctx.lineTo(half - half*0.3, -half - half*0.3);
        ctx.lineTo(half - half*0.3, half - half*0.3);
        ctx.lineTo(half, half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Нижняя грань
        ctx.beginPath();
        ctx.moveTo(-half, half);
        ctx.lineTo(-half - half*0.3, half - half*0.3);
        ctx.lineTo(half - half*0.3, half - half*0.3);
        ctx.lineTo(half, half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Левая боковая грань
        ctx.beginPath();
        ctx.moveTo(-half, -half);
        ctx.lineTo(half, -half);
        ctx.lineTo(half - half*0.3, -half - half*0.3);
        ctx.lineTo(-half - half*0.3, -half - half*0.3);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }
    
    function drawPyramid(ctx, size) {
        const half = size / 2;
        
        // Основание
        ctx.beginPath();
        ctx.moveTo(-half, half);
        ctx.lineTo(half, half);
        ctx.lineTo(0, -half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Боковые грани
        ctx.beginPath();
        ctx.moveTo(-half, half);
        ctx.lineTo(0, 0);
        ctx.lineTo(0, -half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(half, half);
        ctx.lineTo(0, 0);
        ctx.lineTo(0, -half);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }

    // Рисуем фигуры один раз
    renderShapes();
    
    // Респонсив - обновляем размер canvas при изменении размера окна
    window.addEventListener('resize', function() {
        canvas.width = bgContainer.offsetWidth;
        canvas.height = bgContainer.offsetHeight;
        
        // Перерисовываем фигуры с новыми размерами
        renderShapes();
    });
});