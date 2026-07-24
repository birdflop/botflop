import { Client } from 'discord.js';
export default (client: Client) => {
  // Log any REST errors (mostly for debugging, since these don't necessarily need to be reported)
  client.rest.on('rateLimited', (info) =>
    logger.warn(`Encountered ${info.method} rate limit!`)
  );

  // Log unhandled promise rejections, but if it's an unknown message/interaction or missing permissions/access error, log the request body instead of the error (since those errors are usually caused by users and the request body can help us debug it faster)
  process.on('unhandledRejection', (reason: any) => {
    console.error(reason);
    if (
      reason.rawError &&
      (reason.rawError.message == 'Unknown Message' ||
        reason.rawError.message == 'Unknown Interaction' ||
        reason.rawError.message == 'Missing Access' ||
        reason.rawError.message == 'Missing Permissions')
    ) {
      logger.error(JSON.stringify(reason.requestBody));
    }
  });

  // Register events for disconnect, reconnect, warn, and error
  client.on('disconnect', () => {
    logger.info('Bot is disconnecting...');
  });
  client.on('reconnecting', () => {
    logger.info('Bot reconnecting...');
  });
  client.on('warn', (error) => {
    logger.warn(error);
  });
  client.on('error', (error) => {
    logger.error(error);
  });

  logger.info('Error Handler Loaded');
};
