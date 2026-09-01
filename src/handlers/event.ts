import { Client } from 'discord.js';
import loadCommands from '../events/clientReady/loadCommands';
import status from '../events/clientReady/status';
import AutoComplete from '../events/interactionCreate/AutoComplete';
import Command from '../events/interactionCreate/Command';
import messageCreate from '../events/messageCreate/index';

export default async (client: Client) => {
  const events = [
    { event: 'clientReady', handler: loadCommands },
    { event: 'clientReady', handler: status },
    { event: 'interactionCreate', handler: AutoComplete },
    { event: 'interactionCreate', handler: Command },
    { event: 'messageCreate', handler: messageCreate },
  ];

  for (const { event, handler } of events) {
    client.on(event, (handler as (...args: any[]) => any).bind(null, client));
  }

  logger.info(`${events.length} event listeners loaded`);
};
