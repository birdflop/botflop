import { createLogger, format, Logger, transports } from 'winston';
import type {
  Message,
  CommandInteraction,
  ModalSubmitInteraction,
  ButtonInteraction,
  StringSelectMenuInteraction,
  InteractionResponse,
} from 'discord.js';

// Set the global types
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

export const logger: Logger = createLogger({
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

global.logger = logger;
logger.info('Logger started');
