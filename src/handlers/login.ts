import { Client } from 'discord.js';

export default (client: Client) => {
  client.login(process.env.TOKEN);
  logger.info('Bot logged in');
};
