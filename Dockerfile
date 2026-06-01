## build runner
FROM node:lts-alpine AS build-runner

WORKDIR /tmp/app

COPY package.json ./

RUN npm install

COPY src ./src
COPY tsconfig.json .

RUN npm run build

## production runner
FROM node:lts-alpine AS prod-runner

WORKDIR /app

COPY --from=build-runner /tmp/app/package.json ./package.json

RUN npm install --omit=dev

COPY --from=build-runner /tmp/app/build ./build
COPY allowlist.txt ./allowlist.txt

CMD ["node", "build/main.js"]
