import { MochiClient } from '@mochi-analytics/core';
import { attachMochi } from '@mochi-analytics/discordjs';
import { Client } from 'discord.js';

export function setupMochi(client: Client) {
  const url = process.env.MOCHI_URL;
  const apiKey = process.env.MOCHI_API_KEY;

  if (!url && !apiKey) return;
  if (!url || !apiKey) {
    logger.warn(
      'Mochi analytics disabled: set both MOCHI_URL and MOCHI_API_KEY'
    );
    return;
  }

  const mochi = new MochiClient({
    url,
    apiKey,
    onError: (err) => logger.warn(`Mochi analytics error: ${err.message}`),
  });
  const detachMochi = attachMochi(client, mochi);
  let shuttingDown = false;

  const shutdown = async () => {
    if (shuttingDown) return;
    shuttingDown = true;
    detachMochi();
    await mochi.shutdown();
  };

  process.once('SIGINT', () => void shutdown().finally(() => process.exit(0)));
  process.once('SIGTERM', () => void shutdown().finally(() => process.exit(0)));
  process.once('beforeExit', () => void shutdown());
  logger.info('Mochi analytics enabled');
}
