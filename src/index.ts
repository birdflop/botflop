import { readdirSync } from 'fs';
import {
  Client,
  Partials,
  GatewayIntentBits,
  Message,
  CommandInteraction,
  ModalSubmitInteraction,
  ButtonInteraction,
  StringSelectMenuInteraction,
  InteractionResponse,
} from 'discord.js';
import { createLogger, format, Logger, transports } from 'winston';
import { errorFunc } from './util/misc/error';
import { setupMochi } from './util/analytics/mochi';
import dotenv from 'dotenv';
import path from 'path';
dotenv.config();

// Create Discord client
const client = new Client({
  shards: 'auto',
  partials: [Partials.Message, Partials.Channel, Partials.User],
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.DirectMessages,
  ],
});

// Set the global vars
declare global {
  var logger: Logger;
  var error: {
    (
      err: unknown,
      message:
        | Message
        | CommandInteraction
        | ModalSubmitInteraction
        | ButtonInteraction
        | StringSelectMenuInteraction,
      userError?: boolean
    ): Promise<Message | InteractionResponse | undefined>;
  };
}

export const lastStarted = new Date();
function minTwoDigits(n: number) {
  return (n < 10 ? '0' : '') + n;
}
export const logDate = `${minTwoDigits(lastStarted.getMonth() + 1)}-${minTwoDigits(lastStarted.getDate())}-${lastStarted.getFullYear()}`;
export const srcDir = path.resolve(import.meta.dirname);

// Create a logger
global.logger = createLogger({
  format: format.combine(
    format.errors({ stack: true }),
    format.colorize(),
    format.timestamp(),
    format.printf(
      (log) =>
        `[${new Date(log.timestamp as string | number | Date).toLocaleString('default', { hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true })} ${log.level}]: ${log.message}${log.stack ? `\n${log.stack}` : ''}`
    )
  ),
  transports: [
    new transports.Console(),
    new transports.File({ filename: `logs/${logDate}.log` }),
  ],
  rejectionHandlers: [
    new transports.Console(),
    new transports.File({ filename: `logs/${logDate}.log` }),
  ],
});
logger.info('Logger started');

global.error = errorFunc;
setupMochi(client);

// Load the universal and discord-specific handlers
const handlers = readdirSync(`${srcDir}/handlers`).filter((file: string) =>
  file.endsWith('.ts')
);
await Promise.all(
  handlers.map(async (handlerName) => {
    const handlerModule = await import(`./handlers/${handlerName}`);
    handlerModule.default(client);
  })
);
