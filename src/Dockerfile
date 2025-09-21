# Використання офіційного образу Python
FROM python:3.9-slim

# Встановлення робочої директорії всередині контейнера
WORKDIR /app

# Копіювання файлів залежностей та встановлення їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання всіх файлів проєкту в контейнер
COPY . .

# Відкриття порту 3000
EXPOSE 3000

# Команда для запуску програми
CMD ["python", "app.py"]