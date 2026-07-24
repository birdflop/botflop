import { Client } from 'discord.js';

export default (client: Client) => {
  client.login(process.env.BOT_TOKEN);
  logger.info('Bot logged in');
};
