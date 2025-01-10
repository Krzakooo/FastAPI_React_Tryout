FROM node:16

WORKDIR /app/frontend

COPY frontend/package.json /app/frontend/
COPY frontend/package-lock.json /app/frontend/

RUN npm install

COPY frontend/ /app/frontend/

EXPOSE 3000

CMD ["npm", "start"]
