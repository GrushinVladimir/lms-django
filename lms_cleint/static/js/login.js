 // Функция для проверки загрузки всех скриптов что бы закерыть лодер
function scriptsLoaded() {
    return new Promise((resolve) => {
        if (document.readyState === 'complete') {
            resolve();
        } else {
            window.addEventListener('load', resolve);
        }
    });
}

function imagesLoaded() {
            const images = document.querySelectorAll('img');
            let loadedCount = 0;
            
            return new Promise((resolve) => {
                if (images.length === 0) {
                    resolve();
                    return;
                }
                
                images.forEach(img => {
                    if (img.complete) {
                        loadedCount++;
                    } else {
                        img.addEventListener('load', () => {
                            loadedCount++;
                            if (loadedCount === images.length) resolve();
                        });
                        img.addEventListener('error', () => {
                            loadedCount++;
                            if (loadedCount === images.length) resolve();
                        });
                    }
                });
                
                if (loadedCount === images.length) resolve();
            });
        }
        // Ждем загрузки всех ресурсов
        Promise.all([
            imagesLoaded(),
            scriptsLoaded(),
            new Promise(resolve => setTimeout(resolve, 10)) // Минимальное время показа лоадера
        ]).then(() => {
            // Плавно скрываем лоадер
            const preloader = document.querySelector('.preloader');
            preloader.classList.add('hidden');
            
            // Удаляем лоадер из DOM после завершения анимации
            setTimeout(() => {
                preloader.remove();
            }, 500);
        });

        // Остальные скрипты (Select2, togglePasswordVisibility, 3D анимация)
        $(document).ready(function() {
            $('.select-multiple').select2({
                placeholder: "Выберите варианты",
                allowClear: true,
                width: '100%'
            });
            
            $('.teacher-info').each(function() {
                const teacherId = $(this).data('teacher-id');
                if (teacherId) {}
            });
        });
//Функция для смены иконки показать пароль
function togglePasswordVisibility(button) {
    // Находим ближайший контейнер с паролем
    const container = button.closest('.password-input-container');
    // Находим поле ввода внутри контейнера
    const passwordField = container.querySelector('input');
    const eyeIcon = button.querySelector('.eye-icon');
    
    if (!passwordField) {
        console.error('Password field not found');
        return;
    }
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        eyeIcon.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
        `;
    } else {
        passwordField.type = 'password';
        eyeIcon.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        `;
    }
}
        // Инициализация Select2 для всех элементов с классом select-multiple
        $(document).ready(function() {
            $('.select-multiple').select2({
                placeholder: "Выберите варианты",
                allowClear: true,
                width: '100%'
            });
            
            // Добавляем title для элементов с информацией о преподавателе
            $('.teacher-info').each(function() {
                const teacherId = $(this).data('teacher-id');
                if (teacherId) {
                    // Здесь можно добавить AJAX-запрос для получения полной информации,
                    // или передать данные через data-атрибуты
                }
            });
        });




    // 3D анимация фигур
    document.addEventListener('DOMContentLoaded', function() {
        const bgContainer = document.querySelector('.w-bg');
        if (!bgContainer) return;
        
        // Создаем canvas поверх фонового изображения
        const canvas = document.createElement('canvas');
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.zIndex = '1';
        canvas.width = bgContainer.offsetWidth;
        canvas.height = bgContainer.offsetHeight;
        bgContainer.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const colors = ['#4a8a7d', '#63b8a9', '#8fd1c4'];
        
        // Создаем 3D фигуры
        const shapes = [];
        const shapeCount = 15;
        
        // Инициализация фигур в видимой области
        for (let i = 0; i < shapeCount; i++) {
            shapes.push({
                x: Math.random() * (canvas.width - 100) + 50, // Оставляем отступ от краев
                y: Math.random() * (canvas.height - 100) + 50,
                z: Math.random() * 100,
                size: 30 + Math.random() * 50, // Увеличиваем минимальный размер
                speedX: -0.5 + Math.random(),
                speedY: -0.5 + Math.random(),
                speedZ: -0.05 + Math.random() * 0.1, // Замедляем движение по Z
                color: colors[Math.floor(Math.random() * colors.length)],
                rotationX: Math.random() * 360,
                rotationY: Math.random() * 360,
                rotationZ: Math.random() * 360,
                rotationSpeedX: -0.3 + Math.random() * 0.6,
                rotationSpeedY: -0.3 + Math.random() * 0.6,
                rotationSpeedZ: -0.3 + Math.random() * 0.6,
                type: Math.floor(Math.random() * 4)
            });
        }
        
        // Анимация
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Сортируем фигуры по z-координате для правильного отображения
            shapes.sort((a, b) => b.z - a.z);
            
            shapes.forEach(shape => {
                // Обновляем позицию
                shape.x += shape.speedX;
                shape.y += shape.speedY;
                shape.z += shape.speedZ;
                shape.rotationX += shape.rotationSpeedX;
                shape.rotationY += shape.rotationSpeedY;
                shape.rotationZ += shape.rotationSpeedZ;
                
                // Проверяем границы с учетом перспективы
                const perspective = 1 + shape.z / 200;
                const scaledSize = shape.size * perspective;
                
                if (shape.x < -scaledSize) shape.x = canvas.width + scaledSize;
                if (shape.x > canvas.width + scaledSize) shape.x = -scaledSize;
                if (shape.y < -scaledSize) shape.y = canvas.height + scaledSize;
                if (shape.y > canvas.height + scaledSize) shape.y = -scaledSize;
if (shape.z < -50) shape.speedZ = Math.abs(shape.speedZ);
if (shape.z > 50) shape.speedZ = -Math.abs(shape.speedZ);
                
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
            
            requestAnimationFrame(animate);
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
        
        function drawSphere(ctx, radius) {
            const gradient = ctx.createRadialGradient(0, 0, radius*0.3, 0, 0, radius);
            gradient.addColorStop(0, ctx.fillStyle);
            gradient.addColorStop(1, shadeColor(ctx.fillStyle, -30));
            
            ctx.beginPath();
            ctx.arc(0, 0, radius, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
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
        
        function drawTorus(ctx, radius, tubeRadius) {
            ctx.beginPath();
            for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
                const x = (radius + tubeRadius * Math.cos(angle)) * Math.cos(angle*2);
                const y = (radius + tubeRadius * Math.cos(angle)) * Math.sin(angle*2);
                if (angle === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        }
        
        function shadeColor(color, percent) {
            let R = parseInt(color.substring(1,3), 16);
            let G = parseInt(color.substring(3,5), 16);
            let B = parseInt(color.substring(5,7), 16);

            R = parseInt(R * (100 + percent) / 100);
            G = parseInt(G * (100 + percent) / 100);
            B = parseInt(B * (100 + percent) / 100);

            R = (R<255)?R:255;  
            G = (G<255)?G:255;  
            B = (B<255)?B:255;  

            R = Math.round(R);
            G = Math.round(G);
            B = Math.round(B);

            const RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
            const GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
            const BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

            return "#"+RR+GG+BB;
        }

        // Запускаем анимацию
        animate();
        
        // Респонсив - обновляем размер canvas при изменении размера окна
        window.addEventListener('resize', function() {
            canvas.width = bgContainer.offsetWidth;
            canvas.height = bgContainer.offsetHeight;
            
            // Перемещаем фигуры, чтобы они оставались в видимой области
            shapes.forEach(shape => {
                shape.x = Math.max(shape.size, Math.min(canvas.width - shape.size, shape.x));
                shape.y = Math.max(shape.size, Math.min(canvas.height - shape.size, shape.y));
            });
        });
    });