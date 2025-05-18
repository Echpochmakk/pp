FROM openjdk:23-jdk-slim  # Используем легковесный образ Java
WORKDIR /app              # Рабочая папка внутри контейнера
COPY target/bot.jar app.jar  # Копируем наш jar-файл
EXPOSE 8080               # Открываем порт для бота
ENTRYPOINT ["java", "-jar", "app.jar"]  # Команда запуска
