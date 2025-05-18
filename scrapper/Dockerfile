FROM openjdk:23-jdk-slim
WORKDIR /app
COPY target/scrapper.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
