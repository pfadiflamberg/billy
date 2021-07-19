FROM node:16
WORKDIR /app
COPY package.json .
RUN yarn install
COPY . .
RUN yarn install
RUN yarn build
RUN yarn run build

FROM nginx:1.21
COPY nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /app
COPY --from=0 /app/build/ static/