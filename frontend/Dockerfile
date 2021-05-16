FROM node:16

WORKDIR /usr/src/app

COPY package.json .
RUN yarn install

COPY . .
RUN yarn install
RUN yarn build

# run yarn test?

EXPOSE 8080
CMD [ "yarn", "start" ]